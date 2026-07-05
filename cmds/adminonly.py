"""Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb"""
from pyrogram import Client, filters
 
from core.manager import BotManager


def init(app: Client, manager: BotManager, OWNER_IDS: list):
    @app.on_message(filters.command('adminonly'))
    async def adminonly_cmd(client: Client, message):
        uid = message.from_user.id
        # Only owner can use this command
        if uid not in OWNER_IDS:
            await message.reply_text('<b><blockquote>ᴏᴡɴᴇʀ-ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅ</b></blockquote>')
            return
        
        args = message.text.split()
        if len(args) < 2:
            current = manager.storage.get_admin_only()
            status = "◉ <b>𝗘𝗡𝗔𝗕𝗟𝗘𝗗</b>" if current else "◌ <b>𝗗𝗜𝗦𝗔𝗕𝗟𝗘𝗗</b>"
            help_text = (
                '<b><blockquote>◉ 𝗔𝗗𝗠𝗜𝗡 𝗢𝗡𝗟𝗬 𝗠𝗢𝗗𝗘\n\n'
                f'𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗦𝗧𝗔𝗧𝗨𝗦: {status}\n\n'
                '◈ 𝗪𝗛𝗘𝗡 𝗘𝗡𝗔𝗕𝗟𝗘𝗗:\n'
                '• 𝗢𝗡𝗟𝗬 𝗔𝗗𝗠𝗜𝗡𝗦 𝗖𝗔𝗡 𝗛𝗢𝗦𝗧 𝗕𝗢𝗧𝗦\n'
                '• 𝗥𝗘𝗚𝗨𝗟𝗔𝗥 𝗨𝗦𝗘𝗥𝗦 𝗖𝗔𝗡𝗡𝗢𝗧 𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥 𝗕𝗢𝗧𝗦\n\n'
                '◈ 𝗪𝗛𝗘𝗡 𝗗𝗜𝗦𝗔𝗕𝗟𝗘𝗗:\n'
                '• 𝗥𝗘𝗚𝗨𝗟𝗔𝗥 𝗨𝗦𝗘𝗥𝗦 𝗖𝗔𝗡 𝗛𝗢𝗦𝗧 𝗕𝗢𝗧𝗦\n'
                '• 𝗦𝗨𝗕𝗝𝗘𝗖𝗧 𝗧𝗢 𝗧𝗛𝗘𝗜𝗥 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗣𝗟𝗔𝗡 𝗟𝗜𝗠𝗜𝗧𝗦\n\n'
                '◉ 𝗨𝗦𝗔𝗚𝗘: /adminonly [true/false]</blockquote></b>'
            )
            await message.reply_text(help_text)
            return
        
        mode = args[1].lower()
        if mode in ['true', 'on', 'yes', '1']:
            manager.storage.set_admin_only(True)
            await message.reply_text(
                '<b><blockquote>✓ 𝗔𝗗𝗠𝗜𝗡-𝗢𝗡𝗟𝗬 𝗠𝗢𝗗𝗘 𝗘𝗡𝗔𝗕𝗟𝗘𝗗\n\n'
                '𝗢𝗡𝗟𝗬 𝗔𝗗𝗠𝗜𝗡𝗦 𝗖𝗔𝗡 𝗡𝗢𝗪 𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥 𝗕𝗢𝗧𝗦.</blockquote></b>'
            )
        elif mode in ['false', 'off', 'no', '0']:
            manager.storage.set_admin_only(False)
            await message.reply_text(
                '<b><blockquote>✓ 𝗔𝗗𝗠𝗜𝗡-𝗢𝗡𝗟𝗬 𝗠𝗢𝗗𝗘 𝗗𝗜𝗦𝗔𝗕𝗟𝗘𝗗\n\n'
                '𝗥𝗘𝗚𝗨𝗟𝗔𝗥 𝗨𝗦𝗘𝗥𝗦 𝗖𝗔𝗡 𝗡𝗢𝗪 𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥 𝗕𝗢𝗧𝗦 𝗕𝗔𝗦𝗘𝗗 𝗢𝗡 𝗧𝗛𝗘𝗜𝗥 𝗣𝗟𝗔𝗡.</blockquote></b>'
            )
