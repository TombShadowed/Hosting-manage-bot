<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=180&text=HOSTING-BOT&fontAlign=50&fontAlignY=38&fontSize=42&fontColor=FFFFFF&color=0:050810,45:00E5FF,100:7CFFB2&animation=fadeIn&desc=TELEGRAM%20BOT%20HOSTING%20MANAGER&descAlign=50&descAlignY=62&descSize=15" alt="HOSTING-BOT banner" />

<br />

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=18&duration=2200&pause=700&color=00E5FF&center=true&vCenter=true&width=760&lines=%5B+DEPLOY+BOTS+%5D+%5B+CONTROL+RUNTIME+%5D+%5B+MONITOR+SYSTEM+%5D;%5B+PYTHON+3.11%2B+%5D+%5B+SQLITE+%2F+MONGODB+%5D+%5B+SYSTEMD+READY+%5D" alt="animated project summary" />

<br /><br />

<code>LIGHTWEIGHT . COMMAND DRIVEN . OWNER CONTROLLED . DEPLOY READY</code>

<br /><br />

<img src="https://img.shields.io/badge/PYTHON-3.11+-0B1220?style=for-the-badge&labelColor=050810&color=00E5FF" alt="Python 3.11+" />
<img src="https://img.shields.io/badge/STORAGE-SQLITE%20%7C%20MONGODB-0B1220?style=for-the-badge&labelColor=050810&color=7CFFB2" alt="SQLite or MongoDB" />
<img src="https://img.shields.io/badge/RUNTIME-TELEGRAM-0B1220?style=for-the-badge&labelColor=050810&color=8AB4FF" alt="Telegram runtime" />
<img src="https://img.shields.io/badge/DEPLOY-HEROKU%20%7C%20DOCKER%20%7C%20VPS-0B1220?style=for-the-badge&labelColor=050810&color=FFCA3A" alt="Deploy targets" />

<br /><br />

<a href="#-overview-"><code>OVERVIEW</code></a>
<code> | </code>
<a href="#-quick-start-"><code>QUICK START</code></a>
<code> | </code>
<a href="#-command-deck-"><code>COMMANDS</code></a>
<code> | </code>
<a href="#-deployment-"><code>DEPLOY</code></a>
<code> | </code>
<a href="#-copyright-"><code>COPYRIGHT</code></a>

</div>

---

```text
                  _   _  ___  ____ _____ ___ _   _  ____       ____   ___ _____
                 | | | |/ _ \/ ___|_   _|_ _| \ | |/ ___|     | __ ) / _ \_   _|
                 | |_| | | | \___ \ | |  | ||  \| | |  _ _____|  _ \| | | || |
                 |  _  | |_| |___) || |  | || |\  | |_| |_____| |_) | |_| || |
                 |_| |_|\___/|____/ |_| |___|_| \_|\____|     |____/ \___/ |_|

                              [ TELEGRAM BOT HOSTING CONTROL PANEL ]
```

## <code>[ OVERVIEW ]</code>

`HOSTING-BOT` is a Telegram bot hosting manager that helps you deploy, control, and monitor Telegram bots from a clean command interface.

```text
[ MODE ]        MASTER BOT
[ CONTROL ]     START . STOP . RESTART . REGISTER
[ STORAGE ]     SQLITE DEFAULT . MONGODB OPTIONAL
[ ACCESS ]      OWNER . ADMIN . PREMIUM . REDEEM
[ DEPLOY ]      HEROKU . DOCKER . KOYEB . VPS
```

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&height=2&color=gradient&customColorList=12,13,14,24" alt="section divider" />

</div>

## <code>[ FEATURE GRID ]</code>

| SYMBOL | MODULE | DETAIL |
| :---: | --- | --- |
| `[+]` | `COMMAND UI` | Telegram-first control surface with clean bot commands |
| `[#]` | `LIFECYCLE` | Register, start, stop, restart, and inspect hosted bots |
| `[*]` | `STORAGE` | SQLite by default, MongoDB when `MONGO_URI` is configured |
| `[~]` | `ACCESS` | Owner/admin controls, premium users, redeem flow, rate limits |
| `[/]` | `OBSERVE` | Health checks, system stats, runtime logs, basic CI |
| `[>]` | `DEPLOY` | Heroku worker, Docker/Koyeb build, VPS systemd service |

## <code>[ QUICK START ]</code>

### <code>01 . INSTALL DEPENDENCIES</code>

```bash
python -m pip install -r requirements.txt
```

### <code>02 . SET ENVIRONMENT</code>

```bash
export TELEGRAM_TOKEN=your_bot_token
export TELEGRAM_API_ID=123456
export TELEGRAM_API_HASH=your_api_hash
export OWNER_ID=123456789
```

<details>
<summary><code>WINDOWS POWERSHELL VARIANT</code></summary>

