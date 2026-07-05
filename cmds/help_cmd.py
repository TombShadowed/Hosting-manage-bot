# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import HELP_PIC


def init(app, manager, OWNER_IDS):
    @app.on_message(filters.command('help'))
    async def help_cmd(client, message):
        text = '''<b><blockquote>✦ 𝗛𝗢𝗦𝗧𝗜𝗙𝗬 𝗛𝗘𝗟𝗣 𝗚𝗨𝗜𝗗𝗘</blockquote></b>
<blockquote>➥ 𝗧𝗢 𝗗𝗘𝗣𝗟𝗢𝗬 𝗔 𝗕𝗢𝗧:
≡ 𝗨𝗦𝗘 /𝗕𝗢𝗧𝗦 𝗧𝗢 𝗢𝗣𝗘𝗡 𝗧𝗛𝗘 𝗛𝗢𝗦𝗧𝗜𝗡𝗚 𝗣𝗔𝗡𝗘𝗟
≡ 𝗖𝗟𝗜𝗖𝗞 “𝗔𝗗𝗗 𝗡𝗘𝗪 𝗕𝗢𝗧𝗦” 𝗧𝗢 𝗦𝗧𝗔𝗥𝗧 𝗗𝗘𝗣𝗟𝗢𝗬𝗠𝗘𝗡𝗧
≡ 𝗣𝗥𝗢𝗩𝗜𝗗𝗘 𝗧𝗛𝗘 𝗕𝗢𝗧 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘, 𝗚𝗜𝗧 𝗥𝗘𝗣𝗢 𝗨𝗥𝗟, 𝗔𝗡𝗗 𝗠𝗔𝗜𝗡 𝗙𝗜𝗟𝗘 𝗡𝗔𝗠𝗘
≡ 𝗬𝗢𝗨𝗥 𝗕𝗢𝗧 𝗪𝗜𝗟𝗟 𝗕𝗘 𝗗𝗘𝗣𝗟𝗢𝗬𝗘𝗗 𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗖𝗔𝗟𝗟𝗬</blockquote>
<blockquote>➥ 𝗧𝗢 𝗠𝗔𝗡𝗔𝗚𝗘 𝗬𝗢𝗨𝗥 𝗕𝗢𝗧𝗦:
• 𝗩𝗜𝗘𝗪 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗖𝗛𝗘𝗖𝗞 𝗜𝗙 𝗬𝗢𝗨𝗥 𝗕𝗢𝗧𝗦 𝗔𝗥𝗘 𝗥𝗨𝗡𝗡𝗜𝗡𝗚 𝗢𝗥 𝗦𝗧𝗢𝗣𝗣𝗘𝗗
• 𝗥𝗘𝗦𝗧𝗔𝗥𝗧: 𝗥𝗘𝗙𝗥𝗘𝗦𝗛 𝗬𝗢𝗨𝗥 𝗕𝗢𝗧 𝗜𝗡 𝗢𝗡𝗘 𝗧𝗔𝗣
• 𝗦𝗧𝗢𝗣: 𝗦𝗧𝗢𝗣 𝗔 𝗕𝗢𝗧 𝗪𝗛𝗘𝗡 𝗬𝗢𝗨 𝗡𝗘𝗘𝗗 𝗧𝗢
• 𝗥𝗘𝗠𝗢𝗩𝗘: 𝗗𝗘𝗟𝗘𝗧𝗘 𝗔 𝗕𝗢𝗧 𝗙𝗥𝗢𝗠 𝗧𝗛𝗘 𝗦𝗘𝗥𝗩𝗜𝗖𝗘</blockquote>
<blockquote>➥ 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗘𝗡𝗘𝗙𝗜𝗧𝗦:
• 𝗗𝗘𝗣𝗟𝗢𝗬 𝗠𝗨𝗟𝗧𝗜𝗣𝗟𝗘 𝗕𝗢𝗧𝗦 𝗔𝗧 𝗢𝗡𝗖𝗘
• 𝗔𝗨𝗧𝗢 𝗥𝗘𝗦𝗧𝗔𝗥𝗧𝗦 𝗔𝗡𝗗 𝗠𝗢𝗡𝗜𝗧𝗢𝗥𝗜𝗡𝗚
• 𝗛𝗜𝗚𝗛𝗘𝗥 𝗥𝗘𝗦𝗢𝗨𝗥𝗖𝗘 𝗔𝗟𝗟𝗢𝗖𝗔𝗧𝗜𝗢𝗡</blockquote>
≡ 𝗡𝗘𝗘𝗗 𝗔 𝗛𝗔𝗡𝗗? 𝗥𝗘𝗔𝗖𝗛 𝗢𝗨𝗧 𝗧𝗛𝗥𝗢𝗨𝗚𝗛 𝗧𝗛𝗘 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗔𝗕𝗢𝗩𝗘.</b>'''

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton('◉ 𝗦𝗨𝗣𝗣𝗢𝗥𝗧', url='https://t.me/ShadowedTomb')],
            [
                InlineKeyboardButton('◌ 𝗨𝗣𝗗𝗔𝗧𝗘𝗦', url='https://t.me/ShadowedTomb'),
                InlineKeyboardButton('◌ 𝗗𝗘𝗩', url='https://t.me/ShadowedTomb'),
            ]
        ])

        if HELP_PIC:
            await message.reply_photo(HELP_PIC, caption=text, reply_markup=keyboard)
        else:
            await message.reply_text(text, disable_web_page_preview=True, reply_markup=keyboard)
