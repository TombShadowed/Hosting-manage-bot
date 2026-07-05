"""Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb"""

from pyrogram import filters
from core.rate_limit import rate_limit


def init(app, manager, OWNER_IDS):
    @app.on_message(filters.command('addadmin'))
    @rate_limit(1.0)
    async def add_admin_cmd(client, message):
        uid = message.from_user.id
        if uid not in OWNER_IDS:
            await message.reply_text('<b><blockquote>◉ 𝗢𝗪𝗡𝗘𝗥-𝗢𝗡𝗟𝗬 𝗖𝗢𝗠𝗠𝗔𝗡𝗗</blockquote></b>')
            return
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text('<b><blockquote>◉ 𝗨𝗦𝗔𝗚𝗘: /addadmin [telegram_id]</blockquote></b>')
            return
        try:
            tid = int(args[1])
            manager.storage.add_admin(tid)
            await message.reply_text(f'<b><blockquote>✓ 𝗔𝗗𝗗𝗘𝗗 𝗔𝗗𝗠𝗜𝗡: {tid}</blockquote></b>')
        except Exception as e:
            await message.reply_text(f'<b><blockquote>✖ 𝗘𝗥𝗥𝗢𝗥: {str(e)}</blockquote></b>')