```powershell
$env:TELEGRAM_TOKEN="your_bot_token"
$env:TELEGRAM_API_ID="123456"
$env:TELEGRAM_API_HASH="your_api_hash"
$env:OWNER_ID="123456789"
```

</details>

### <code>03 . START MASTER BOT</code>

```bash
python main.py
```

## <code>[ PROJECT MAP ]</code>

```text
HOSTING-BOT
|-- main.py                         [ runtime entrypoint ]
|-- bot.py                          [ app wiring and command registration ]
|-- config.py                       [ environment-driven configuration ]
|-- cmds/                           [ Telegram command handlers ]
|   |-- start.py
|   |-- register.py
|   |-- bots_management.py
|   |-- premium.py
|   `-- system.py
|-- core/
|   |-- manager.py                  [ bot lifecycle control ]
|   |-- storage.py                  [ file, SQLite, MongoDB storage ]
|   |-- deployer.py                 [ deployment helpers ]
|   |-- rate_limit.py
|   `-- utils.py
|-- deploy/systemd/hosting-bot.service
|-- Dockerfile
|-- docker-compose.yml
|-- Procfile
`-- tests/
```

## <code>[ COMMAND DECK ]</code>

| COMMAND | ACCESS | PURPOSE |
| --- | :---: | --- |
| `/start` | `USER` | Show the welcome interface |
| `/help` | `USER` | Show available commands |
| `/bots` | `USER` | List deployed bots |
| `/register` | `USER` | Register a bot for hosting |
| `/startbot` | `USER` | Start a hosted bot |
| `/stop` | `USER` | Stop a hosted bot |
| `/restart` | `USER` | Restart a hosted bot |
| `/status` | `USER` | Show hosted bot status |
| `/health` | `USER` | Run a simple health check |
| `/system` | `ADMIN` | Show system stats |
| `/add_premium <id> [plan] [duration]` | `OWNER` | Grant premium access |
| `/rem_premium <id>` | `OWNER` | Revoke premium access |

## <code>[ CONFIG NOTES ]</code>

| KEY | REQUIRED | NOTE |
| --- | :---: | --- |
| `TELEGRAM_TOKEN` | `YES` | Telegram bot token from BotFather |
| `TELEGRAM_API_ID` | `YES` | Telegram API ID |
| `TELEGRAM_API_HASH` | `YES` | Telegram API hash |
| `OWNER_ID` | `YES` | Telegram user ID for owner access |
| `MONGO_URI` | `NO` | Optional MongoDB connection string |
| `BASE_DATA_DIR` | `NO` | Optional runtime data directory |

```text
[ STORAGE RULE ]
IF MONGO_URI EXISTS  -> USE MONGODB
ELSE                 -> USE LOCAL SQLITE
```

Runtime logs are written under `BASE_DATA_DIR/logs/master-bot.log`.

## <code>[ DEPLOYMENT ]</code>

### <code>HEROKU WORKER</code>

```text
[1] CREATE HEROKU APP
[2] SET CONFIG VARS
    TELEGRAM_TOKEN
    TELEGRAM_API_ID
    TELEGRAM_API_HASH
    OWNER_ID
[3] PUSH REPOSITORY
[4] PROCFILE STARTS THE WORKER
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

## <code>[ BRANDING ]</code>

Displayed links and text can be customized in `.env` and `cmds/start.py`.

```text
[ EDIT .ENV ]          OWNER IDS . CHANNEL LINKS . RUNTIME VALUES
[ EDIT cmds/start.py ] WELCOME TEXT . BUTTONS . START SCREEN
```

## <code>[ CREDITS ]</code>

Made and maintained by the Telegram channel: [`SHADOWEDTOMB`](https://t.me/ShadowedTomb)

## <code>[ COPYRIGHT ]</code>

<div align="center">

<code>COPYRIGHT (C) 2026 YOUR-GITHUB-USERNAME . ALL RIGHTS RESERVED</code>

<br /><br />

<a href="https://github.com/TombShadowed">
  <img src="https://img.shields.io/badge/TombShadowed-0B1220?style=for-the-badge&logo=github&logoColor=white&labelColor=050810&color=00E5FF" alt="GitHub profile" />
</a>

<br /><br />

<sub><code>[ SOURCE CREDIT MUST BE PRESERVED WHEN SHARING OR MODIFYING THIS PROJECT ]</code></sub>

</div>

<div align="center">

<br />

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=18&duration=3000&pause=900&color=7CFFB2&center=true&vCenter=true&width=760&lines=%5B+SYSTEM+ONLINE+%5D;%5B+DEPLOY+THE+BOT+%5D;%5B+CONTROL+THE+RUNTIME+%5D;%5B+WATCH+THE+LOGS+%5D" alt="animated footer" />

<br /><br />

<img src="https://capsule-render.vercel.app/api?type=waving&height=110&section=footer&color=0:7CFFB2,45:00E5FF,100:050810" alt="footer wave" />

<br />

<code>[ END ]</code>

</div>
