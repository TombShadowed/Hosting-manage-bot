# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

from pyrogram import Client, filters
from core.manager import BotManager
from datetime import datetime


PREMIUM_CATEGORIES = {
    'silver': '🥈 Silver',
    'gold': '🥇 Gold',
    'diamond': '💎 Diamond',
    'platinum': '🏆 Platinum'
}


async def premium_users_handler(client: Client, message, manager: BotManager, owner_ids: list):
    if message.from_user.id not in owner_ids:
        await message.reply("❌ <b>Owner only</b>")
        return

    try:
        premium_data = manager.storage.get_premium_users()
        if not premium_data:
            await message.reply("📭 <b>No premium users yet</b>")
            return

        text = "<b>👑 Premium Users</b>\n\n"
        now = datetime.now()
        
        for idx, (user_id, user_info) in enumerate(sorted(premium_data.items()), 1):
            category = user_info.get('category', 'unknown')
            category_label = PREMIUM_CATEGORIES.get(category, category.title())
            expires_at = user_info.get('expires_at')
            
            if expires_at:
                exp_dt = datetime.fromisoformat(expires_at)
                if exp_dt > now:
                    days_left = (exp_dt - now).days
                    text += f"{idx}. <code>{user_id}</code> • {category_label} • {days_left}d left\n"
                else:
                    text += f"{idx}. <code>{user_id}</code> • {category_label} • ⏰ EXPIRED\n"
            else:
                text += f"{idx}. <code>{user_id}</code> • {category_label} • ♾️ Lifetime\n"

        text += f"\n<b>Total:</b> {len(premium_data)}"
        await message.reply(text)
    except Exception as e:
        await message.reply(f"❌ <b>Error:</b> {str(e)}")


def init(app: Client, manager: BotManager, owner_ids: list):
    @app.on_message(filters.command('premium_users'))
    async def _premium_users(client: Client, message):
        await premium_users_handler(client, message, manager, owner_ids)
