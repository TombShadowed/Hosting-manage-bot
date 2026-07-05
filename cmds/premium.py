# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from config import PREMIUM_PIC, PREMIUM_PLAN_PIC

PREMIUM_TEXT = '''<b><blockquote>✦ 𝗛𝗢𝗦𝗧𝗜𝗡𝗚 𝗣𝗟𝗔𝗡 & 𝗣𝗥𝗜𝗖𝗘𝗦</blockquote>
<blockquote>≡ ᴅᴜʀᴀᴛɪᴏɴ & ᴄᴏsᴛ</blockquote>
────────────────────
<blockquote>›› sɪʟᴠᴇʀ : ₹55 / 30 ᴅᴀʏs  
›› ɢᴏʟᴅ : ₹120 / 30 ᴅᴀʏs  
›› ᴘʟᴀᴛɪɴᴜᴍ : ₹300 / 30 ᴅᴀʏs  
›› ᴅɪᴀᴍᴏɴᴅ : ₹380 / 30 ᴅᴀʏs</blockquote>
────────────────────
<blockquote>✦ 𝗕𝗢𝗧 𝗗𝗘𝗣𝗟𝗢𝗬𝗠𝗘𝗡𝗧 𝗟𝗜𝗠𝗜𝗧𝗦</blockquote>
• sɪʟᴠᴇʀ : 2 ʙᴏᴛs
• ɢᴏʟᴅ : 5 ʙᴏᴛs
• ᴘʟᴀᴛɪɴᴜᴍ : 8 ʙᴏᴛs
• ᴅɪᴀᴍᴏɴᴅ : 12 ʙᴏᴛs

<blockquote>≡ ᴀғᴛᴇʀ sᴇʟᴇᴄᴛɪɴɢ ʏᴏᴜʀ ᴘʟᴀɴ, ᴄʟɪᴄᴋ ᴛʜᴇ ᴘʀᴇᴍɪᴜᴍ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀᴋᴇ ʏᴏᴜʀ ᴘᴀʏᴍᴇɴᴛ!</blockquote></b>'''

