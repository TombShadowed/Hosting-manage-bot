<h2 align="center">
    ──「 𝗛𝗢𝗦𝗧𝗜𝗡𝗚 𝗠𝗔𝗡𝗔𝗚𝗘𝗥 」──
</h2>

<p align="center">
  <img src="https://i.ibb.co/4wTRN43F/photo-2026-07-05-09-03-56-7658967178955194408.jpg">
</p>

----

## <code>| OVERVIEW |</code>
---
> `HOSTING-BOT` is a Telegram bot hosting manager that helps you deploy, control, and monitor Telegram bots from a clean command interface.
---

```text
[ MODE ]        MASTER BOT
[ CONTROL ]     START . STOP . RESTART . REGISTER
[ STORAGE ]     SQLITE DEFAULT . MONGODB OPTIONAL
[ ACCESS ]      OWNER . ADMIN . PREMIUM . REDEEM
[ DEPLOY ]      HEROKU . DOCKER . KOYEB . VPS
```

<div align="center">

---
</div>

## <code>| FEATURE GRID |</code>
---
| SYMBOL | MODULE | DETAIL |
| :---: | --- | --- |
| `[+]` | `COMMAND UI` | Telegram-first control surface with clean bot commands |
| `[#]` | `LIFECYCLE` | Register, start, stop, restart, and inspect hosted bots |
| `[*]` | `STORAGE` | SQLite by default, MongoDB when `MONGO_URI` is configured |
| `[~]` | `ACCESS` | Owner/admin controls, premium users, redeem flow, rate limits |
| `[/]` | `OBSERVE` | Health checks, system stats, runtime logs, basic CI |
| `[>]` | `DEPLOY` | Heroku worker, Docker/Koyeb build, VPS systemd service |
---
## <code>| QUICK START |</code>
---
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
---
## <code>| PROJECT MAP |</code>
---
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
---
## <code>| COMMAND DECK |</code>
---
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
---
## <code>| CONFIGS NOTE |</code>
---
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
---
## <code>| DEPLOYMENT |</code>
---
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
---
## <code>| BRANDING |</code>
---
Displayed links and text can be customized in `.env` and `cmds/start.py`.

```text
[ EDIT .ENV ]          OWNER IDS . CHANNEL LINKS . RUNTIME VALUES
[ EDIT cmds/start.py ] WELCOME TEXT . BUTTONS . START SCREEN
```
----
## <code>[ ᴄʀᴇᴅɪᴛs ]</code>

<p align="center">
  <img src="https://i.ibb.co/rK3Fwptg/photo-2026-07-05-09-09-48-7658968609179303968.jpg">
</p>

----

Made and maintained by the Telegram channel: [`SHADOWEDTOMB`](https://telegram.me/ShadowedTomb)

## <code>[ ᴄᴏᴘʏʀɪɢʜᴛ ]</code>

<div align="center">

<code>COPYRIGHT (C) 2026 Shadowed-Tomb . ALL RIGHTS RESERVED</code>

<br /><br />

<a href="https://github.com/TombShadowed">
  <img src="https://img.shields.io/badge/TombShadowed-0B1220?style=for-the-badge&logo=github&logoColor=white&labelColor=050810&color=00E5FF" alt="GitHub profile" />
</a>

<br /><br />

<sub><code>[ SOURCE CREDIT MUST BE PRESERVED WHEN SHARING OR MODIFYING THIS PROJECT ]</code></sub>

</div>

<div align="center">

<br />

<code>[ END ]</code>

</div>
