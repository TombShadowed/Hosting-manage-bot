# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from config import START_PIC, ABOUT_PIC, TERMS_PIC


def init(app, manager, OWNER_IDS):
    def _build_start():
        text = ('<b><blockquote>✦ 𝗢𝗫𝗜𝗙𝗬 𝗛𝗢𝗦𝗧𝗜𝗡𝗚</blockquote></b>\n'
                '<blockquote>➥ 𝗛𝗘𝗬 𝗧𝗛𝗘𝗥𝗘! 𝗜 𝗔𝗠 𝗬𝗢𝗨𝗥 𝗦𝗠𝗢𝗢𝗧𝗛 𝗔𝗡𝗗 𝗥𝗘𝗟𝗜𝗔𝗕𝗟𝗘 𝗕𝗢𝗧-𝗛𝗢𝗦𝗧𝗜𝗡𝗚 𝗣𝗔𝗥𝗧𝗡𝗘𝗥, 𝗗𝗘𝗦𝗜𝗚𝗡𝗘𝗗 𝗧𝗢 𝗗𝗘𝗣𝗟𝗢𝗬 𝗔𝗡𝗗 𝗠𝗔𝗡𝗔𝗚𝗘 𝗬𝗢𝗨𝗥 𝗕𝗢𝗧𝗦 𝗪𝗜𝗧𝗛 𝗘𝗔𝗦𝗘.\n'
                '𝗝𝗨𝗦𝗧 𝗨𝗦𝗘 /𝗕𝗢𝗧𝗦 𝗔𝗡𝗗 𝗚𝗘𝗧 𝗬𝗢𝗨𝗥 𝗕𝗢𝗧 𝗟𝗜𝗩𝗘 𝗜𝗡 𝗦𝗘𝗖𝗢𝗡𝗗𝗦!</blockquote>\n'
                '━━━━━━━━━━━━━━━━━━\n'
                '<blockquote><b>≡ 𝗣𝗨𝗥𝗣𝗢𝗦𝗘: 𝗗𝗘𝗣𝗟𝗢𝗬, 𝗛𝗢𝗦𝗧 𝗔𝗡𝗗 𝗠𝗔𝗡𝗔𝗚𝗘 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠 𝗕𝗢𝗧𝗦 𝗪𝗜𝗧𝗛 𝗭𝗘𝗥𝗢 𝗛𝗔𝗦𝗦𝗟𝗘.\n'
            '≡ 𝗠𝗔𝗡𝗔𝗚𝗘𝗗 𝗕𝗬: <a href="https://t.me/ShadowedTomb">Name Huh</a></b></blockquote>')

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('◉ 𝗔𝗕𝗢𝗨𝗧', callback_data='start_about'),
                    InlineKeyboardButton('✖ 𝗖𝗟𝗢𝗦𝗘', callback_data='start_close'),
                ],
                [InlineKeyboardButton('☰ 𝗧𝗘𝗥𝗠𝗦', callback_data='start_terms')]
            ]
        )
        return text, keyboard

    @app.on_message(filters.command('start'))
    async def start_cmd(client, message):
        text, keyboard = _build_start()

        if START_PIC:
            await message.reply_photo(START_PIC, caption=text, reply_markup=keyboard)
            return

        await message.reply_text(text, disable_web_page_preview=True, reply_markup=keyboard)

    @app.on_callback_query(filters.regex(r'^start_'))
    async def _start_callbacks(client, callback_query):
        data = callback_query.data or ''
        await callback_query.answer()

        if data == 'start_close':
            try:
                await callback_query.message.delete()
            except Exception:
                pass
            return

        if data == 'start_back':
            text, keyboard = _build_start()
            try:
                if START_PIC:
                    try:
                        await callback_query.message.edit_media(InputMediaPhoto(START_PIC, caption=text), reply_markup=keyboard)
                    except Exception:
                        await callback_query.message.edit_text(text, disable_web_page_preview=True, reply_markup=keyboard)
                else:
                    await callback_query.message.edit_text(text, disable_web_page_preview=True, reply_markup=keyboard)
            except Exception:
                try:
                    await callback_query.message.delete()
                except Exception:
                    pass
                chat_id = callback_query.message.chat.id
                if START_PIC:
                    await client.send_photo(chat_id, START_PIC, caption=text, reply_markup=keyboard)
                else:
                    await client.send_message(chat_id, text, disable_web_page_preview=True, reply_markup=keyboard)
            return

        if data == 'start_about':
            about_text = '''<b><blockquote>◉ ᴀʙᴏᴜᴛ ᴍᴇ</blockquote></b>
≡ 𝗡𝗔𝗠𝗘: <a href="https://t.me/Oxigenbot">Oxigen</a>
≡ 𝗨𝗣𝗗𝗔𝗧𝗘𝗦: <a href="https://t.me/ShadowedTomb">Name Huh</a>
≡ 𝗦𝗨𝗣𝗣𝗢𝗥𝗧: <a href="https://t.me/ShadowedTomb">𝗛𝗢𝗦𝗧-𝗦𝗨𝗣𝗣𝗢𝗥𝗧</a>
≡ 𝗗𝗘𝗩𝗘𝗟𝗢𝗣𝗘𝗥: <a href="https://t.me/ShadowedTomb">Name Huh</a> • <a href="https://t.me/name_huh">𝗡𝗔𝗠𝗘_𝗛𝗨𝗛</a>
≡ 𝗗𝗔𝗧𝗔𝗕𝗔𝗦𝗘: <a href="https://www.mongodb.com/">𝗠𝗢𝗡𝗚𝗢 𝗗𝗕</a>
≡ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬: <a href="https://t.me/ShadowedTomb">𝗕𝗢𝗧 𝗛𝗢𝗦𝗧𝗜𝗡𝗚</a>

<blockquote>›› 𝗜 𝗔𝗠 𝗔 𝗣𝗢𝗪𝗘𝗥𝗙𝗨𝗟 𝗬𝗘𝗧 𝗦𝗜𝗠𝗣𝗟𝗘 𝗛𝗢𝗦𝗧𝗜𝗡𝗚 𝗕𝗢𝗧 𝗕𝗨𝗜𝗟𝗧 𝗧𝗢 𝗠𝗔𝗞𝗘 𝗗𝗘𝗣𝗟𝗢𝗬𝗠𝗘𝗡𝗧 𝗙𝗔𝗦𝗧, 𝗦𝗠𝗢𝗢𝗧𝗛, 𝗔𝗡𝗗 𝗥𝗘𝗟𝗜𝗔𝗕𝗟𝗘.</blockquote></b>'''
            kb = InlineKeyboardMarkup([[InlineKeyboardButton('◀ 𝗕𝗔𝗖𝗞', callback_data='start_back'), InlineKeyboardButton('✖ 𝗖𝗟𝗢𝗦𝗘', callback_data='start_close')]])
            try:
                if ABOUT_PIC:
                    await callback_query.message.edit_media(InputMediaPhoto(ABOUT_PIC, caption=about_text), reply_markup=kb)
                else:
                    await callback_query.message.edit_text(about_text, disable_web_page_preview=True, reply_markup=kb)
            except Exception:
                if ABOUT_PIC:
                    await callback_query.message.reply_photo(ABOUT_PIC, caption=about_text, reply_markup=kb)
                else:
                    await callback_query.message.reply_text(about_text, disable_web_page_preview=True, reply_markup=kb)
            return

        if data == 'start_terms':
            terms_text = '''<blockquote>✦ 𝗧𝗘𝗥𝗠𝗦 𝗢𝗙 𝗦𝗘𝗥𝗩𝗜𝗖𝗘</blockquote>
<blockquote>❐ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗢𝗫𝗜𝗙𝗬, 𝗔 𝗣𝗟𝗔𝗧𝗙𝗢𝗥𝗠 𝗗𝗘𝗦𝗜𝗚𝗡𝗘𝗗 𝗧𝗢 𝗠𝗔𝗞𝗘 𝗕𝗢𝗧 𝗗𝗘𝗣𝗟𝗢𝗬𝗠𝗘𝗡𝗧 𝗔𝗡𝗗 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧 𝗦𝗜𝗠𝗣𝗟𝗘, 𝗙𝗔𝗦𝗧, 𝗔𝗡𝗗 𝗥𝗘𝗟𝗜𝗔𝗕𝗟𝗘. 𝗕𝗬 𝗨𝗦𝗜𝗡𝗚 𝗢𝗨𝗥 𝗦𝗘𝗥𝗩𝗜𝗖𝗘, 𝗬𝗢𝗨 𝗔𝗚𝗥𝗘𝗘 𝗧𝗢 𝗢𝗨𝗥 𝗨𝗦𝗔𝗚𝗘 𝗥𝗨𝗟𝗘𝗦 𝗔𝗡𝗗 𝗖𝗢𝗡𝗗𝗜𝗧𝗜𝗢𝗡𝗦.</blockquote>
<blockquote>✦ 𝗗𝗔𝗧𝗔 𝗣𝗥𝗜𝗩𝗔𝗖𝗬</blockquote>
<blockquote>❐ 𝗪𝗘 𝗖𝗢𝗟𝗟𝗘𝗖𝗧 𝗢𝗡𝗟𝗬 𝗠𝗜𝗡𝗜𝗠𝗔𝗟 𝗗𝗔𝗧𝗔 𝗦𝗨𝗖𝗛 𝗔𝗦 𝗬𝗢𝗨𝗥 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠 𝗨𝗦𝗘𝗥 𝗜𝗗, 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘, 𝗔𝗡𝗗 𝗕𝗢𝗧 𝗗𝗘𝗣𝗟𝗢𝗬𝗠𝗘𝗡𝗧 𝗗𝗘𝗧𝗔𝗜𝗟𝗦. 𝗡𝗢 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗖𝗢𝗗𝗘 𝗢𝗥 𝗣𝗘𝗥𝗦𝗢𝗡𝗔𝗟 𝗗𝗔𝗧𝗔 𝗜𝗦 𝗦𝗛𝗔𝗥𝗘𝗗.</blockquote>
≡ <a href="https://t.me/ShadowedTomb">𝗥𝗘𝗔𝗗 𝗠𝗢𝗥𝗘</a> • <a href="https://t.me/ShadowedTomb">𝗥𝗘𝗔𝗗 𝗢𝗡 𝗧𝗚</a>
            '''

            kb = InlineKeyboardMarkup([[InlineKeyboardButton('◀ 𝗕𝗔𝗖𝗞', callback_data='start_back'), InlineKeyboardButton('✖ 𝗖𝗟𝗢𝗦𝗘', callback_data='start_close')]])
            try:
                if TERMS_PIC:
                    await callback_query.message.edit_media(InputMediaPhoto(TERMS_PIC, caption=terms_text), reply_markup=kb)
                else:
                    await callback_query.message.edit_text(terms_text, disable_web_page_preview=True, reply_markup=kb)
            except Exception:
                if TERMS_PIC:
                    await callback_query.message.reply_photo(TERMS_PIC, caption=terms_text, reply_markup=kb)
                else:
                    await callback_query.message.reply_text(terms_text, disable_web_page_preview=True, reply_markup=kb)
