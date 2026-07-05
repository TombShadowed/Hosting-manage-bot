# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

from pyrogram import filters
import json


def init(app, manager, OWNER_IDS):
    @app.on_message(filters.command('status'))
    async def status_cmd(client, message):
        uid = message.from_user.id
        try:
            admins = manager.get_admins()
        except Exception:
            admins = []
        if uid not in admins and uid not in OWNER_IDS:
            await message.reply_text('<b><blockquote>◉ 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗\n\n𝗬𝗢𝗨 𝗗𝗢 𝗡𝗢𝗧 𝗛𝗔𝗩𝗘 𝗣𝗘𝗥𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗧𝗢 𝗨𝗦𝗘 𝗧𝗛𝗜𝗦 𝗖𝗢𝗠𝗠𝗔𝗡𝗗.</blockquote></b>')
            return
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text('<b><blockquote>◉ 𝗨𝗦𝗔𝗚𝗘\n\n/status <name></blockquote></b>')
            return
        name = args[1]
        meta = manager.storage.get_bot(name)
        if not meta:
            await message.reply_text('<b><blockquote>✖ 𝗕𝗢𝗧 𝗡𝗢𝗧 𝗙𝗢𝗨𝗡𝗗\n\n𝗡𝗢 𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥𝗘𝗗 𝗕𝗢𝗧 𝗠𝗔𝗧𝗖𝗛𝗘𝗦 𝗧𝗛𝗔𝗧 𝗡𝗔𝗠𝗘.</blockquote></b>')
            return
        await message.reply_text(f'<b><blockquote>◉ 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗨𝗦\n\n<code>{json.dumps(meta, indent=2)}</code></blockquote></b>')
