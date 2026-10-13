# Cumulus Local Development Environment

This guide sets up a local Cumulus stack on an Ubuntu machine or VM:

| Repo | What it runs locally | How |
| --- | --- | --- |
| [cumulus-api](https://github.com/USACE/cumulus-api) | Postgres/PostGIS, Flyway migrations, Go API, async listener, geoprocess and packager workers, ElasticMQ (SQS), MinIO (S3), pg_featureserv | Docker Compose |
| [airflow-config](https://github.com/USACE/airflow-config) | Airflow scheduler, workers, UI, and its own Postgres, Redis and ElasticMQ | Docker Compose |
| [cumulus-ui](https://github.com/USACE/cumulus-ui) | React front end (Vite dev server) | Node.js on the host |
| [cumulus-geoproc](https://github.com/USACE/cumulus-geoproc) | Grid processors (optional; only needed if you are changing processors) | Docker Compose |

Only Docker, Git, and Node.js are installed on the host. GDAL, Go and Python all run inside containers.

---

## 1. Host setup (one time)

Recommended VM size: 4+ CPUs, 8+ GB RAM, 60+ GB disk. The GDAL-based images are several GB each, and Airflow alone uses a few GB of RAM.

### 1.1 Base packages and Git

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
```

To push to GitHub, you need a [personal access token](https://github.com/settings/tokens) or an SSH key. The repos are public, so you can clone them without one.

### 1.2 Docker Engine + Compose plugin

These steps follow Docker's [official Ubuntu instructions](https://docs.docker.com/engine/install/ubuntu/):

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Run docker without sudo. The package already creates the "docker" group.
sudo usermod -aG docker $USER
```

**Log out and back in** (or reboot the VM) so the group change takes effect. Then check the install:

```bash
docker run --rm hello-world
docker compose version     # must be v2 ("docker compose", not "docker-compose")
```

### 1.3 Node.js (only for cumulus-ui)

Install Node through [nvm](https://github.com/nvm-sh/nvm). Ubuntu's `nodejs`/`npm` packages are too old for Vite 6, and NodeSource's `setup_19.x` is end of life.

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# open a new terminal, then:
nvm install 22
nvm alias default 22
node -v   # v22.x
```

### 1.4 Clone the repos

Put all the repos in the same parent folder:

```bash
mkdir -p ~/code && cd ~/code
git clone https://github.com/USACE/cumulus-api.git
git clone https://github.com/USACE/airflow-config.git
git clone https://github.com/USACE/cumulus-ui.git
# optional, only for processor development:
git clone https://github.com/USACE/cumulus-geoproc.git

for r in cumulus-api airflow-config cumulus-ui; do git -C $r checkout cwbi-dev; done
```

---

## 2. Cumulus API

### 2.1 How the stack fits together

- **`docker-compose.yml`**: `cumulusdb`, `flyway`, `api`, `listener`, `geoprocess`, `packager`, `elasticmq`, `featureserv`.
- **`docker-compose.minio.yml`**: `minio` and `minio_init`. `minio_init` creates the buckets `castle-data-develop` and `cwbi-airflow-dev`, then uploads everything in `_volumes/minio/cumulus/` to `castle-data-develop/cumulus/`. **Always include MinIO locally.** The API, the workers and Airflow all expect it.
- **Flyway** runs `sql/common` + `sql/local` on every `up`. `sql/local` holds the local seed data (products, test downloads, and so on). Flyway only applies migrations that have not run yet, so an existing database is not re-seeded.
- The compose network is named **`cumulus-api_default`**. Airflow joins it as an *external* network, which is why **cumulus-api has to be started before Airflow**.
- The `geoprocess` image installs the processors from **GitHub `USACE/cumulus-geoproc@main`** at build time. Your local `cumulus-geoproc` checkout is **not** used by this stack (see section 5).

### 2.2 `compose.sh` cheat sheet

`compose.sh` is a thin wrapper around `docker compose`. Pass `-m` on **every** command so MinIO is included consistently.

| Command | Runs | Effect on data |
| --- | --- | --- |
| `./compose.sh -bm` | `up --build` (foreground) | Keeps data if containers already exist |
| `./compose.sh -m` | `up` (foreground, no rebuild) | Keeps data |
| `./compose.sh -sm` | `stop` | **Keeps** DB + MinIO data |
| `./compose.sh -dm` | `down` | **Resets** DB + MinIO on the next `up` (see section 2.5) |
| `./compose.sh -h` | help | |

`compose.sh` always runs in the foreground and cannot pass `-d`, `-v`, `logs`, or `exec`. For those, run `docker compose` directly with both files. An alias makes this easy (add it to `~/.bashrc`):

```bash
alias cdc='docker compose -f docker-compose.yml -f docker-compose.minio.yml'
```

The rest of this guide uses `cdc`. Run it from the `cumulus-api` directory.

### 2.3 Start

```bash
cd ~/code/cumulus-api
./compose.sh -bm            # first time, or after changing a Dockerfile or service code
# or, detached:
cdc up -d --build
```

The first build takes several minutes because of the GDAL images. The stack is ready when:

- `flyway-1` exits with code 0 (`Successfully applied N migrations`, or `Schema ... is up to date`)
- `listener-1` prints `received no work for 90 seconds; checking for new work` (after about 90 s)
- `curl http://localhost/api/health` returns `{"status":"healthy",...}`

If you started detached, watch the logs with `cdc logs -f` (or `cdc logs -f api listener`).

### 2.4 Stop / restart **keeping data**

```bash
# foreground: press Ctrl+C once (graceful stop), or from another terminal:
./compose.sh -sm            # == cdc stop

# later:
./compose.sh -m             # or: cdc up -d
```

Postgres and MinIO keep their data in **anonymous Docker volumes** attached to their containers. `stop`/`start`, and even `up --build` (which recreates containers), keep those volumes. The data survives as long as the containers are not removed.

> Ctrl+**C** stops a foreground `docker compose up`. Ctrl+**D** does nothing there.

### 2.5 Reset **everything** (fresh DB + empty MinIO)

```bash
cdc down -v                 # removes containers, network, AND their anonymous volumes
./compose.sh -bm            # fresh DB, Flyway re-runs all migrations + local seed, MinIO re-initialized
```

`./compose.sh -dm` (plain `down`, as in the old instructions) *also* gives you a fresh DB and MinIO on the next `up`, because new containers get new anonymous volumes. However, it leaves the old volumes on disk. Over time these pile up, and you can remove them with:

```bash
docker volume ls -f dangling=true      # review first
docker volume prune                    # removes ALL unused anonymous volumes, including other projects'
```

Prefer `cdc down -v` so nothing piles up.

### 2.6 Reset only the database, or only MinIO

```bash
# Fresh database, keep MinIO objects
cdc rm -s -f -v cumulusdb
cdc up -d                   # new cumulusdb volume; flyway re-runs all migrations + seed

# Empty MinIO, keep the database
cdc rm -s -f -v minio
cdc up -d                   # minio_init re-creates buckets and re-uploads _volumes/minio/cumulus/
```

After a MinIO-only reset, `productfile` rows in the database will point at objects that no longer exist. Reset both if you need them to match.

### 2.7 Keeping data across `down` (optional)

If you want data to survive `down` as well (not just `stop`), give Postgres and MinIO **named** volumes. Create an untracked file `docker-compose.volumes.yml`:

```yaml
services:
  cumulusdb:
    volumes:
      - cumulus_pgdata:/var/lib/postgresql/data
  minio:
    volumes:
      - cumulus_minio:/data
volumes:
  cumulus_pgdata:
  cumulus_minio:
```

Then include it in the alias:

```bash
alias cdc='docker compose -f docker-compose.yml -f docker-compose.minio.yml -f docker-compose.volumes.yml'
```

With this file, `cdc down` keeps the data and `cdc down -v` resets it. `compose.sh` does not know about this file, so use `cdc` consistently if you adopt it.

### 2.8 Day-to-day tasks

| Task | Command |
| --- | --- |
| Rebuild/restart only the API after Go changes | `cdc up -d --build api` |
| Rebuild one worker | `cdc up -d --build geoprocess` (or `packager`, `listener`) |
| Follow logs | `cdc logs -f api` |
| psql as superuser | `cdc exec cumulusdb psql -U postgres` (tables are in schema `cumulus`: `SET search_path TO cumulus, public;`) |
| Re-run migrations | `cdc up flyway` |
| Load geoproc test acquirables into MinIO + API (optional) | `./dcompose minio geoinit up --build` |
| Service status | `cdc ps` |

The API image is a compiled Go binary on `scratch`. The `./api` bind mount does **not** hot-reload, so you must rebuild after code changes.

### 2.9 Local services and credentials

| Service | URL / port | Credentials |
| --- | --- | --- |
| Cumulus API | http://localhost/api (health: `/api/health`) | Auth is mocked (`CUMULUS_AUTH_ENVIRONMENT=MOCK`); application key `appkey` |
| Features (via API proxy) | http://localhost/features | |
| pg_featureserv (direct) | http://localhost:8080 | |
| Postgres/PostGIS | `localhost:5432`, db `postgres` | `postgres`/`postgres` (admin), `cumulus_user`/`cumulus_pass` (app) |
| MinIO console | http://localhost:9001 (S3 API on 9000) | `AKIAIOSFODNN7EXAMPLE` / `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| ElasticMQ (SQS) | http://localhost:9324 (UI: 9325) | |

**Port conflicts:** ports 80, 5432, 8080, 9000 and 9001 have to be free. If another project on the machine (another MinIO or Postgres, for example) holds one of them, the corresponding container exits right away. Check with `docker ps` and stop the other stack first.

---

## 3. Airflow

### 3.1 One-time setup

```bash
cd ~/code/airflow-config
git checkout cwbi-dev

# .env is required (docker-compose.yml lists it as env_file) and is gitignored
cat > .env <<'EOF'
export AIRFLOW_VAR_CDA_URL=https://water.dev.cwbi.us/cwms-data/
export AIRFLOW_VAR_API_KEY=foo
EOF

# The containers run as UID 50000 and must be able to write these bind mounts
chmod 777 dags logs plugins
```

`API_KEY=foo` is enough for the DAGs to load. Only DAGs that actually write to CWMS Data API need a real key.

### 3.2 Start

**Cumulus API must already be running**, because Airflow attaches to the `cumulus-api_default` network. Otherwise you get `network cumulus-api_default declared as external, but could not be found`.

```bash
cd ~/code/airflow-config
docker compose up --build     # first time (slow); afterwards: docker compose up   (add -d to detach)
```

Do **not** use `./compose.sh -m` in airflow-config while the cumulus-api stack is running. Its MinIO would collide on ports 9000/9001. Airflow already uses the cumulus-api MinIO (`LOCAL_MINIO` connection → `http://minio:9000` on the shared network).

Airflow is ready when `docker ps` shows `airflow-ui` as `(healthy)`, or when `curl -f http://localhost:8000/health` succeeds. The UI's access log is sent to `/dev/null`, so the old `GET /health ... 200` log line no longer appears.

| Service | URL | Credentials |
| --- | --- | --- |
| Airflow UI | http://localhost:8000/home | `airflow` / `airflow` |
| Flower (Celery) | http://localhost:5555 | |
| Airflow Postgres | `localhost:50432` | `airflow` / `airflow` |

DAGs start **paused** (`DAGS_ARE_PAUSED_AT_CREATION`). Unpause the ones you need in the UI. Edits to files in `dags/` are picked up within about 30–60 s, with no restart needed.

### 3.3 Stop / reset

```bash
docker compose stop        # keep Airflow metadata (DAG runs, users, variables)
docker compose down        # metadata DB is recreated on next up (airflow_init re-creates the airflow user + variables)
docker compose down -v     # same, and also deletes the old volumes
```

Airflow task logs are sent to MinIO (`s3://cwbi-airflow-dev/airflow/logs`), so resetting cumulus-api's MinIO also clears them.

---

## 4. Cumulus UI

```bash
cd ~/code/cumulus-ui
git checkout cwbi-dev
npm ci                       # or npm install
npm run dev                  # http://localhost:5173
```

The old `npm start` no longer exists, because the project moved from Create React App to Vite.

Local settings live in `.env.development.local` (committed):

- `VITE_CUMULUS_API_URL=http://localhost/api`: your local API. Change it to `https://cumulus.dev.cwbi.us/api` to use the dev server instead.
- `VITE_AUTH_MOCK_USER=ADMIN` (or `USER`): skips Keycloak login. Leave it blank to use real auth.

---

## 5. Geoprocessors (optional)

You do **not** need GDAL on the host (`pip install gdal` / `gdal-bin` is unnecessary). Processor development and tests run in the `cumulus-geoproc` container:

```bash
cd ~/code/cumulus-geoproc
docker compose run --rm geoproc      # default entrypoint runs pytest against the test data
docker compose down -v
```

See that repo's README for the three entrypoint options (shell, pytest, single-processor runner).

To run a local processor branch inside the cumulus-api stack, change the `GEOPROC_PACKAGE` build arg of `geoprocess` in `docker-compose.yml` (format `<git-ref>:geoproc`). Push the branch first, then run `cdc up -d --build geoprocess`.

---

## 6. Full start / stop order

**Start**

1. `cd cumulus-api && cdc up -d --build` (or `./compose.sh -bm` in its own terminal)
2. Wait for `curl http://localhost/api/health`
3. `cd airflow-config && docker compose up -d`
4. `cd cumulus-ui && npm run dev`

**Stop (keep data)**: stop in the reverse order.

1. Ctrl+C the UI dev server
2. `cd airflow-config && docker compose stop`
3. `cd cumulus-api && ./compose.sh -sm`

**Stop and reset**

1. `cd airflow-config && docker compose down -v`
2. `cd cumulus-api && cdc down -v`

Airflow has to come down first. `cumulus-api`'s `down` cannot remove the `cumulus-api_default` network while Airflow containers are still attached to it.

---

## 7. Known stale bits in this repo

- `README.md` refers to `docker-compose up`, a `site/` UI folder, and pgAdmin on port 7000. None of these apply anymore; this document replaces them.
- `reload_db.sh` uses the old Compose v1 container name (`cumulus-api_cumulusdb_1`) and a `/sql` path that is not mounted into `cumulusdb`, so it does not work as written.
- `./compose.sh -u` does nothing on its own. Use `./compose.sh -m` to start.
