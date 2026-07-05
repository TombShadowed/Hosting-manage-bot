"""Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb"""

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_IDS
import json
import logging
import os
import aiofiles
from pyrogram.enums import ChatAction

logger = logging.getLogger('master.bots_mgmt')

# Callback data prefixes
BOT_MENU_CBD = "bot_menu"  # View all bots
BOT_STATUS_CBD = "bot_status"  # View single bot status
BOT_START_CBD = "bot_start"  # Start a bot
BOT_STOP_CBD = "bot_stop"  # Stop a bot
BOT_RESTART_CBD = "bot_restart"  # Restart a bot
BOT_SWITCH_CBD = "bot_switch"  # Switch branch (shows branch menu)
BOT_DELETE_CBD = "bot_delete"  # Delete a bot
BOT_DETAILS_CBD = "bot_details"  # Show detailed info
BOT_LOGS_CBD = "bot_logs"  # View logs
BOT_FILES_CBD = "bot_files"  # View files
BOT_KILL_CBD = "bot_kill"  # Kill bot process
BOT_MODIFY_CBD = "bot_modify"  # Modify bot config


def init(app, manager, OWNER_IDS):
    """Initialize bot management commands and callbacks."""
    
    async def get_user_bots(uid: int):
        """Get all bots for a specific user (filtered by owner_id)."""
        try:
            all_bots = manager.list_bots()
            # Filter bots by owner_id to only show user's own bots
            # STRICTLY: Only show bots where owner_id is set AND matches exactly
            user_bots = {}
            for bot_name, bot_data in all_bots.items():
                owner_id = bot_data.get('owner_id')
                # Must have owner_id and it must match
                if owner_id is not None and int(owner_id) == int(uid):
                    user_bots[bot_name] = bot_data
            logger.debug(f"User {uid}: found {len(user_bots)} bots out of {len(all_bots)} total")
            return user_bots
        except Exception as e:
            logger.error(f"Error in get_user_bots: {e}")
            return {}

    async def get_bot_status_text(bot_name: str) -> tuple[str, str]:
        """Get bot status (running/stopped/error) and emoji."""
        try:
            meta = manager.storage.get_bot(bot_name)
            if not meta:
                return "❌ Not found", "error"
            
            status = meta.get('status', 'stopped')
            if status == 'running':
                return "🟢 Running", "running"
            elif status == 'stopped':
                return "🔴 Stopped", "stopped"
            else:
                return "🟠 Error", "error"
        except Exception:
            return "🟠 Error", "error"

    def build_bots_list_keyboard(bots: dict, user_id: int) -> InlineKeyboardMarkup:
        """Build keyboard for listing all bots in grid format (3 per row)."""
        buttons = []
        bot_names = sorted(bots.keys())
        
        # Create grid of bots (3 per row)
        for i in range(0, len(bot_names), 3):
            row = []
            for j in range(3):
                if i + j < len(bot_names):
                    bot_name = bot_names[i + j]
                    bot_data = bots[bot_name]
                    status = bot_data.get('status', 'stopped')
                    emoji = "🟢" if status == "running" else "🔴"
                    idx = i + j + 1
                    
                    row.append(
                        InlineKeyboardButton(
                            f"{emoji} 🤖 {idx}",
                            callback_data=f"{BOT_STATUS_CBD}:{bot_name}"
                        )
                    )
            if row:
                buttons.append(row)
        
        # Add action buttons
        buttons.extend([
            [
                InlineKeyboardButton("✖️ Stop All", callback_data="bot_stop_all"),
                InlineKeyboardButton("🗑️ Remove All", callback_data="bot_delete_all")
            ],
            [InlineKeyboardButton("➕ Add New Bot", callback_data="register_new_bot")],
            [
                InlineKeyboardButton("♻️ Refresh", callback_data=f"{BOT_MENU_CBD}"),
                InlineKeyboardButton("❌ Cancel", callback_data="close_menu")
            ]])
        buttons = []
        
        # Start/Stop/Restart controls
        if status == "running":
            buttons.append([
                InlineKeyboardButton("⏸️ Stop", callback_data=f"{BOT_STOP_CBD}:{bot_name}"),
                InlineKeyboardButton("🔄 Restart", callback_data=f"{BOT_RESTART_CBD}:{bot_name}")
            ])
        else:
            buttons.append([
                InlineKeyboardButton("▶️ Start", callback_data=f"{BOT_START_CBD}:{bot_name}"),
                InlineKeyboardButton("🔄 Restart", callback_data=f"{BOT_RESTART_CBD}:{bot_name}")
            ])
        
        # Info & Management
        buttons.extend([
            [
                InlineKeyboardButton("ℹ️ Details", callback_data=f"{BOT_DETAILS_CBD}:{bot_name}"),
                InlineKeyboardButton("⚙️ Modify", callback_data=f"{BOT_MODIFY_CBD}:{bot_name}")
            ],
            # Logs & Files
            [
                InlineKeyboardButton("📋 Logs", callback_data=f"{BOT_LOGS_CBD}:{bot_name}"),
                InlineKeyboardButton("📁 Files", callback_data=f"{BOT_FILES_CBD}:{bot_name}")
            ],
            # Danger Zone
            [
                InlineKeyboardButton("⚡ Force Kill", callback_data=f"{BOT_KILL_CBD}:{bot_name}"),
                InlineKeyboardButton("🗑️ Delete", callback_data=f"{BOT_DELETE_CBD}:{bot_name}")
            ],
            # Navigation
            [
                InlineKeyboardButton("⬅️ Back", callback_data=f"{BOT_DETAILS_CBD}:{bot_name}"),
            ],
            [
                InlineKeyboardButton("🗑️ Delete", callback_data=f"{BOT_DELETE_CBD}:{bot_name}"),
                InlineKeyboardButton("📋 Logs", callback_data=f"bot_logs:{bot_name}")
            ],
            [
                InlineKeyboardButton("⬅️ Back to Bots", callback_data=f"{BOT_MENU_CBD}"),
                InlineKeyboardButton("❌ Close", callback_data="close_menu")
            ]
        ])
        
        return InlineKeyboardMarkup(buttons)

    def build_bot_details_text(bot_name: str, bot_data: dict) -> str:
        """Build detailed bot info text."""
        repo = bot_data.get('repo_url', 'N/A')
        branch = bot_data.get('branch', 'main')
        start_cmd = bot_data.get('start_cmd', 'python bot.py')
        status = bot_data.get('status', 'stopped')
        owner = bot_data.get('owner_id', 'N/A')
        
        status_emoji = "🟢" if status == "running" else "🔴"
        
        return (
            f"<b>🤖 Bot: {bot_name}</b>\n"
            f"{status_emoji} <b>Status:</b> {status.capitalize()}\n\n"
            f"<b>Repository:</b> <code>{repo}</code>\n"
            f"<b>Branch:</b> <code>{branch}</code>\n"
            f"<b>Start Command:</b> <code>{start_cmd}</code>\n"
            f"<b>Owner ID:</b> <code>{owner}</code>\n"
        )

    @app.on_message(filters.command('bots'))
    async def bots_cmd(client, message):
        """Show all user's bots with status and controls."""
        uid = message.from_user.id
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await message.reply_text(
                '<b><blockquote>🔒 ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ</b></blockquote>'
            )
            return
        
        bots = await get_user_bots(uid)
        
        if not bots:
            await message.reply_text(
                '<b><blockquote>⚠️ ɴᴏ ʙᴏᴛs ᴀᴠᴀɪʟᴀʙʟᴇ\n\n'
                'Use /register to add a new bot.</b></blockquote>'
            )
            return
        
        # Build summary
        running = sum(1 for b in bots.values() if b.get('status') == 'running')
        stopped = len(bots) - running
        
        text = (
            f"<b>📊 Your Bots</b>\n\n"
            f"🟢 Running: {running}\n"
            f"🔴 Stopped: {stopped}\n"
            f"📦 Total: {len(bots)}\n\n"
            f"<b>Select a bot to manage:</b>"
        )
        
        keyboard = build_bots_list_keyboard(bots, uid)
        await message.reply_text(text, reply_markup=keyboard)

    @app.on_callback_query(filters.regex(f"^{BOT_MENU_CBD}"))
    async def bot_menu_callback(client, callback_query):
        """Handle bot menu callback."""
        uid = callback_query.from_user.id
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        await callback_query.answer()
        
        bots = await get_user_bots(uid)
        
        if not bots:
            await callback_query.message.edit_text(
                '<b><blockquote>⚠️ ɴᴏ ʙᴏᴛs ᴀᴠᴀɪʟᴀʙʟᴇ</b></blockquote>'
            )
            return
        
        running = sum(1 for b in bots.values() if b.get('status') == 'running')
        stopped = len(bots) - running
        
        text = (
            f"<b>📊 Your Bots</b>\n\n"
            f"🟢 Running: {running}\n"
            f"🔴 Stopped: {stopped}\n"
            f"📦 Total: {len(bots)}\n\n"
            f"<b>Select a bot to manage:</b>\n"
        )
        
        keyboard = build_bots_list_keyboard(bots, uid)
        
        try:
            await callback_query.message.edit_text(text, reply_markup=keyboard)
        except Exception:
            await callback_query.message.delete()
            await client.send_message(callback_query.message.chat.id, text, reply_markup=keyboard)

    @app.on_callback_query(filters.regex(f"^{BOT_STATUS_CBD}:"))
    async def bot_status_callback(client, callback_query):
        """Show bot status and controls."""
        uid = callback_query.from_user.id
        bot_name = callback_query.data.split(":", 1)[1]
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        await callback_query.answer()
        
        try:
            bot_data = manager.storage.get_bot(bot_name)
            if not bot_data:
                await callback_query.message.edit_text(
                    '<b>❌ Bot not found</b>'
                )
                return
            
            status = bot_data.get('status', 'stopped')
            text = build_bot_details_text(bot_name, bot_data)
            keyboard = build_bot_status_keyboard(bot_name, status)
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
        except Exception as e:
            await callback_query.message.edit_text(f'<b>Error:</b> {str(e)}')

    @app.on_callback_query(filters.regex(f"^{BOT_START_CBD}:"))
    async def bot_start_callback(client, callback_query):
        """Start a bot."""
        uid = callback_query.from_user.id
        bot_name = callback_query.data.split(":", 1)[1]
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        try:
            result = manager.start(bot_name)
            await callback_query.answer(f"✅ Started {bot_name}", show_alert=False)
            
            # Refresh status
            bot_data = manager.storage.get_bot(bot_name)
            text = build_bot_details_text(bot_name, bot_data)
            keyboard = build_bot_status_keyboard(bot_name, "running")
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
        except Exception as e:
            await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)

    @app.on_callback_query(filters.regex(f"^{BOT_STOP_CBD}:"))
    async def bot_stop_callback(client, callback_query):
        """Stop a bot."""
        uid = callback_query.from_user.id
        bot_name = callback_query.data.split(":", 1)[1]
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        try:
            manager.stop(bot_name)
            await callback_query.answer(f"✅ Stopped {bot_name}", show_alert=False)
            
            # Refresh status
            bot_data = manager.storage.get_bot(bot_name)
            text = build_bot_details_text(bot_name, bot_data)
            keyboard = build_bot_status_keyboard(bot_name, "stopped")
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
        except Exception as e:
            await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)

    @app.on_callback_query(filters.regex(f"^{BOT_RESTART_CBD}:"))
    async def bot_restart_callback(client, callback_query):
        """Restart a bot."""
        uid = callback_query.from_user.id
        bot_name = callback_query.data.split(":", 1)[1]
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        try:
            manager.stop(bot_name)
            result = manager.start(bot_name)
            await callback_query.answer(f"✅ Restarted {bot_name}", show_alert=False)
            
            # Refresh status
            bot_data = manager.storage.get_bot(bot_name)
            text = build_bot_details_text(bot_name, bot_data)
            keyboard = build_bot_status_keyboard(bot_name, "running")
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
        except Exception as e:
            await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)

    @app.on_callback_query(filters.regex(f"^{BOT_DETAILS_CBD}:"))
    async def bot_details_callback(client, callback_query):
        """Show detailed bot information."""
        uid = callback_query.from_user.id
        bot_name = callback_query.data.split(":", 1)[1]
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        await callback_query.answer()
        
        try:
            bot_data = manager.storage.get_bot(bot_name)
            if not bot_data:
                await callback_query.message.edit_text('<b>❌ Bot not found</b>')
                return
            
            # Show full JSON details
            details = json.dumps(bot_data, indent=2)
            text = f"<b>🤖 Bot Details: {bot_name}</b>\n\n<code>{details}</code>"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data=f"{BOT_STATUS_CBD}:{bot_name}")],
                [InlineKeyboardButton("❌ Close", callback_data="close_menu")]
            ])
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
        except Exception as e:
            await callback_query.message.edit_text(f'<b>Error:</b> {str(e)}')

    @app.on_callback_query(filters.regex(f"^{BOT_DELETE_CBD}:"))
    async def bot_delete_callback(client, callback_query):
        """Delete a bot (confirmation)."""
        uid = callback_query.from_user.id
        bot_name = callback_query.data.split(":", 1)[1]
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        await callback_query.answer()
        
        text = (
            f"<b>⚠️ Delete Bot: {bot_name}</b>\n\n"
            f"Are you sure you want to delete this bot?\n"
            f"<i>This action cannot be undone.</i>"
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes, Delete", callback_data=f"bot_delete_confirm:{bot_name}"),
                InlineKeyboardButton("❌ Cancel", callback_data=f"{BOT_STATUS_CBD}:{bot_name}")
            ]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)

    @app.on_callback_query(filters.regex(f"^bot_delete_confirm:"))
    async def bot_delete_confirm_callback(client, callback_query):
        """Confirm bot deletion."""
        uid = callback_query.from_user.id
        bot_name = callback_query.data.split(":", 1)[1]
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        try:
            manager.delete_bot(bot_name)
            await callback_query.answer(f"✅ Deleted {bot_name}", show_alert=False)
            
            # Go back to bots list
            await callback_query.message.edit_text(
                '<b>✅ Bot deleted successfully</b>\n\n'
                'Returning to bots list...'
            )
            
            # Refresh after short delay
            import asyncio
            await asyncio.sleep(1)
            
            bots = await get_user_bots(uid)
            if bots:
                running = sum(1 for b in bots.values() if b.get('status') == 'running')
                stopped = len(bots) - running
                text = (
                    f"<b>📊 Your Bots</b>\n\n"
                    f"🟢 Running: {running}\n"
                    f"🔴 Stopped: {stopped}\n"
                    f"📦 Total: {len(bots)}\n\n"
                    f"<b>Select a bot to manage:</b>\n"
                )
                keyboard = build_bots_list_keyboard(bots, uid)
                await callback_query.message.edit_text(text, reply_markup=keyboard)
        except Exception as e:
            await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)

    @app.on_callback_query(filters.regex("^bot_stop_all$"))
    async def bot_stop_all_callback(client, callback_query):
        """Stop all bots."""
        uid = callback_query.from_user.id
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        try:
            bots = await get_user_bots(uid)
            stopped_count = 0
            
            for bot_name in bots.keys():
                try:
                    manager.stop(bot_name)
                    stopped_count += 1
                except Exception:
                    pass
            
            await callback_query.answer(f"✅ Stopped {stopped_count} bot(s)", show_alert=False)
            
            # Refresh the bots list
            import asyncio
            await asyncio.sleep(1)
            
            bots = await get_user_bots(uid)
            running = sum(1 for b in bots.values() if b.get('status') == 'running')
            stopped = len(bots) - running
            
            text = (
                f"<b>📊 Your Bots</b>\n\n"
                f"🟢 Running: {running}\n"
                f"🔴 Stopped: {stopped}\n"
                f"📦 Total: {len(bots)}\n\n"
                f"<b>Select a bot to manage:</b>\n"
            )
            
            keyboard = build_bots_list_keyboard(bots, uid)
            await callback_query.message.edit_text(text, reply_markup=keyboard)
        except Exception as e:
            await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)

    @app.on_callback_query(filters.regex("^bot_delete_all$"))
    async def bot_delete_all_callback(client, callback_query):
        """Delete all bots (confirmation)."""
        uid = callback_query.from_user.id
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        await callback_query.answer()
        
        text = (
            f"<b>⚠️ Delete All Bots</b>\n\n"
            f"Are you sure you want to delete ALL bots?\n"
            f"<i>This action cannot be undone.</i>"
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes, Delete All", callback_data="bot_delete_all_confirm"),
                InlineKeyboardButton("❌ Cancel", callback_data=f"{BOT_MENU_CBD}")
            ]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)

    @app.on_callback_query(filters.regex("^bot_delete_all_confirm$"))
    async def bot_delete_all_confirm_callback(client, callback_query):
        """Confirm deletion of all bots."""
        uid = callback_query.from_user.id
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        try:
            bots = await get_user_bots(uid)
            deleted_count = 0
            
            for bot_name in bots.keys():
                try:
                    manager.delete_bot(bot_name)
                    deleted_count += 1
                except Exception:
                    pass
            
            await callback_query.answer(f"✅ Deleted {deleted_count} bot(s)", show_alert=False)
            
            await callback_query.message.edit_text(
                '<b>✅ All bots deleted successfully</b>\n\n'
                '<b>No bots available. Use /register to add a new bot.</b>'
            )
        except Exception as e:
            await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)

    @app.on_callback_query(filters.regex("^register_new_bot$"))
    async def register_new_bot_callback(client, callback_query):
        """Show register help when Add New Bot button is clicked."""
        uid = callback_query.from_user.id
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        await callback_query.answer()
        
        text = (
            '<b>𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥 𝗕𝗢𝗧\n\n'
            '<b>Usage:</b> /register <repo_url> [branch] [start_cmd]\n\n'
            '<b>Examples:</b>\n'
            '• /register https://github.com/user/my-bot\n'
            '• /register https://github.com/user/my-bot dev\n'
            '• /register https://github.com/user/my-bot main python bot.py</b>'
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back to Bots", callback_data=f"{BOT_MENU_CBD}")],
            [InlineKeyboardButton("❌ Close", callback_data="close_menu")]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)

    @app.on_callback_query(filters.regex("^close_menu$"))
    async def close_menu_callback(client, callback_query):
        """Close the menu."""
        await callback_query.message.delete()
        await callback_query.answer()

    @app.on_message(filters.command('allbots'))
    async def allbots_cmd(client, message):
        """Admin command to see all bots in system (for debugging)."""
        uid = message.from_user.id
        
        # Only allow owners to use this command
        if uid not in OWNER_IDS:
            await message.reply_text('<b>🔒 Owner only command</b>')
            return
        
        try:
            all_bots = manager.list_bots()
            
            if not all_bots:
                await message.reply_text('<b>No bots in system</b>')
                return
            
            text = '<b>🔍 All Bots in System:</b>\n\n'
            for bot_name, bot_data in all_bots.items():
                owner = bot_data.get('owner_id', '❌ NO OWNER')
                status = bot_data.get('status', 'unknown')
                emoji = "🟢" if status == "running" else "🔴"
                text += f"{emoji} <code>{bot_name}</code>\n"
                text += f"  Owner ID: <code>{owner}</code>\n"
                text += f"  Status: {status}\n\n"
            
            # Add cleanup button for orphaned bots
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🧹 Clean Orphaned Bots", callback_data="cleanup_orphaned_bots")],
                [InlineKeyboardButton("❌ Close", callback_data="close_menu")]
            ])
            
            await message.reply_text(text, reply_markup=keyboard)
        except Exception as e:
            await message.reply_text(f'<b>Error:</b> {str(e)}')

    @app.on_callback_query(filters.regex("^cleanup_orphaned_bots$"))
    async def cleanup_orphaned_bots_callback(client, callback_query):
        """Remove bots that don't have an owner_id."""
        uid = callback_query.from_user.id
        
        if uid not in OWNER_IDS:
            await callback_query.answer("Owner only", show_alert=True)
            return
        
        try:
            all_bots = manager.list_bots()
            deleted = []
            
            for bot_name, bot_data in all_bots.items():
                owner_id = bot_data.get('owner_id')
                # Delete if no owner_id
                if owner_id is None:
                    try:
    # ============================================================
    # LOGS HANDLER
    # ============================================================
