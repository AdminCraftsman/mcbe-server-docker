# AdCraft's Minecraft Bedrock Server Docker Image

**TL;DR:** A self-updating Docker image for a Minecraft Bedrock dedicated server — drop a `.mcworld` file in a `mods` folder and it's live on boot. [Jump to setup →](#quick-start)

## Why this exists

One of my kids loves Minecraft and, like every kid with a favorite streamer, wants whatever custom world or mod they just saw played — for about thirty minutes, until the next video changes their mind. They play on console, not PC, so anything beyond vanilla needs a server hosting it for them.

Manually re-provisioning a server every time the flavor of the week changes wasn't sustainable, especially over summer break. So instead: a vanilla, always-current Bedrock server image where "installing a mod" means dropping a file in a folder and restarting the container.

## What it does

- Builds a Bedrock Dedicated Server image on Arch Linux, running as a non-root user.
- Fetches the **latest** official Bedrock server binary at build time — rebuild the image and you're on the newest version, no manual URL/version bumping.
- On container boot, scans a mounted `mods` folder and installs anything it finds:
  - `.mcworld` files → extracted and set as the active world (`level-name` in `server.properties` is updated automatically).
- Everything lands where the actual `bedrock_server` binary expects it (`worlds/`, `behavior_packs/`, `resource_packs/`), so no extra wiring is needed after install.

### Coming soon

- `.mcpack` / `.mcaddon` (resource pack / behavior pack) installation is planned but not wired up yet — `fetch-packs.py` is a stub.

## Quick start

### 1. Get the image

Pull the published image from [Docker Hub](https://hub.docker.com/r/fingerhutascode/minecraft-bedrock-server):

```bash
docker pull fingerhutascode/minecraft-bedrock-server
```

Or build it yourself from source on [GitHub](https://github.com/AdminCraftsman/mcbe-server-docker):

```bash
./build.sh
```

### 2. Point a folder at your mods

Put the `.mcworld` file(s) you want loaded into a local folder, e.g. `./mods/`.

### 3. Configure `docker-compose.yml`

```yaml
services:
  bedrock:
    image: fingerhutascode/minecraft-bedrock-server:latest
    container_name: minecraft-bedrock-server
    restart: unless-stopped
    ports:
      - "19132:19132/udp"
    volumes:
      - ./mods:/home/minecraft/mods:ro
```

### 4. Start it up

```bash
docker compose up -d
```

On boot, the container installs whatever it finds in `mods/` and starts the server. To switch worlds, swap the file in `mods/` and restart the container:

```bash
docker compose restart
```

> **Note:** the world is reinstalled fresh from the `.mcworld` file on every boot, so in-game progress isn't preserved across restarts. This is intentional for the "swap mods on a whim" use case, not a bug — don't expect a save to survive a restart yet.

## Configuration

| Env var | Default | Purpose |
| --- | --- | --- |
| `MODS_DIR` | `/home/minecraft/mods` | Where to look for `.mcworld` files. |
| `WORLD_FILE` | *(unset)* | Pick a specific `.mcworld` by name when more than one exists in `MODS_DIR`. |
| `WORLD_NAME` | `Bedrock level` | Folder name for the installed world, and the `level-name` written to `server.properties`. |
| `DATA_DIR` | `/home/minecraft/data` | Scratch space used while extracting mod archives. |
| `BEDROCK_DIR` | `/home/minecraft` | Server root — rarely needs changing. |

## Directory layout

After a world with embedded packs is installed, the server root looks like:

```
/home/minecraft/
├── behavior_packs/
│   └── <pack-folder>/
├── resource_packs/
│   └── <pack-folder>/
└── worlds/
    └── <world-folder-name>/
        ├── level.dat
        ├── world_behavior_packs.json
        ├── world_resource_packs.json
        └── db/
```

## Credits

Bedrock server version discovery in `fetch-server.sh` uses [kittizz's bedrock-server-downloads](https://github.com/kittizz/bedrock-server-downloads) feed.
