"""Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb"""

from pyrogram import filters


def init(app, manager, OWNER_IDS):
    @app.on_message(filters.command('admins'))
    async def list_admins_cmd(client, message):
        uid = message.from_user.id
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        if uid not in OWNER_IDS and uid not in admins:
            await message.reply_text('<b><blockquote>ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ</b></blockquote>')
            return
        await message.reply_text(
            '<b><blockquote>✦ 𝗔𝗗𝗠𝗜𝗡 𝗟𝗜𝗦𝗧</blockquote>\n<blockquote>ᴏᴡɴᴇʀ: ' 
            + ','.join(str(x) for x in OWNER_IDS) 
            + '\nᴀᴅᴍɪɴs: ' 
            + ','.join(str(x) for x in admins)
            + '</b></blockquote>'
        )