def init(app, manager, OWNER_IDS):
    @app.on_message(filters.command(['premium', 'plan']))
    async def premium_cmd(client, message):
        text = PREMIUM_TEXT

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton('ᴘʀᴇᴍɪᴜᴍ', callback_data='premium_upgrade'),
            InlineKeyboardButton('Cʟᴏsᴇ', callback_data='premium_close')]
        ])

        if PREMIUM_PIC:
            await message.reply_photo(PREMIUM_PIC, caption=text, reply_markup=keyboard)
        else:
            await message.reply_text(text, disable_web_page_preview=True, reply_markup=keyboard)

    @app.on_callback_query(filters.regex(r'^premium_'))
    async def _premium_callbacks(client, callback_query):
        data = callback_query.data or ''
        await callback_query.answer()

        if data == 'premium_close':
            try:
                await callback_query.message.delete()
            except Exception:
                pass
            return

        if data == 'premium_upgrade':
            upgrade_text = '''<b><blockquote>✦ 𝗛𝗢𝗦𝗧𝗜𝗡𝗚 𝗣𝗟𝗔𝗡 & 𝗣𝗥𝗜𝗖𝗘𝗦</blockquote>
────────────────────
<blockquote>›› sɪʟᴠᴇʀ : ₹95 / 30 ᴅᴀʏs  
›› ɢᴏʟᴅ : ₹180 / 30 ᴅᴀʏs  
›› ᴘʟᴀᴛɪɴᴜᴍ : ₹360 / 30 ᴅᴀʏs  
›› ᴅɪᴀᴍᴏɴᴅ : ₹440 / 30 ᴅᴀʏs</blockquote>
────────────────────
<blockquote>✦ 𝗕𝗢𝗧 𝗗𝗘𝗣𝗟𝗢𝗬𝗠𝗘𝗡𝗧 𝗟𝗜𝗠𝗜𝗧𝗦</blockquote>
• sɪʟᴠᴇʀ : 2 ʙᴏᴛs
• ɢᴏʟᴅ : 5 ʙᴏᴛs
• ᴘʟᴀᴛɪɴᴜᴍ : 8 ʙᴏᴛs
• ᴅɪᴀᴍᴏɴᴅ : 12 ʙᴏᴛs
────────────────────
<blockquote>›› Pʀᴇᴍɪᴜᴍ ᴡɪʟʟ ʙᴇ ᴀᴅᴅᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴏɴᴄᴇ ᴘᴀɪᴅ</blockquote>
<blockquote>›› 𝗔𝗙𝗧𝗘𝗥 𝗣𝗔𝗬𝗠𝗘𝗡𝗧:</blockquote>
<blockquote>≡ Sᴇɴᴅ ᴀ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ & ᴡᴀɪᴛ ғᴏʀ ᴀᴄᴛɪᴠᴀᴛɪᴏɴ ✓</b></blockquote>'''
            plan_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton('• sɪʟᴠᴇʀ •', callback_data='premium_plan_silver'),
                InlineKeyboardButton('• ɢᴏʟᴅ •', callback_data='premium_plan_gold')],
                [InlineKeyboardButton('• ᴘʟᴀᴛɪɴᴜᴍ •', callback_data='premium_plan_platinum'),
                InlineKeyboardButton('• ᴅɪᴀᴍᴏɴᴅ •', callback_data='premium_plan_diamond')],
                [InlineKeyboardButton('✦ Cᴜsᴛᴏᴍ Pʟᴀɴ ✦', url='https://t.me/ShadowedTomb')],
                [InlineKeyboardButton('‹ Back', callback_data='premium_back')]
            ])
            try:
                if PREMIUM_PLAN_PIC:
                    await callback_query.message.edit_media(
                        InputMediaPhoto(PREMIUM_PLAN_PIC, caption=upgrade_text),
                        reply_markup=plan_keyboard
                    )
                else:
                    await callback_query.message.edit_text(
                        upgrade_text,
                        disable_web_page_preview=True,
                        reply_markup=plan_keyboard
                    )
            except Exception:
                try:
                    await callback_query.message.delete()
                except Exception:
                    pass
                chat_id = callback_query.message.chat.id
                if PREMIUM_PLAN_PIC:
                    await client.send_photo(
                        chat_id,
                        PREMIUM_PLAN_PIC,
                        caption=upgrade_text,
                        reply_markup=plan_keyboard
                    )
                else:
                    await client.send_message(
                        chat_id,
                        upgrade_text,
                        disable_web_page_preview=True,
                        reply_markup=plan_keyboard
                    )
            return


        if data.startswith('premium_plan_'):
            plan_name = data.replace('premium_plan_', '').upper()
            plan_details = {
                'SILVER': {'price': '₹95', 'bots': '2', 'days': '30'},
                'GOLD': {'price': '₹180', 'bots': '5', 'days': '30'},
                'PLATINUM': {'price': '₹360', 'bots': '8', 'days': '30'},
                'DIAMOND': {'price': '₹440', 'bots': '12', 'days': '30'},
            }
            plan_info = plan_details.get(plan_name, {})
            plan_text = f'''<b>𝗬𝗢𝗨 𝗦𝗘𝗟𝗘𝗖𝗧𝗘𝗗: {plan_name}</b>

<b>Price:</b> {plan_info.get('price', 'N/A')}
<b>Duration:</b> {plan_info.get('days', '30')} days
<b>Bot Slots:</b> {plan_info.get('bots', 'N/A')} bots

<blockquote>ᴘʟᴇᴀsᴇ ᴘᴀʏ ᴛʜɪs ᴀᴍᴏᴜɴᴛ ᴛᴏ ᴛʜᴇ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴀɴᴅ ᴛʜᴇɴ sᴇɴᴅ ᴀ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ᴏғ ᴛʜᴇ ᴩᴀʏᴍᴇɴᴛ ғᴏʀ ᴀᴄᴛɪᴠᴀᴛɪᴏɴ.</blockquote>'''
            back_kb = InlineKeyboardMarkup([[InlineKeyboardButton('‹ Back', callback_data='premium_upgrade'), InlineKeyboardButton('Cʟᴏsᴇ', callback_data='premium_close')]])
            try:
                await callback_query.message.edit_text(plan_text, disable_web_page_preview=True, reply_markup=back_kb)
            except Exception:
                try:
                    await callback_query.message.delete()
                except Exception:
                    pass
                await client.send_message(callback_query.message.chat.id, plan_text, disable_web_page_preview=True, reply_markup=back_kb)

        if data == 'premium_back':
            text = PREMIUM_TEXT
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton('ᴘʀᴇᴍɪᴜᴍ', callback_data='premium_upgrade'),
                InlineKeyboardButton('Cʟᴏsᴇ', callback_data='premium_close')]
            ])
            try:
                await callback_query.message.edit_text(text, disable_web_page_preview=True, reply_markup=keyboard)
            except Exception:
                try:
                    await callback_query.message.delete()
                except Exception:
                    pass
                chat_id = callback_query.message.chat.id
                if PREMIUM_PIC:
                    await client.send_photo(chat_id, PREMIUM_PIC, caption=text, reply_markup=keyboard)
                else:
                    await client.send_message(chat_id, text, disable_web_page_preview=True, reply_markup=keyboard)
