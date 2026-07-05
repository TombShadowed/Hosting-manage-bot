# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

from pyrogram import filters


def init(app, manager, OWNER_IDS):
    @app.on_message(filters.command('remove'))
    async def remove(client, message):
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
            await message.reply_text('<b><blockquote>◉ 𝗨𝗦𝗔𝗚𝗘\n\n/remove <name></blockquote></b>')
            return
        name = args[1]
        try:
            manager.delete_bot(name)
            await message.reply_text(f'<b><blockquote>✓ 𝗕𝗢𝗧 𝗥𝗘𝗠𝗢𝗩𝗘𝗗\n\n{name} 𝗛𝗔𝗦 𝗕𝗘𝗘𝗡 𝗥𝗘𝗠𝗢𝗩𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬.</blockquote></b>')
        except Exception as e:
            await message.reply_text(f'<b><blockquote>✖ 𝗘𝗥𝗥𝗢𝗥\n\n{str(e)}</blockquote></b>')