@app.on_callback_query(filters.regex(f"^{BOT_LOGS_CBD}:"))
    async def bot_logs_callback(client, callback_query):
        """View bot logs with options to send or clear."""
        uid = callback_query.from_user.id
        parts = callback_query.data.split(":")
        bot_name = parts[1]
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        await callback_query.answer()
        
        # Check if this is a secondary operation (send, clear, view)
        if len(parts) > 2:
            operation = parts[2]
            
            log_path = f"mnt/data/bots/repos/{bot_name}/logs"
            
            if operation == "send":
                await callback_query.message.reply_chat_action(ChatAction.UPLOAD_DOCUMENT)
                await callback_query.message.edit_text(f"**📂 Sending {bot_name} logs, please wait...**")
                
                try:
                    if os.path.exists(log_path):
                        await callback_query.message.reply_document(
                            log_path,
                            caption=f"**📋 @{bot_name} Logs**",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("⬅️ Back", callback_data=f"{BOT_LOGS_CBD}:{bot_name}")]
                            ])
                        )
                        await callback_query.message.edit_text(f"**✅ @{bot_name} logs sent successfully**")
                    else:
                        await callback_query.message.edit_text(
                            f"**⚠️ No logs found for @{bot_name}**",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("⬅️ Back", callback_data=f"{BOT_STATUS_CBD}:{bot_name}")]
                            ])
                        )
                except Exception as e:
                    await callback_query.message.edit_text(f"**❌ Error: {str(e)}**")
                return
            
            elif operation == "clear":
                try:
                    if os.path.exists(log_path):
                        async with aiofiles.open(log_path, "w") as f:
                            await f.write("")
                        text = f"**✅ @{bot_name} logs cleared successfully**"
                    else:
                        text = f"**⚠️ No logs found for @{bot_name}**"
                except Exception as e:
                    text = f"**❌ Error clearing logs: {str(e)}**"
                
                await callback_query.message.edit_text(
                    text,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Back", callback_data=f"{BOT_STATUS_CBD}:{bot_name}")]
                    ])
                )
                return
        
        # Main logs view
        log_path = f"mnt/data/bots/repos/{bot_name}/logs"
        
        if os.path.exists(log_path):
            try:
                async with aiofiles.open(log_path, "r") as f:
                    content = await f.read()
                    lines = content.split("\n")
                    log_lines = lines[-20:]  # Last 20 lines
                    log_preview = "\n".join(log_lines[-10:])  # Show last 10 lines
                    
                    text = (
                        f"**📋 @{bot_name} Logs**\n\n"
                        f"**<blockquote expandable>**\n{log_preview}\n**</blockquote>**"
                    )
            except Exception as e:
                text = f"**⚠️ Error reading logs: {str(e)}**"
        else:
            text = f"**⚠️ No logs available for @{bot_name}**"
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📤 Send", callback_data=f"{BOT_LOGS_CBD}:{bot_name}:send"),
                InlineKeyboardButton("🗑️ Clear", callback_data=f"{BOT_LOGS_CBD}:{bot_name}:clear")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data=f"{BOT_STATUS_CBD}:{bot_name}"),
                InlineKeyboardButton("❌ Close", callback_data="close_menu")
            ]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)

    # ============================================================
    # FILES HANDLER
    # ============================================================
    @app.on_callback_query(filters.regex(f"^{BOT_FILES_CBD}:"))
    async def bot_files_callback(client, callback_query):
        """Manage bot files (view, delete)."""
        uid = callback_query.from_user.id
        parts = callback_query.data.split(":")
        bot_name = parts[1]
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        await callback_query.answer()
        
        bot_path = f"mnt/data/bots/repos/{bot_name}"
        
        if len(parts) > 2:
            action = parts[2]
            
            if action == "delete" and len(parts) > 3:
                filename = ":".join(parts[3:])
                try:
                    file_path = os.path.join(bot_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        text = f"**✅ Deleted: `{filename}`**"
                    elif os.path.isdir(file_path):
                        import shutil
                        shutil.rmtree(file_path)
                        text = f"**✅ Deleted folder: `{filename}`**"
                    else:
                        text = f"**⚠️ File not found: `{filename}`**"
                except Exception as e:
                    text = f"**❌ Error deleting: {str(e)}**"
                
                await callback_query.message.edit_text(
                    text,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Back to Files", callback_data=f"{BOT_FILES_CBD}:{bot_name}")]
                    ])
                )
                return
        
        # List files
        try:
            if not os.path.exists(bot_path):
                await callback_query.message.edit_text(
                    f"**⚠️ Bot directory not found**",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Back", callback_data=f"{BOT_STATUS_CBD}:{bot_name}")]
                    ])
                )
                return
            
            files = os.listdir(bot_path)
            files = [f for f in files if f not in ['.git', '__pycache__', '.env', '.session']]
            
            buttons = []
            for f in sorted(files)[:15]:  # Show first 15 files
                is_dir = os.path.isdir(os.path.join(bot_path, f))
                icon = "📁" if is_dir else "📄"
                buttons.append([
                    InlineKeyboardButton(
                        f"{icon} {f}",
                        callback_data=f"{BOT_FILES_CBD}:{bot_name}:delete:{f}"
                    )
                ])
            
            buttons.extend([
                [InlineKeyboardButton("⬅️ Back", callback_data=f"{BOT_STATUS_CBD}:{bot_name}")],
                [InlineKeyboardButton("❌ Close", callback_data="close_menu")]
            ])
            
            text = f"**📁 Files for @{bot_name}**\n\n**Click to delete:**"
            
            await callback_query.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            await callback_query.message.edit_text(f"**❌ Error: {str(e)}**")

    # ============================================================
    # KILL BOT PROCESS
    # ============================================================
    @app.on_callback_query(filters.regex(f"^{BOT_KILL_CBD}:"))
    async def bot_kill_callback(client, callback_query):
        """Force kill bot process."""
        uid = callback_query.from_user.id
        bot_name = callback_query.data.split(":", 1)[1]
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        await callback_query.answer()
        
        try:
            await callback_query.message.edit_text(
                f"**⚡ Force killing @{bot_name} process...**"
            )
            
            # Use manager's stop method to kill the process
            manager.stop(bot_name)
            
            text = f"**✅ @{bot_name} process killed successfully**"
        except Exception as e:
            text = f"**❌ Error killing process: {str(e)}**"
        
        await callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data=f"{BOT_STATUS_CBD}:{bot_name}")],
                [InlineKeyboardButton("❌ Close", callback_data="close_menu")]
            ])
        )

    # ============================================================
    # MODIFY BOT CONFIG
    # ============================================================
    @app.on_callback_query(filters.regex(f"^{BOT_MODIFY_CBD}:"))
    async def bot_modify_callback(client, callback_query):
        """Modify bot configuration (branch, start command, etc)."""
        uid = callback_query.from_user.id
        bot_name = callback_query.data.split(":", 1)[1]
        
        try:
            admins = manager.storage.get_admins()
        except Exception:
            admins = []
        
        if uid not in admins and uid not in OWNER_IDS:
            await callback_query.answer("Unauthorized", show_alert=True)
            return
        
        await callback_query.answer()
        
        try:
            bot_data = manager.storage.get_bot(bot_name)
            repo = bot_data.get('repo_url', 'N/A')
            branch = bot_data.get('branch', 'main')
            start_cmd = bot_data.get('start_cmd', 'python bot.py')
            
            text = (
                f"**⚙️ Modify @{bot_name}**\n\n"
                f"**Repo:** `{repo}`\n"
                f"**Branch:** `{branch}`\n"
                f"**Start Command:** `{start_cmd}`\n\n"
                f"**<blockquote expandable>📝 Click buttons below to edit:</blockquote>**"
            )
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🌿 Change Branch", callback_data=f"bot_change_branch:{bot_name}"),
                    InlineKeyboardButton("▶️ Change Command", callback_data=f"bot_change_cmd:{bot_name}")
                ],
                [InlineKeyboardButton("⬅️ Back", callback_data=f"{BOT_STATUS_CBD}:{bot_name}")],
                [InlineKeyboardButton("❌ Close", callback_data="close_menu")]
            ])
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
        except Exception as e:
            await callback_query.message.edit_text(f"**❌ Error: {str(e)}**")                        manager.delete_bot(bot_name)
                        deleted.append(bot_name)
                    except Exception as e:
                        logger.error(f"Failed to delete bot {bot_name}: {e}")
            
            if deleted:
                text = f'<b>🧹 Cleaned {len(deleted)} orphaned bot(s):</b>\n\n'
                for bot in deleted:
                    text += f'  🗑️ <code>{bot}</code>\n'
            else:
                text = '<b>✅ No orphaned bots found</b>'
            
            await callback_query.message.edit_text(text)
            await callback_query.answer("Cleanup complete", show_alert=False)
        except Exception as e:
            await callback_query.answer(f"Error: {str(e)}", show_alert=True)
