# Memgraph offline

Linux/amd64 Docker images for Memgraph (with MAGE graph algorithms) and Memgraph Lab. The images are stored with Git LFS so an isolated machine can download them from this public repo without a Docker Hub login.

## Installation

Install Docker, Git, and Git LFS on the Linux machine, then clone and start the containers.

```bash
git lfs install
git clone https://github.com/kiranbeethoju/memgraph-offline.git
cd memgraph-offline
sha256sum -c SHA256SUMS
chmod +x load-and-start.sh
./load-and-start.sh
```

`load-and-start.sh` loads both image archives and runs `docker compose up -d`.

Check that both containers are running:

```bash
docker ps
```

You should see `memgraph-mage` and `memgraph-lab`.

If `git lfs` is missing, the clone only contains small pointer files. Install Git LFS and run `git lfs pull` in the repo.

Manual start, after the archives are already on disk:

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

These archives are linux/amd64. `docker load` expands Memgraph MAGE to about 3.3 GB, so the machine needs several gigabytes free.

Stop the services with `docker compose down`. Data stays in the `mg_lib` volume. `docker compose down -v` deletes that volume.

Logs:

```bash
docker logs -f memgraph-mage
```

### Direct download

The files are also available without cloning. No GitHub login is required.

```bash
curl -L -o memgraph-mage-linux-amd64.tar \
  https://github.com/kiranbeethoju/memgraph-offline/raw/refs/heads/main/images/memgraph-mage-linux-amd64.tar
curl -L -o memgraph-lab-linux-amd64.tar \
  https://github.com/kiranbeethoju/memgraph-offline/raw/refs/heads/main/images/memgraph-lab-linux-amd64.tar
```

The two archives are 834 MB together. GitHub Free includes 1 GB of Git LFS storage and 1 GB of LFS bandwidth per month, so one clone or one pair of direct downloads uses most of that monthly bandwidth. A later download in the same month can be rejected until the quota resets or a [Git LFS data pack](https://docs.github.com/en/billing/managing-billing-for-git-large-file-storage/about-billing-for-git-large-file-storage) is added.

## Accessing Memgraph

No username or password is set. From this machine use `bolt://localhost:7687`. From another machine on the network, use `bolt://<server-ip>:7687`.

| Port | Use |
| --- | --- |
| 7687 | Bolt (Cypher drivers, `mgconsole`, and the Python starter) |
| 7444 | WebSocket / log streaming |
| 3000 | Memgraph Lab web UI |

### Memgraph Lab

Memgraph Lab is its own container. The browser only loads the UI from port 3000. The Lab process then opens Bolt itself. With the default image settings that connection goes to `127.0.0.1` **inside the Lab container**, so a Memgraph node that is healthy on the Linux host still looks unreachable.

Run Lab on the host network. It then uses the same addresses as the Linux machine, and it does not need internet or any extra packages. The image already contains the UI and the Bolt client. Recreate the container you already have:

```bash
docker rm -f memgraph-lab
docker run -d \
  --name memgraph-lab \
  --restart unless-stopped \
  --network host \
  -e QUICK_CONNECT_MG_HOST=127.0.0.1 \
  -e QUICK_CONNECT_MG_PORT=7687 \
  -e QUICK_CONNECT_MG_IS_ENCRYPTED=false \
  -e LOGIN_RESERVED_HOSTNAME_IS_ENABLED=true \
  memgraph/lab:latest
```

Or, from this repo, `docker compose up -d --force-recreate`. The Compose file uses the same host network and environment.

Open [http://localhost:3000](http://localhost:3000) on that Linux machine, or `http://<linux-ip>:3000` from another computer. Click **Connect**. Use these values:

| Field | Local Memgraph on this machine | Another Memgraph node |
| --- | --- | --- |
| Host | `127.0.0.1` | That node's IP or DNS name, the same one a Bolt client on this Linux host uses |
| Port | `7687` | `7687` |
| Logs port | `7444` | `7444` on that node, if it is open |
| Encrypted | off | off |
| Username / password | empty | empty, unless that node has auth |

Do not enter `localhost` for a node on another machine. Do not enter the Docker service name `memgraph` unless Lab and that database share a Docker network. `127.0.0.1` is the Linux host, which is correct for the container started with `-p 7687:7687`.

### mgconsole

```bash
docker exec -it memgraph-mage mgconsole
```

```cypher
CREATE (a:User {name: "Alice"})-[:KNOWS]->(b:User {name: "Bob"});
MATCH (u:User)-[r:KNOWS]->(f) RETURN u.name, f.name;
```

### Python

The starter in `python/quickstart.py` connects with the [Neo4j Python driver](https://neo4j.com/docs/python-manual/current/), which speaks Bolt. It creates two `User` nodes, reads the `KNOWS` relationship, and runs MAGE PageRank.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python python/quickstart.py
```

Expected output:

```text
Connected to bolt://localhost:7687
Friendships:
  Alice KNOWS Bob
PageRank:
  Bob: ...
  Alice: ...
```

Point the script at another host without editing it:

```bash
MEMGRAPH_URI=bolt://192.168.1.20:7687 python python/quickstart.py
```

`pip install` needs network access or a local copy of the `neo4j` package. The database images in this repo do not include that Python package.

## Images

Packed from Docker Hub `latest` on 2026-11-04.

| Archive | Image loaded by `docker load` | Platform manifest |
| --- | --- | --- |
| `images/memgraph-mage-linux-amd64.tar` (709 MB) | `memgraph/memgraph-mage:latest` | `sha256:48fe84376e45559864249a9435854e3ad4255e5e856519ee07ab916ae69bc3f4` |
| `images/memgraph-lab-linux-amd64.tar` (86 MB) | `memgraph/lab:latest` | `sha256:e234386e8ff8864b4b3b8884e7f4e5d2587e5e7231bde9ce4adf42575e61db8a` |
