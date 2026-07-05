# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_IDS, BOT_DEPLOYMENT_LIMITS, PREMIUM_PLAN_PIC
from core.bot_naming import generate_bot_name, extract_repo_name
from datetime import datetime, timedelta


def init(app, manager, OWNER_IDS):
    @app.on_message(filters.command('register'))
    async def register(client, message):
        uid = message.from_user.id
        user = message.from_user
        
        # Check admin only mode
        admin_only = manager.storage.get_admin_only()
        if admin_only:
            # Admin mode: only admins can register
            try:
                admins = manager.storage.get_admins()
            except Exception:
                admins = []
            if uid not in admins and uid not in OWNER_IDS:
                await message.reply_text('<b><blockquote>◉ 𝗕𝗢𝗧 𝗛𝗢𝗦𝗧𝗜𝗡𝗚 𝗜𝗦 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗜𝗡 𝗔𝗗𝗠𝗜𝗡-𝗢𝗡𝗟𝗬 𝗠𝗢𝗗𝗘</blockquote></b>')
                return
        
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text(
                '<b><blockquote>◉ 𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥 𝗕𝗢𝗧\n\n'
                '𝗨𝗦𝗔𝗚𝗘: /register <repo_url> [branch] [start_cmd]\n\n'
                '𝗘𝗫𝗔𝗠𝗣𝗟𝗘𝗦:\n'
                '• /register https://github.com/user/my-bot\n'
                '• /register https://github.com/user/my-bot dev\n'
                '• /register https://github.com/user/my-bot main python bot.py</blockquote></b>'
            )
            return
        
        repo = args[1]
        branch = args[2] if len(args) >= 3 else 'main'
        start_cmd = ' '.join(args[3:]) if len(args) >= 4 else 'python bot.py'
        
        # Generate bot name automatically
        username = user.username or f"user{uid}"
        bot_name = generate_bot_name(repo, uid, username)
        
        # Check deployment limit for non-admin users
        is_admin = uid in OWNER_IDS or (uid in (manager.storage.get_admins() if hasattr(manager.storage, 'get_admins') else []))
        if not is_admin:
            # Get user's plan and limit
            plan_type = manager.storage.get_premium_plan(uid)
            
            # Check if user has a plan
            if not plan_type:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton('• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ • ', callback_data='premium_upgrade')]
                ])
                if PREMIUM_PLAN_PIC:
                    await message.reply_photo(
                        photo=PREMIUM_PLAN_PIC,
                        caption='<b><blockquote>◉ 𝗔𝗖𝗖𝗘𝗦𝗦 𝗥𝗘𝗦𝗧𝗥𝗜𝗖𝗧𝗘𝗗\n\n'
                        '𝗬𝗢𝗨 𝗔𝗥𝗘 𝗡𝗢𝗧 𝗔 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗨𝗦𝗘𝗥. 𝗣𝗟𝗔𝗡 𝗬𝗢𝗨𝗥 𝗨𝗣𝗚𝗥𝗔𝗗𝗘 𝗧𝗢 𝗨𝗦𝗘 𝗧𝗛𝗜𝗦 𝗙𝗘𝗔𝗧𝗨𝗥𝗘.\n\n'
                        '◈ 𝗖𝗟𝗜𝗖𝗞 𝗧𝗛𝗘 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗨𝗧𝗧𝗢𝗡 𝗕𝗘𝗟𝗢𝗪</blockquote></b>',
                        reply_markup=keyboard
                    )
                else:
                    await message.reply_text(
                        '<b><blockquote>◉ 𝗔𝗖𝗖𝗘𝗦𝗦 𝗥𝗘𝗦𝗧𝗥𝗜𝗖𝗧𝗘𝗗\n\n'
                        '𝗬𝗢𝗨 𝗔𝗥𝗘 𝗡𝗢𝗧 𝗔 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗨𝗦𝗘𝗥. 𝗣𝗟𝗔𝗡 𝗬𝗢𝗨𝗥 𝗨𝗣𝗚𝗥𝗔𝗗𝗘 𝗧𝗢 𝗨𝗦𝗘 𝗧𝗛𝗜𝗦 𝗙𝗘𝗔𝗧𝗨𝗥𝗘.\n\n'
                        '◈ 𝗖𝗟𝗜𝗖𝗞 𝗧𝗛𝗘 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗨𝗧𝗧𝗢𝗡 𝗕𝗘𝗟𝗢𝗪</blockquote></b>',
                        reply_markup=keyboard
                    )
                return
            
            limit = BOT_DEPLOYMENT_LIMITS.get(plan_type.capitalize(), 0)
            
            # Count current bots owned by user
            current_bots = manager.storage.get_user_bots(uid)
            
            if current_bots >= limit:
                plan_msg = f' ({plan_type} plan)' if plan_type else ''
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton('💳 ᴜᴘɢʀᴀᴅᴇ ɴᴏᴡ', callback_data='premium_upgrade')]
                ])
                await message.reply_text(
                    f'<b><blockquote>◉ 𝗗𝗘𝗣𝗟𝗢𝗬𝗠𝗘𝗡𝗧 𝗟𝗜𝗠𝗜𝗧 𝗥𝗘𝗔𝗖𝗛𝗘𝗗\n\n'
                    f'𝗬𝗢𝗨 𝗛𝗔𝗩𝗘 𝗥𝗘𝗔𝗖𝗛𝗘𝗗 𝗬𝗢𝗨𝗥 𝗟𝗜𝗠𝗜𝗧{plan_msg}\n\n'
                    f'𝗖𝗨𝗥𝗥𝗘𝗡𝗧: {current_bots}/{limit} 𝗕𝗢𝗧𝗦\n\n'
                    f'𝗨𝗣𝗚𝗥𝗔𝗗𝗘 𝗬𝗢𝗨𝗥 𝗣𝗟𝗔𝗡 𝗧𝗢 𝗗𝗘𝗣𝗟𝗢𝗬 𝗠𝗢𝗥𝗘.</blockquote></b>',
                    reply_markup=keyboard
                )
                return
        
        try:
            # Step 1: Send initial progress message
            status_msg = await message.reply_text(
                '<b><blockquote>◉ 𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥𝗜𝗡𝗚 𝗕𝗢𝗧\n\n'
                '◌ 𝗖𝗟𝗢𝗡𝗜𝗡𝗚 𝗥𝗘𝗣𝗢𝗦𝗜𝗧𝗢𝗥𝗬...'
                '</blockquote></b>'
            )
            
            repo_name = extract_repo_name(repo)
            
            # Step 2: Update progress - preparing environment
            await status_msg.edit_text(
                '<b><blockquote>◉ 𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥𝗜𝗡𝗚 𝗕𝗢𝗧\n\n'
                '✓ 𝗥𝗘𝗣𝗢𝗦𝗜𝗧𝗢𝗥𝗬 𝗖𝗟𝗢𝗡𝗘𝗗\n'
                '◌ 𝗣𝗥𝗘𝗣𝗔𝗥𝗜𝗡𝗚 𝗘𝗡𝗩𝗜𝗥𝗢𝗡𝗠𝗘𝗡𝗧...'
                '</blockquote></b>'
            )
            
            # Step 3: Register and start bot, then update progress
            meta = manager.register_bot(bot_name, repo, branch, start_cmd, owner_id=uid)
            
            # Step 4: Final success message
            msg = f'<b><blockquote>✓ 𝗕𝗢𝗧 𝗗𝗘𝗣𝗟𝗢𝗬𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬!</blockquote></b>\n\n'
            msg += f'<blockquote expandable><b>◉ 𝗕𝗢𝗧 𝗗𝗘𝗧𝗔𝗜𝗟𝗦</b>\n'
            msg += f'• 𝗡𝗔𝗠𝗘: <code>{bot_name}</code>\n'
            msg += f'• 𝗥𝗘𝗣𝗢: {repo_name}\n'
            msg += f'• 𝗕𝗥𝗔𝗡𝗖𝗛: {branch}\n'
            msg += f'• 𝗦𝗧𝗔𝗧𝗨𝗦: <b>{meta.get("status", "unknown").upper()}</b>\n'
            if meta.get('pid'):
                msg += f'• 𝗣𝗜𝗗: <code>{meta.get("pid")}</code></blockquote expandable>\n'
            msg += f'\n<blockquote>◌ 𝗨𝗦𝗘 /status 𝗧𝗢 𝗖𝗛𝗘𝗖𝗞 𝗧𝗛𝗘 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗨𝗦</blockquote>\n'
            msg += f'<blockquote>◌ 𝗨𝗦𝗘 /stop {bot_name} 𝗧𝗢 𝗦𝗧𝗢𝗣 𝗧𝗛𝗘 𝗕𝗢𝗧</blockquote>'
            await status_msg.edit_text(msg)
        except KeyError:
            await message.reply_text('<b><blockquote>◉ 𝗕𝗢𝗧 𝗡𝗔𝗠𝗘 𝗖𝗢𝗡𝗙𝗟𝗜𝗖𝗧. 𝗧𝗛𝗜𝗦 𝗡𝗔𝗠𝗘 𝗜𝗦 𝗔𝗟𝗥𝗘𝗔𝗗𝗬 𝗜𝗡 𝗨𝗦𝗘. 𝗣𝗟𝗘𝗔𝗦𝗘 𝗧𝗥𝗬 𝗔𝗚𝗔𝗜𝗡.</blockquote></b>')
        except Exception as e:
            await message.reply_text(f'<b><blockquote>✖ 𝗘𝗥𝗥𝗢𝗥: {str(e)}</blockquote></b>')
