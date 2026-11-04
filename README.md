# Memgraph offline

Linux/amd64 Docker images for an air-gapped machine. This repo holds the images in Git LFS so they can be cloned from a public GitHub URL without a Docker Hub login.

Images packed from Docker Hub `latest` on 2026-11-04:

| Archive | Image loaded by `docker load` | Platform manifest |
| --- | --- | --- |
| `images/memgraph-mage-linux-amd64.tar` (709 MB) | `memgraph/memgraph-mage:latest` | `sha256:48fe84376e45559864249a9435854e3ad4255e5e856519ee07ab916ae69bc3f4` |
| `images/memgraph-lab-linux-amd64.tar` (86 MB) | `memgraph/lab:latest` | `sha256:e234386e8ff8864b4b3b8884e7f4e5d2587e5e7231bde9ce4adf42575e61db8a` |

These archives are **linux/amd64** only. They are the images to use on a typical x86_64 Linux server. `docker load` expands Memgraph MAGE to about 3.3 GB, so the isolated machine needs several gigabytes free.

## Download on the isolated machine

Git and Git LFS, no GitHub login (public repo):

```bash
git lfs install
git clone https://github.com/kiranbeethoju/memgraph-offline.git
cd memgraph-offline
sha256sum -c SHA256SUMS
```

If `git lfs` is missing, the clone only contains small pointer files. Install Git LFS and run `git lfs pull` in the repo.

The two archives are 834 MB together. GitHub Free includes 1 GB of Git LFS storage and 1 GB of LFS bandwidth per month, so one clone or one pair of direct downloads uses most of that monthly bandwidth. A later download in the same month can be rejected until the quota resets or a [Git LFS data pack](https://docs.github.com/en/billing/managing-billing-for-git-large-file-storage/about-billing-for-git-large-file-storage) is added.

Direct file download (also public, no login):

```bash
curl -L -o memgraph-mage-linux-amd64.tar \
  https://github.com/kiranbeethoju/memgraph-offline/raw/refs/heads/main/images/memgraph-mage-linux-amd64.tar
curl -L -o memgraph-lab-linux-amd64.tar \
  https://github.com/kiranbeethoju/memgraph-offline/raw/refs/heads/main/images/memgraph-lab-linux-amd64.tar
```

## Load and start

From the repository root:

```bash
chmod +x load-and-start.sh
./load-and-start.sh
```

That runs `docker load` for both archives, then `docker compose up -d`.

Manual equivalent:

```bash
docker load -i images/memgraph-mage-linux-amd64.tar
docker load -i images/memgraph-lab-linux-amd64.tar
docker compose up -d
```

Database only, without the web UI:

```bash
docker load -i images/memgraph-mage-linux-amd64.tar
docker volume create mg_lib
docker run -d \
  --name memgraph-mage \
  --restart unless-stopped \
  -p 7687:7687 \
  -p 7444:7444 \
  -v mg_lib:/var/lib/memgraph \
  memgraph/memgraph-mage:latest
```

## Connect

Memgraph Lab: [http://localhost:3000](http://localhost:3000)

In Lab, connect to `bolt://memgraph:7687` when Lab is started from this Compose file (the hostname is the Compose service name). From a client on the host, use `bolt://localhost:7687`. No credentials are required.

Shell inside the database container:

```bash
docker exec -it memgraph-mage mgconsole
```

Quick check:

```cypher
CREATE (a:User {name: "Alice"})-[:KNOWS]->(b:User {name: "Bob"});
MATCH (u:User)-[r:KNOWS]->(f) RETURN u.name, f.name;
```

Logs:

```bash
docker logs -f memgraph-mage
```

Stop:

```bash
docker compose down
```

Data stays in the `mg_lib` volume. `docker compose down -v` deletes that volume.

## Ports

| Port | Use |
| --- | --- |
| 7687 | Bolt (Cypher drivers and `mgconsole`) |
| 7444 | WebSocket / log streaming |
| 3000 | Memgraph Lab web UI |
