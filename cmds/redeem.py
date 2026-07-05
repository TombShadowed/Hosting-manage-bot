# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_IDS
from datetime import datetime, timedelta


def init(app, manager, OWNER_IDS):
    @app.on_message(filters.command('redeem'))
    async def redeem(client, message):
        uid = message.from_user.id
        args = message.text.split()
        
        if len(args) < 2:
            await message.reply_text(
                '<b><blockquote>𝗥𝗘𝗗𝗘𝗘𝗠 𝗣𝗟𝗔𝗡\n\n'
                '<b>Usage:</b> /redeem <code>\n\n'
                '<b>Example:</b>\n'
                '• /redeem ABC1234567</b></blockquote>'
            )
            return
        
        code = args[1].upper()
        
        # Check if code exists
        code_data = manager.storage.get_redeem_code(code)
        if not code_data:
            await message.reply_text(
                '<b><blockquote>❌ ɪɴᴠᴀʟɪᴅ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ\n\n'
                'The code you provided is invalid or has expired.</b></blockquote>'
            )
            return
        
        # Try to use the code
        success = manager.storage.use_redeem_code(code, uid)
        
        if not success:
            # Code was either already used by this user or limit reached
            used_by = code_data.get('used_by', [])
            user_limit = code_data.get('user_limit', 1)
            
            if uid in used_by:
                await message.reply_text(
                    '<b><blockquote>⚠️ ᴀʟʀᴇᴀᴅʏ ᴜsᴇᴅ\n\n'
                    'You have already redeemed this code.</b></blockquote>'
                )
            elif len(used_by) >= user_limit:
                await message.reply_text(
                    '<b><blockquote>⚠️ ᴄᴏᴅᴇ ᴇxʜᴀᴜsᴛᴇᴅ\n\n'
                    f'This code has been used {len(used_by)}/{user_limit} times.'
                    '</b></blockquote>'
                )
            return
        
        # Code was successfully used, now apply the plan
        plan = code_data.get('plan', 'Silver')
        duration_days = code_data.get('duration_days', 30)
        
        # Calculate expiry date
        expires_at = (datetime.now() + timedelta(days=duration_days)).isoformat()
        
        # Add the premium plan to user
        manager.storage.add_premium_user(uid, category=plan, expires_at=expires_at)
        
        # Send success message
        await message.reply_text(
            '<b><blockquote>✅ ᴘʟᴀɴ ᴀᴄᴛɪᴠᴀᴛᴇᴅ\n\n'
            f'🎉 Congratulations! Your <b>{plan}</b> plan is now active!\n\n'
            f'⏰ Expires: <b>{duration_days} days</b> from now\n\n'
            f'You can now use /register to deploy bots.</b></blockquote>'
        )
