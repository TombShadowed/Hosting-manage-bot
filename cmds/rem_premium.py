# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

from pyrogram import Client, filters
from core.manager import BotManager
from core.rate_limit import rate_limit


async def rem_premium_handler(client: Client, message, manager: BotManager, owner_ids: list):
    if message.from_user.id not in owner_ids:
        await message.reply("❌ <b>Owner only</b>")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("📝 <b>Usage:</b> /rem_premium &lt;telegram_id&gt;")
            return

        tg_id = int(parts[1])
        user = manager.storage.get_premium_user(tg_id)
        if not user:
            await message.reply(f"❌ <b>User {tg_id} is not premium</b>")
            return
            
        manager.storage.remove_premium_user(tg_id)
        await message.reply(f"✅ <b>User {tg_id} removed from {user.get('category', 'premium')}</b>")
    except ValueError:
        await message.reply("❌ <b>Invalid telegram ID</b>")
    except Exception as e:
        await message.reply(f"❌ <b>Error:</b> {str(e)}")


def init(app: Client, manager: BotManager, owner_ids: list):
    @app.on_message(filters.command('rem_premium'))
    @rate_limit(1.0)
    async def _rem_premium(client: Client, message):
        await rem_premium_handler(client, message, manager, owner_ids)
