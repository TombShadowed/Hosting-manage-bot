<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=30&duration=2600&pause=900&color=00E5FF&center=true&vCenter=true&width=760&lines=HOSTING-BOT;TELEGRAM+BOT+HOSTING+MANAGER;DEPLOY+%2F+CONTROL+%2F+MONITOR" alt="HOSTING-BOT animated title" />

<br />

<code>LIGHTWEIGHT . FAST . OWNER CONTROLLED . DEPLOY READY</code>

<br /><br />

<img src="https://img.shields.io/badge/PYTHON-3.11+-0B1220?style=for-the-badge&labelColor=050810&color=00E5FF" alt="Python 3.11+" />
<img src="https://img.shields.io/badge/STORAGE-SQLITE%20%7C%20MONGODB-0B1220?style=for-the-badge&labelColor=050810&color=7CFFB2" alt="SQLite or MongoDB" />
<img src="https://img.shields.io/badge/DEPLOY-HEROKU%20%7C%20DOCKER%20%7C%20VPS-0B1220?style=for-the-badge&labelColor=050810&color=FFCA3A" alt="Deploy targets" />

</div>

---

```text
 __  __  ___  ____  _____ ___ _   _  ____       ____   ___ _____
|  \/  |/ _ \/ ___||_   _|_ _| \ | |/ ___|     | __ ) / _ \_   _|
| |\/| | | | \___ \  | |  | ||  \| | |  _ _____|  _ \| | | || |
| |  | | |_| |___) | | |  | || |\  | |_| |_____| |_) | |_| || |
|_|  |_|\___/|____/  |_| |___|_| \_|\____|     |____/ \___/ |_|
```

## <code>[ OVERVIEW ]</code>

`HOSTING-BOT` is a Telegram bot hosting manager for deploying, controlling, and monitoring Telegram bots from a command-driven interface.

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&height=2&color=gradient&customColorList=12,13,14,24" alt="animated divider" />

</div>

## <code>[ HIGHLIGHTS ]</code>

| SYMBOL | FEATURE |
| :---: | --- |
| `[+]` | Clean Telegram command interface |
| `[#]` | Bot lifecycle management: start, stop, restart, register |
| `[*]` | Durable storage through SQLite or MongoDB |
| `[~]` | Owner/admin controls, premium users, redeem flow, rate limits |
| `[/]` | Health checks, system stats, logs, and CI coverage |
| `[>]` | Deployable on Heroku, Docker/Koyeb, or VPS with systemd |

## <code>[ QUICK START ]</code>

### <code>01 . INSTALL</code>

```bash
python -m pip install -r requirements.txt
```

### <code>02 . CONFIGURE</code>

Set the required environment variables:

```bash
export TELEGRAM_TOKEN=your_bot_token
export TELEGRAM_API_ID=123456
export TELEGRAM_API_HASH=your_api_hash
export OWNER_ID=123456789
```

On Windows PowerShell:

```powershell
$env:TELEGRAM_TOKEN="your_bot_token"
$env:TELEGRAM_API_ID="123456"
$env:TELEGRAM_API_HASH="your_api_hash"
$env:OWNER_ID="123456789"
```

### <code>03 . RUN</code>

```bash
python main.py
```

## <code>[ PROJECT MAP ]</code>

```text
HOSTING-BOT
|-- bot.py                         -> app wiring and command registration
|-- main.py                        -> runtime entrypoint
|-- config.py                      -> environment-driven configuration
|-- cmds/                          -> Telegram command handlers
|-- core/manager.py                -> bot lifecycle control
|-- core/storage.py                -> file, SQLite, and MongoDB storage
|-- core/deployer.py               -> deployment helpers
|-- deploy/systemd/hosting-bot.service
|-- Dockerfile
|-- docker-compose.yml
|-- Procfile
`-- tests/
```

## <code>[ COMMAND DECK ]</code>

| COMMAND | PURPOSE |
| --- | --- |
| `/start` | Show the welcome interface |
| `/help` | Show available commands |
| `/bots` | List deployed bots |
| `/register` | Register a bot for hosting |
| `/startbot` | Start a hosted bot |
| `/stop` | Stop a hosted bot |
| `/restart` | Restart a hosted bot |
| `/status` | Show bot status |
| `/system` | Show system stats for owners/admins |
| `/health` | Run a simple health check |
| `/add_premium <id> [plan] [duration]` | Grant premium access |
| `/rem_premium <id>` | Revoke premium access |

## <code>[ DEPLOYMENT ]</code>

### <code>HEROKU</code>

```text
[1] CREATE A HEROKU APP
[2] SET CONFIG VARS:
    TELEGRAM_TOKEN
    TELEGRAM_API_ID
    TELEGRAM_API_HASH
    OWNER_ID
[3] PUSH THE REPO
[4] PROCFILE RUNS THE BOT AS A WORKER
```

### <code>DOCKER / KOYEB</code>

Koyeb can deploy this project through the included `Dockerfile`. For local Docker usage:

```bash
docker-compose up -d --build
```

### <code>VPS / SYSTEMD</code>

Install Python 3.11, create a virtual environment, install dependencies, then adjust `deploy/systemd/hosting-bot.service` for your server paths and environment values.

```bash
sudo cp deploy/systemd/hosting-bot.service /etc/systemd/system/hosting-bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now hosting-bot
sudo journalctl -u hosting-bot -f
```

## <code>[ CONFIG NOTES ]</code>

| KEY | NOTE |
| --- | --- |
| `TELEGRAM_TOKEN` | Telegram bot token from BotFather |
| `TELEGRAM_API_ID` | Telegram API ID |
| `TELEGRAM_API_HASH` | Telegram API hash |
| `OWNER_ID` | Telegram user ID for owner access |
| `MONGO_URI` | Optional MongoDB connection string |
| `BASE_DATA_DIR` | Optional runtime data directory |

If `MONGO_URI` is not provided, the bot can use local SQLite storage by default. Runtime logs are written under `BASE_DATA_DIR/logs/master-bot.log`.

## <code>[ BRANDING ]</code>

Displayed links and text can be customized in `.env` and `cmds/start.py`.

## <code>[ CREDITS ]</code>

Made and maintained by the Telegram channel: [`SHADOWEDTOMB`](https://t.me/ShadowedTomb)

## <code>[ COPYRIGHT ]</code>

<div align="center">

<code>COPYRIGHT (C) 2026 YOUR-GITHUB-USERNAME . ALL RIGHTS RESERVED</code>

<br /><br />

<a href="https://github.com/YOUR-GITHUB-USERNAME">
  <img src="https://img.shields.io/badge/GITHUB-YOUR--GITHUB--USERNAME-0B1220?style=for-the-badge&logo=github&logoColor=white&labelColor=050810&color=00E5FF" alt="GitHub profile" />
</a>

<br /><br />

<sub><code>[ SOURCE CREDIT MUST BE PRESERVED WHEN SHARING OR MODIFYING THIS PROJECT ]</code></sub>

</div>

<div align="center">

<br />

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=18&duration=3000&pause=1000&color=7CFFB2&center=true&vCenter=true&width=720&lines=%5B+DEPLOY+THE+BOT+%5D;%5B+CONTROL+THE+FLEET+%5D;%5B+WATCH+THE+SYSTEM+%5D" alt="animated footer" />

<br />

<code>[ END OF TRANSMISSION ]</code>

</div>
