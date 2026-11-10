# Dgraph offline

Linux/amd64 Docker images for Dgraph and Ratel, the web UI. Both images are in one Git LFS archive so an isolated machine can load them without Docker Hub.

The bundle is Dgraph v25.5.1 (Zero and Alpha) and Ratel v25.3.0. `docker load` creates these tags:

- `dgraph/dgraph:v25.5.1`
- `dgraph/ratel:v25.3.0`

## Installation

Install Docker, Git, and Git LFS on the Linux machine, then clone and start the stack.

```bash
git lfs install
git clone https://github.com/kiranbeethoju/memgraph-offline.git
cd memgraph-offline
sha256sum -c SHA256SUMS
chmod +x load-and-start.sh
./load-and-start.sh
```

`load-and-start.sh` loads `images/dgraph-offline-linux-amd64.tar` and runs `docker compose up -d`.

Check that the three containers are running:

```bash
docker ps
```

You should see `dgraph-zero`, `dgraph-alpha`, and `dgraph-ratel`.

If `git lfs` is missing, the clone only contains a small pointer file. Install Git LFS and run `git lfs pull` in the repo.

Manual start, after the archive is already on disk:

```bash
docker load -i images/dgraph-offline-linux-amd64.tar
docker compose up -d
```

These images are linux/amd64. The archive is about 93 MB. Alpha needs a few hundred megabytes of free disk for its data volume.

Stop the services with `docker compose down`. Data stays in the `dgraph_zero` and `dgraph_alpha` volumes. `docker compose down -v` deletes those volumes.

Logs:

```bash
docker logs -f dgraph-alpha
```

### Direct download

The archive is also available without cloning. No GitHub login is required.

```bash
curl -L -o dgraph-offline-linux-amd64.tar \
  https://github.com/kiranbeethoju/memgraph-offline/raw/refs/heads/main/images/dgraph-offline-linux-amd64.tar
```

GitHub Free includes 1 GB of Git LFS storage and 1 GB of LFS bandwidth per month. This archive is about 93 MB.

## Accessing Dgraph

No username or password is set. Ratel is a page served on port 8000. The browser then talks to Alpha's HTTP API. On this machine that address is `http://127.0.0.1:8080`. From another computer, use `http://<linux-ip>:8080`.

| Port | Use |
| --- | --- |
| 8000 | Ratel web UI |
| 8080 | Alpha HTTP. Ratel, queries, mutations, and schema |
| 9080 | Alpha gRPC. The Python client uses this port |
| 5080 | Zero gRPC, used by Alpha inside Compose |
| 6080 | Zero HTTP admin |

### Ratel

Open [http://localhost:8000](http://localhost:8000) on the Linux machine, or `http://<linux-ip>:8000` from another computer.

Set the Dgraph server URL to `http://127.0.0.1:8080` when the browser is on the same machine. From another computer, set it to `http://<linux-ip>:8080`. Leave the connection unencrypted.

A query you can run in Ratel:

```
{
  people(func: has(name)) {
    name
    age
  }
}
```

### HTTP

```bash
curl http://127.0.0.1:8080/health
```

A healthy Alpha returns JSON with `"status":"healthy"` for the `alpha` instance.

### Python

The starter in `python/quickstart.py` uses [pydgraph](https://github.com/dgraph-io/pydgraph). It sets a small schema, stores Alice and Bob, and reads Alice's friend.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python python/quickstart.py
```

Expected output:

```text
Connected to localhost:9080
People named Alice: 1
  Alice age 26 friend Bob
```

Point the script at another host without editing it:

```bash
DGRAPH_GRPC=192.168.1.20:9080 python python/quickstart.py
```

`pip install` needs network access or a local copy of the `pydgraph` package. The database image does not include that Python package.

## Images

Packed on 2026-11-10. One archive holds both images.

| Archive | Images loaded by `docker load` |
| --- | --- |
| `images/dgraph-offline-linux-amd64.tar` (93 MB) | `dgraph/dgraph:v25.5.1`, `dgraph/ratel:v25.3.0` |
