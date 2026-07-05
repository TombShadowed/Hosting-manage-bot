# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from pyrogram import Client

import config as config
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_TOKEN, OWNER_IDS
from core.manager import BotManager

logger = logging.getLogger('master.pyro')

manager = BotManager()

app = Client('master-bot', api_id=int(TELEGRAM_API_ID) if TELEGRAM_API_ID else None,
             api_hash=TELEGRAM_API_HASH, bot_token=TELEGRAM_TOKEN)


# Configure structured logging (file + rotation + console)
try:
    log_dir = Path(config.BASE_DATA_DIR) / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'master-bot.log'
    handler = RotatingFileHandler(str(log_file), maxBytes=5 * 1024 * 1024, backupCount=5)
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
    handler.setFormatter(fmt)
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(handler)
        # also add a console handler
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        root_logger.addHandler(ch)
except Exception:
    # best-effort, don't crash on logging setup
    pass


def is_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS


def is_admin(user_id: int) -> bool:
    try:
        admins = manager.get_admins()
    except Exception:
        admins = []
    return user_id in admins or is_owner(user_id)


# Initialize command modules (each module exposes init(app, manager, OWNER_IDS))
from cmds import (
    start, help_cmd, register, remove, bots_management, restart,
    addadmin, deladmin, admins, system, premium, info, forcesub,
    add_premium, rem_premium, premium_users, adminonly, addredeem, redeem
)

start.init(app, manager, OWNER_IDS)
help_cmd.init(app, manager, OWNER_IDS)
register.init(app, manager, OWNER_IDS)
remove.init(app, manager, OWNER_IDS)
bots_management.init(app, manager, OWNER_IDS)
restart.init(app, manager, OWNER_IDS)
addadmin.init(app, manager, OWNER_IDS)
deladmin.init(app, manager, OWNER_IDS)
admins.init(app, manager, OWNER_IDS)
system.init(app, manager, OWNER_IDS)
premium.init(app, manager, OWNER_IDS)
info.init(app, manager, OWNER_IDS)
add_premium.init(app, manager, OWNER_IDS)
rem_premium.init(app, manager, OWNER_IDS)
premium_users.init(app, manager, OWNER_IDS)
adminonly.init(app, manager, OWNER_IDS)
addredeem.init(app, manager, OWNER_IDS)
redeem.init(app, manager, OWNER_IDS)
forcesub.init(app, manager, OWNER_IDS)


def run():
    errors = config.validate_config() if hasattr(config, 'validate_config') else []
    if errors:
        for e in errors:
            logger.error(e)
        logger.error('Missing required configuration; aborting startup')
        return

    logger.info('Starting Pyrogram master bot...')
    app.run()


if __name__ == '__main__':
    run()
