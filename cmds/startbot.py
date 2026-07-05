# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

from pyrogram import filters


def init(app, manager, OWNER_IDS):
    @app.on_message(filters.command('startbot'))
    async def start_bot_cmd(client, message):
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
            await message.reply_text('<b><blockquote>◉ 𝗨𝗦𝗔𝗚𝗘\n\n/startbot <name></blockquote></b>')
            return
        name = args[1]
        try:
            res = manager.start(name)
            await message.reply_text(f'<b><blockquote>✓ 𝗕𝗢𝗧 𝗦𝗧𝗔𝗥𝗧𝗘𝗗\n\n{name} 𝗜𝗦 𝗡𝗢𝗪 𝗥𝗨𝗡𝗡𝗜𝗡𝗚. 𝗣𝗜𝗗: {res["pid"]}</blockquote></b>')
        except Exception as e:
            await message.reply_text(f'<b><blockquote>✖ 𝗘𝗥𝗥𝗢𝗥\n\n{str(e)}</blockquote></b>')
