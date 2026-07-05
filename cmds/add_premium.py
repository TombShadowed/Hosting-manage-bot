"""Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb"""

from pyrogram import Client, filters
from core.manager import BotManager
from datetime import datetime, timedelta
from core.rate_limit import rate_limit


def parse_duration(duration_str: str) -> datetime:
    duration_str = duration_str.lower().strip()
    now = datetime.now()
    
    try:
        if 'day' in duration_str:
            days = int(duration_str.replace('day', '').replace('s', '').strip())
            return now + timedelta(days=days)
        elif 'month' in duration_str:
            months = int(duration_str.replace('month', '').replace('s', '').strip())
            return now + timedelta(days=months * 30)
        elif 'year' in duration_str:
            years = int(duration_str.replace('year', '').replace('s', '').strip())
            return now + timedelta(days=years * 365)
        elif 'hour' in duration_str:
            hours = int(duration_str.replace('hour', '').replace('s', '').strip())
            return now + timedelta(hours=hours)
        else:
            return None
    except ValueError:
        return None


PREMIUM_CATEGORIES = {
    'silver': 'sɪʟᴠᴇʀ',
    'gold': 'ɢᴏʟᴅ',
    'diamond': 'ᴅɪᴀᴍᴏɴᴅ',
    'platinum': 'ᴘʟᴀᴛɪɴᴜᴍ '
}


async def add_premium_handler(client: Client, message, manager: BotManager, owner_ids: list):
    if message.from_user.id not in owner_ids:
        await message.reply("<blockquote><b>ᴏᴡɴᴇʀ ᴏɴʟʏ</b></blockquote>")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            categories = ', '.join(PREMIUM_CATEGORIES.keys())
            await message.reply(f"<blockquote><b>ᴜsᴀɢᴇ:</b> /add_premium &lt;telegram_id&gt; [category] [duration]\n\n"
                              f"<b>ᴄᴀᴛᴇɢᴏʀɪᴇs:</b> {categories}\n"
                              f"<b>ᴅᴜʀᴀᴛɪᴏɴ:</b> 1day, 7days, 1month, 1year, or 24hour\n"
                              f"<b>ᴇxᴀᴍᴘʟᴇ:</b> /add_premium 778855533 silver 1day</blockquote>")
            return

        tg_id = int(parts[1])
        category = parts[2].lower() if len(parts) > 2 else 'silver'
        duration_str = parts[3] if len(parts) > 3 else None
        
        if category not in PREMIUM_CATEGORIES:
            await message.reply(f"<blockquote expandable><b>ɪɴᴠᴀʟɪᴅ ᴄᴀᴛᴇɢᴏʀʏ.</b> ᴀᴠᴀɪʟᴀʙʟᴇ: {', '.join(PREMIUM_CATEGORIES.keys())}</blockquote expandable>")
            return
        
        expires_at = None
        if duration_str:
            expires_at_dt = parse_duration(duration_str)
            if not expires_at_dt:
                await message.reply("<blockquote><b>ɪɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ.</b> ᴜsᴇ: 1day, 7days, 1month, 1year, 24hour</blockquote>")
                return
            expires_at = expires_at_dt.isoformat()
        
        manager.storage.add_premium_user(tg_id, category, expires_at)
        
        exp_text = f" (expires {expires_at[:10]})" if expires_at else " (lifetime)"
        await message.reply(f"<blockquote><b>ᴜsᴇʀ {tg_id} ᴀᴅᴅᴇᴅ ᴛᴏ {PREMIUM_CATEGORIES[category]}{exp_text}</b></blockquote>")
    except ValueError:
        await message.reply("<b><blockquote>ɪɴᴠᴀʟɪᴅ ᴛᴇʟᴇɢʀᴀᴍ ID</blockquote></b>")
    except Exception as e:
        await message.reply(f"<b>Error:</b> {str(e)}")


def init(app: Client, manager: BotManager, owner_ids: list):
    @app.on_message(filters.command('add_premium'))
    @rate_limit(2.0)
    async def _add_premium(client: Client, message):
        await add_premium_handler(client, message, manager, owner_ids)

