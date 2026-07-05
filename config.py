# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

import os
from pathlib import Path
from typing import List

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_API_ID = os.environ.get('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.environ.get('TELEGRAM_API_HASH')
BASE_DATA_DIR = Path(os.environ.get('BASE_DATA_DIR', './mnt/data/bots'))
BASE_DATA_DIR.mkdir(parents=True, exist_ok=True)
MONGO_URI = os.environ.get('MONGO_URI')
MONGO_DB = os.environ.get('MONGO_DB', 'master_bot')
OWNER_ID_RAW = os.environ.get('OWNER_ID', '')

OWNER_IDS: List[int] = []
for part in OWNER_ID_RAW.split(','):
    part = part.strip()
    if not part:
        continue
    try:
        OWNER_IDS.append(int(part))
    except Exception:
        pass

# Optional
START_PIC = os.environ.get('START_PIC')
ABOUT_PIC = os.environ.get('ABOUT_PIC')
TERMS_PIC = os.environ.get('TERMS_PIC')
HELP_PIC = os.environ.get('HELP_PIC')
PREMIUM_PIC = os.environ.get('PREMIUM_PIC')
PREMIUM_PLAN_PIC = os.environ.get('PREMIUM_PLAN_PIC')

# Bot Deployment Limits per Premium Plan
BOT_DEPLOYMENT_LIMITS = {
    "Trial": 1,
    "Silver": 3,
    "Gold": 5,
    "Platinum": 10,
    "Diamond": 15,
}


def validate_config():
    """Validate essential configuration values.

    Returns a list of error strings (empty when valid).
    """
    errors: List[str] = []
    if not TELEGRAM_TOKEN:
        errors.append('TELEGRAM_TOKEN is missing')
    if not TELEGRAM_API_ID:
        errors.append('TELEGRAM_API_ID is missing')
    else:
        try:
            int(TELEGRAM_API_ID)
        except Exception:
            errors.append('TELEGRAM_API_ID must be an integer')
    if not TELEGRAM_API_HASH:
        errors.append('TELEGRAM_API_HASH is missing')

    # OWNER_IDS can be empty but warn
    if not OWNER_IDS:
        errors.append('OWNER_IDS is empty — set OWNER_ID env var if needed')

    return errors
