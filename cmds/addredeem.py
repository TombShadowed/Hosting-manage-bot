"""Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb"""

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_IDS, BOT_DEPLOYMENT_LIMITS
from core.utils import generate_redeem_code


def init(app, manager, OWNER_IDS):
    @app.on_message(filters.command('addredeem'))
    async def addredeem(client, message):
        uid = message.from_user.id
        
        # Check if user is admin
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in OWNER_IDS and uid not in admins:
            await message.reply_text(
                '<b><blockquote>🔒 ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ</b></blockquote>'
            )
            return
        
        args = message.text.split()
        if len(args) < 4:
            await message.reply_text(
                '<b><blockquote>𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘 𝗥𝗘𝗗𝗘𝗘𝗠 𝗖𝗢𝗗𝗘\n\n'
                '<b>Usage:</b> /addredeem <plan> <duration_days> <user_limit>\n\n'
                f'<b>Valid plans:</b> {", ".join(BOT_DEPLOYMENT_LIMITS.keys())}\n\n'
                '<b>Examples:</b>\n'
                '• /addredeem Trial 1 10\n'
                '• /addredeem Silver 30 5\n'
                '• /addredeem Gold 365 3</b></blockquote>'
            )
            return
        
        plan = args[1].capitalize()
        
        # Validate plan
        if plan not in BOT_DEPLOYMENT_LIMITS.keys():
            await message.reply_text(
                f'<b><blockquote>❌ ɪɴᴠᴀʟɪᴅ ᴘʟᴀɴ\n\n'
                f'Valid plans: {", ".join(BOT_DEPLOYMENT_LIMITS.keys())}</b></blockquote>'
            )
            return
        
        try:
            duration_days = int(args[2])
            user_limit = int(args[3])
            
            if duration_days <= 0 or user_limit <= 0:
                raise ValueError('Values must be positive')
        except (ValueError, IndexError):
            await message.reply_text(
                '<b><blockquote>❌ ɪɴᴠᴀʟɪᴅ ᴘᴀʀᴀᴍᴇᴛᴇʀs\n\n'
                'Duration and user limit must be positive integers.</b></blockquote>'
            )
            return
        
        # Generate redeem code
        code = generate_redeem_code(10)
        
        # Save to storage
        manager.storage.save_redeem_code(code, plan, duration_days, user_limit)
        
        # Send success message with code
        await message.reply_text(
            '<b><blockquote>✅ ᴄᴏᴅᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ\n\n'
            f'<code>{code}</code>\n\n'
            f'Plan: <b>{plan}</b>\n'
            f'Duration: <b>{duration_days} days</b>\n'
            f'User Limit: <b>{user_limit}</b>\n\n'
            f'Share this code with users to activate their plans!</b></blockquote>'
        )
