import logging
from typing import List

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

logger = logging.getLogger(__name__)


def _get_force_sub_channels(manager) -> List[int]:
    data = manager.storage.load()
    channels = data.get("__force_sub_channels__", [])
    if not isinstance(channels, list):
        return []
    cleaned = []
    for item in channels:
        try:
            cleaned.append(int(item))
        except Exception:
            continue
    return cleaned


def _save_force_sub_channels(manager, channels: List[int]) -> None:
    data = manager.storage.load()
    data["__force_sub_channels__"] = [int(channel) for channel in channels if str(channel).strip()]
    manager.storage.save(data)


def _is_admin_or_owner(user_id: int, owner_ids: list, manager) -> bool:
    if user_id in owner_ids:
        return True
    try:
        return user_id in manager.get_admins()
    except Exception:
        return False


async def _has_access(client: Client, user_id: int, channels: List[int]) -> bool:
    if not channels:
        return True
    for channel_id in channels:
        try:
            member = await client.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status in {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER}:
                return True
        except UserNotParticipant:
            continue
        except Exception as exc:
            logger.warning("force-sub check failed for %s: %s", channel_id, exc)
            continue
    return False


async def _send_force_sub_prompt(client: Client, target, channels: List[int], *, edit: bool = False) -> None:
    buttons = []
    for channel_id in channels:
        try:
            chat = await client.get_chat(channel_id)
            title = chat.title or f"Channel {channel_id}"
            invite_link = chat.invite_link
            if not invite_link and getattr(chat, "username", None):
                invite_link = f"https://t.me/{chat.username}"
            if invite_link:
                buttons.append([InlineKeyboardButton(title, url=invite_link)])
            else:
                buttons.append([InlineKeyboardButton(title, url=f"https://t.me/{channel_id}")])
        except Exception:
            buttons.append([InlineKeyboardButton(f"Channel {channel_id}", url=f"https://t.me/{channel_id}")])

    buttons.append([InlineKeyboardButton("✅ Verify", callback_data="fsub_verify")])
    markup = InlineKeyboardMarkup(buttons)
    text = "<b>⚠️ Please join the required channel(s) first and then verify.</b>"

    if edit:
        await target.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
    else:
        await target.reply_text(text, reply_markup=markup, disable_web_page_preview=True)


def init(app: Client, manager, OWNER_IDS: list):
    @app.on_message(filters.private)
    async def enforce_force_sub(client: Client, message: Message):
        if not message.from_user or message.from_user.is_bot:
            return

        if message.text and message.text.startswith("/"):
            return

        if _is_admin_or_owner(message.from_user.id, OWNER_IDS, manager):
            return

        channels = _get_force_sub_channels(manager)
        if not channels:
            return

        if await _has_access(client, message.from_user.id, channels):
            return

        await _send_force_sub_prompt(client, message, channels)

    @app.on_callback_query(filters.regex(r"^fsub_verify$"))
    async def verify_force_sub(client: Client, callback_query: CallbackQuery):
        await callback_query.answer()
        user_id = callback_query.from_user.id
        if _is_admin_or_owner(user_id, OWNER_IDS, manager):
            await callback_query.message.edit_text("✅ Access granted. You are exempt from force-sub.")
            return

        channels = _get_force_sub_channels(manager)
        if not channels:
            await callback_query.message.edit_text("✅ Force-sub is not configured.")
            return

        if await _has_access(client, user_id, channels):
            await callback_query.message.edit_text("✅ You have joined the required channel(s).")
            return

        await _send_force_sub_prompt(client, callback_query.message, channels, edit=True)

    @app.on_message(filters.private & filters.command("addfsub"))
    async def add_force_sub(client: Client, message: Message):
        if not _is_admin_or_owner(message.from_user.id, OWNER_IDS, manager):
            await message.reply_text("<b>Only admins and the owner can use this command.</b>")
            return

        args = message.text.split()[1:]
        if not args:
            await message.reply_text("<b>Usage:</b> /addfsub <channel_id> [channel_id ...]")
            return

        channels = _get_force_sub_channels(manager)
        added = []
        failed = []

        for raw in args:
            try:
                if raw.startswith("@"):
                    chat = await client.get_chat(raw)
                    channel_id = int(chat.id)
                else:
                    channel_id = int(raw)
            except Exception:
                failed.append(raw)
                continue

            if channel_id in channels:
                continue
            channels.append(channel_id)
            added.append(str(channel_id))

        _save_force_sub_channels(manager, channels)

        if added:
            await message.reply_text(f"<b>Added force-sub channel(s):</b> {', '.join(added)}")
        else:
            await message.reply_text("<b>No new force-sub channel was added.</b>")

        if failed:
            await message.reply_text(f"<b>Could not parse:</b> {', '.join(failed)}")

    @app.on_message(filters.private & filters.command("delfsub"))
    async def delete_force_sub(client: Client, message: Message):
        if not _is_admin_or_owner(message.from_user.id, OWNER_IDS, manager):
            await message.reply_text("<b>Only admins and the owner can use this command.</b>")
            return

        args = message.text.split()[1:]
        channels = _get_force_sub_channels(manager)
        if not channels:
            await message.reply_text("<b>No force-sub channels are configured.</b>")
            return

        if not args or args[0].lower() == "all":
            _save_force_sub_channels(manager, [])
            await message.reply_text("<b>Removed all force-sub channels.</b>")
            return

        removed = []
        for raw in args:
            try:
                channel_id = int(raw)
            except Exception:
                continue
            if channel_id in channels:
                channels.remove(channel_id)
                removed.append(str(channel_id))

        _save_force_sub_channels(manager, channels)
        if removed:
            await message.reply_text(f"<b>Removed force-sub channel(s):</b> {', '.join(removed)}")
        else:
            await message.reply_text("<b>No matching force-sub channels were removed.</b>")

    @app.on_message(filters.private & filters.command("channels"))
    async def list_force_sub_channels(client: Client, message: Message):
        if not _is_admin_or_owner(message.from_user.id, OWNER_IDS, manager):
            await message.reply_text("<b>Only admins and the owner can use this command.</b>")
            return

        channels = _get_force_sub_channels(manager)
        if not channels:
            await message.reply_text("<b>No force-sub channels configured.</b>")
            return

        lines = []
        for channel_id in channels:
            try:
                chat = await client.get_chat(channel_id)
                name = chat.title or chat.username or str(channel_id)
                lines.append(f"- {name} ({channel_id})")
            except Exception:
                lines.append(f"- {channel_id}")

        await message.reply_text("<b>Configured force-sub channels:</b>\n" + "\n".join(lines))

    # ===== System stats =====
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    memory_used = round(memory.used / (1024 ** 3), 2)
    memory_total = round(memory.total / (1024 ** 3), 2)

    # ===== Uptime / start time =====
    uptime = get_uptime()
    start_time = BOT_START_TIME.strftime("%d-%b-%Y | %I:%M %p")

    caption = STATUS_TXT.format(
        total_users=total_users,
        banned_users=banned_users,
        premium_users=premium_users,
        total_bots=total_bots,
        running_bots=running_bots,
        uptime=uptime,
        start_time=start_time,
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        memory_used=memory_used,
        memory_total=memory_total
    )

    await waiting.edit(
        caption,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Close", callback_data="close")]]
        )
    )


#--------------------------------------------------------------[[ADMIN COMMANDS]]---------------------------------------------------------------------------#
# Handler for the /cancel command
cancel_lock = asyncio.Lock()
is_canceled = False


@SidBot.on_message(filters.command("cancel") & ADMINS)
@sid_hpr.on_log_exception
async def cancel_broadcast(client: Client, message: Message):
    global is_canceled
    async with cancel_lock:
        is_canceled = True

@SidBot.on_message(filters.command("broadcast") & ADMINS)
@sid_hpr.on_log_exception
async def broadcast(client: Client, message: Message):
    global is_canceled
    args = message.text.split()[1:]

    if not message.reply_to_message:
        msg = await message.reply(
            "Reply to a message to broadcast.\n\nUsage examples:\n"
            "`/broadcast normal`\n"
            "`/broadcast pin`\n"
            "`/broadcast delete 30`\n"
            "`/broadcast pin delete 30`\n"
            "`/broadcast silent`\n"
        )
        await asyncio.sleep(8)
        return await msg.delete()

    # Defaults
    do_pin = False
    do_delete = False
    duration = 0
    silent = False
    mode_text = []

    i = 0
    while i < len(args):
        arg = args[i].lower()
        if arg == "pin":
            do_pin = True
            mode_text.append("PIN")
        elif arg == "delete":
            do_delete = True
            try:
                duration = int(args[i + 1])
                i += 1
            except (IndexError, ValueError):
                return await message.reply("<b>Provide valid duration for delete mode.</b>\nUsage: `/broadcast delete 30`")
            mode_text.append(f"DELETE({duration}s)")
        elif arg == "silent":
            silent = True
            mode_text.append("SILENT")
        else:
            mode_text.append(arg.upper())
        i += 1

    if not mode_text:
        mode_text.append("NORMAL")

    # Reset cancel flag
    async with cancel_lock:
        is_canceled = False

    query = await db.full_userbase()
    broadcast_msg = message.reply_to_message
    total = len(query)
    successful = blocked = deleted = unsuccessful = 0

    pls_wait = await message.reply(f"<i>Broadcasting in <b>{' + '.join(mode_text)}</b> mode...</i>")

    bar_length = 20
    progress_bar = ''
    last_update_percentage = 0
    update_interval = 0.05  # 5%

    for i, chat_id in enumerate(query, start=1):
        async with cancel_lock:
            if is_canceled:
                await pls_wait.edit(f"›› BROADCAST ({' + '.join(mode_text)}) CANCELED ❌")
                return

        try:
            sent_msg = await broadcast_msg.copy(chat_id, disable_notification=silent)

            if do_pin:
                await client.pin_chat_message(chat_id, sent_msg.id, both_sides=True)
            if do_delete:
                asyncio.create_task(auto_delete(sent_msg, duration))

            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.x)
            try:
                sent_msg = await broadcast_msg.copy(chat_id, disable_notification=silent)
                if do_pin:
                    await client.pin_chat_message(chat_id, sent_msg.id, both_sides=True)
                if do_delete:
                    asyncio.create_task(auto_delete(sent_msg, duration))
                successful += 1
            except:
                unsuccessful += 1
        except UserIsBlocked:
            await db.del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await db.del_user(chat_id)
            deleted += 1
        except:
            unsuccessful += 1
            await db.del_user(chat_id)

        # Progress
        percent_complete = i / total
        if percent_complete - last_update_percentage >= update_interval or last_update_percentage == 0:
            num_blocks = int(percent_complete * bar_length)
            progress_bar = "●" * num_blocks + "○" * (bar_length - num_blocks)
            status_update = f"""<b>›› BROADCAST ({' + '.join(mode_text)}) IN PROGRESS...

<blockquote>⏳:</b> [{progress_bar}] <code>{percent_complete:.0%}</code></blockquote>

<b>›› Total Users: <code>{total}</code>
›› Successful: <code>{successful}</code>
›› Blocked: <code>{blocked}</code>
›› Deleted: <code>{deleted}</code>
›› Unsuccessful: <code>{unsuccessful}</code></b>

<i>➪ To stop broadcasting click: <b>/cancel</b></i>"""
            await pls_wait.edit(status_update)
            last_update_percentage = percent_complete

    # Final status
    final_status = f"""<b>›› BROADCAST ({' + '.join(mode_text)}) COMPLETED ✅

<blockquote>Dᴏɴᴇ:</b> [{progress_bar}] {percent_complete:.0%}</blockquote>

<b>›› Total Users: <code>{total}</code>
›› Successful: <code>{successful}</code>
›› Blocked: <code>{blocked}</code>
›› Deleted: <code>{deleted}</code>
›› Unsuccessful: <code>{unsuccessful}</code></b>"""
    return await pls_wait.edit(final_status)


# helper for delete mode
async def auto_delete(sent_msg, duration):
    await asyncio.sleep(duration)
    try:
        await sent_msg.delete()
    except:
        pass


@SidBot.on_message(filters.command(["info", "userinfo", "whois"]) & ADMINS)
@sid_hpr.on_log_exception
async def admin_pfp(bot: SidBot, message: Message):
    # Quick check: ensure message.from_user exists
    if not message.from_user:
        return

    # Wrap in try-except to handle all errors and ensure response
    try:
        # Determine target: reply > argument > sender
        target_chat = None
        target_id = None
        is_channel = False

        # Check if replying to a message
        if message.reply_to_message:
            if message.reply_to_message.from_user:
                target_chat = message.reply_to_message.from_user
                target_id = target_chat.id
            elif message.reply_to_message.sender_chat:
                target_chat = message.reply_to_message.sender_chat
                target_id = target_chat.id
                is_channel = True
        # Check if user/channel ID or username provided as argument
        elif len(message.command) > 1:
            try:
                query = message.command[1].strip()
                # Try to get chat by ID or username
                if query.isdigit() or (query.startswith('-') and query[1:].isdigit()):
                    target_id = int(query)
                    # Try to get as chat (for channels)
                    try:
                        target_chat = await bot.get_chat(target_id)
                        is_channel = target_chat.type in (ChatType.CHANNEL, ChatType.SUPERGROUP)
                    except:
                        # If chat fails, try as user
                        try:
                            target_chat = await bot.get_users(target_id)
                            is_channel = False
                        except:
                            raise
                elif query.startswith('@'):
                    target_chat = await bot.get_chat(query)
                    target_id = target_chat.id
                    is_channel = target_chat.type in (ChatType.CHANNEL, ChatType.SUPERGROUP)
                else:
                    # Try as chat first (for channels), then as user
                    try:
                        target_chat = await bot.get_chat(query)
                        target_id = target_chat.id
                        is_channel = target_chat.type in (ChatType.CHANNEL, ChatType.SUPERGROUP)
                    except:
                        target_chat = await bot.get_users(query)
                        target_id = target_chat.id
                        is_channel = False
            except Exception as e:
                return await message.reply_text(
                    f"❌ <b>Error:</b> Could not find user/channel. Please provide a valid ID or username.\n\n"
                    f"<b>Usage:</b>\n"
                    f"• <code>/info</code> - Your info\n"
                    f"• <code>/info @username</code> - User/channel info by username\n"
                    f"• <code>/info 123456789</code> - User/channel info by ID\n"
                    f"• Reply to a message with <code>/info</code> - Get info of replied user/channel",
                    quote=True
                )
        # Default to sender
        else:
            target_chat = message.from_user
            target_id = target_chat.id
            is_channel = False

        # If we only have ID, fetch chat/user object
        if not target_chat and target_id:
            try:
                # Try as chat first (for channels)
                try:
                    target_chat = await bot.get_chat(target_id)
                    is_channel = target_chat.type in (ChatType.CHANNEL, ChatType.SUPERGROUP)
                except:
                    # If chat fails, try as user
                    target_chat = await bot.get_users(target_id)
                    is_channel = False
            except Exception as e:
                return await message.reply_text(
                    f"❌ <b>Error:</b> Could not fetch information for ID <code>{target_id}</code>.",
                    quote=True,
                    protect_content=PROTECT_CONTENT
                )

        # Check if command sender is banned (not target) - but allow admins/owner
        sender_id = message.from_user.id

        # Allow owner and admins to bypass ban check
        # Check owner first (fastest check, no DB call needed)
        is_admin_or_owner = (sender_id == OWNER_ID)

        # Only check admin status if not owner (to avoid unnecessary DB calls)
        if not is_admin_or_owner:
            try:
                from utils import sid_db
                # Use asyncio.wait_for to add timeout to admin check
                try:
                    is_admin_or_owner = await asyncio.wait_for(
                        sid_db.admin_exists(sender_id),
                        timeout=2.0  # 2 second timeout
                    )
                except asyncio.TimeoutError:
                    logging.warning(f"[INFO_CMD] Admin check timed out for {sender_id}")
                    is_admin_or_owner = False
                except Exception as admin_check_error:
                    # If admin check fails, log but don't block - assume not admin for ban check
                    logging.warning(f"[INFO_CMD] Admin check failed for {sender_id}: {admin_check_error}")
                    is_admin_or_owner = False
            except Exception as import_error:
                # If import fails, at least check owner
                logging.error(f"[INFO_CMD] Failed to import sid_db: {import_error}")
                is_admin_or_owner = False

        # Only check ban list for non-admins
        if not is_admin_or_owner:
            try:
                banned_users = await db.get_ban_users()
                if sender_id in banned_users:
                    caption = BAN_MSG.format(
                        mention=message.from_user.mention
                    )

                    return await message.reply_photo(
                        photo=BAN_PIC,
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("🚨 Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ", url=ADMIN_LINK)]]
                        ),
                        protect_content=PROTECT_CONTENT,
                    )
            except Exception as ban_check_error:
                # If ban check fails, log but continue - don't block execution
                logging.warning(f"[INFO_CMD] Ban check failed for {sender_id}: {ban_check_error}")

        wait_msg = await message.reply_text("⏳ ɢᴇɴᴇʀᴀᴛɪɴɢ ɪɴғᴏ...", protect_content=PROTECT_CONTENT)
        await asyncio.sleep(1)
        await wait_msg.delete()

        # Fetch profile photo - use async iteration for better reliability
        profile_photo = None
        try:
            async for photo in bot.get_chat_photos(target_id, limit=1):
                profile_photo = photo.file_id
                break
        except Exception:
            profile_photo = None

        # Get chat/user info
        if is_channel:
            chat_name = target_chat.title or "N/A"
            chat_username = target_chat.username or "N/A"
            chat_id = target_id
            bio = target_chat.description or "ɴᴏ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ"
            member_count = "N/A"
            try:
                if hasattr(target_chat, 'members_count'):
                    member_count = target_chat.members_count or "N/A"
            except:
                pass
        else:
            # Set chat_id and get user info
            chat_id = target_id
            chat_name = target_chat.first_name + (f" {target_chat.last_name}" if hasattr(target_chat, 'last_name') and target_chat.last_name else "")
            chat_username = target_chat.username or "N/A"
            
            # Fetch bio safely - use get_chat() to get bio (works for both own and others)
            # This is the correct method as shown in working code
            try:
                # Use get_chat() instead of get_users() - this returns Chat object with bio
                chat_user = await bot.get_chat(chat_id)
                bio = chat_user.bio if chat_user.bio else "ɴᴏ ʙɪᴏ"
            except Exception as bio_error:
                logging.warning(f"[INFO_CMD] Bio fetch error for {chat_id}: {bio_error}")
                bio = "ɴᴏ ʙɪᴏ"
            
            member_count = "N/A"
            
            # Check if target user is admin/owner
            from utils import sid_db
            is_target_admin = False
            try:
                is_target_admin = (chat_id == OWNER_ID) or (await sid_db.admin_exists(chat_id))
            except Exception:
                is_target_admin = (chat_id == OWNER_ID)

        backup_photo = "https://telegra.ph/file/1c4fe47a4aaf5a3313f69-201afdedf112e512d3.jpg"

        # Build profile text based on user or channel
        if is_channel:
            # Channel info
            profile_text = (
                f"📢 <b>𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗜𝗡𝗙𝗢</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"➣ <b>ɴᴀᴍᴇ:</b> {chat_name}\n"
                f"➣ <b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{chat_username if chat_username != 'N/A' else 'Not set'}\n"
                f"➣ <b>ᴄʜᴀᴛ ɪᴅ:</b> <code>{chat_id}</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"➣ <b>ᴛʏᴘᴇ:</b> {'Channel' if target_chat.type == ChatType.CHANNEL else 'Supergroup'}\n"
                f"➣ <b>ᴍᴇᴍʙᴇʀs:</b> {member_count}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"➣ <b>ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:</b> <code>{bio}</code>"
            )
            reply_markup = None
        else:
            # User info - check premium
            is_premium_user = await db.is_premium(chat_id)
            
            # Add admin status indicator
            admin_status = ""
            if is_target_admin:
                if chat_id == OWNER_ID:
                    admin_status = "\n➣ <b>ʀᴏʟᴇ:</b>ᴍʏ ᴍᴀsᴛᴇʀ"
                else:
                    admin_status = "\n➣ <b>ʀᴏʟᴇ:</b>ɢᴜᴀʀᴅɪᴀɴ"

            if is_premium_user:
                expiry_time = await db.get_premium_expiry(chat_id)
                if expiry_time:
                    # Ensure timezone-aware and convert to IST
                    from pytz import timezone as tz
                    INDIA_TZ = tz("Asia/Kolkata")
                    if expiry_time.tzinfo is None:
                        expiry_ist = INDIA_TZ.localize(expiry_time)
                    else:
                        expiry_ist = expiry_time.astimezone(INDIA_TZ)
                    expiry_text = expiry_ist.strftime('%Y-%m-%d %I:%M:%S %p IST')
                else:
                    expiry_text = "Unknown"

                plan_type = await db.get_premium_plan(chat_id)
                plan_text = plan_type if plan_type else "Not set"

                profile_text = (
                    f"👤 <b>𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"➣ <b>ɴᴀᴍᴇ:</b> {chat_name}\n"
                    f"➣ <b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{chat_username if chat_username != 'N/A' else 'Not set'}\n"
                    f"➣ <b>ᴜsᴇʀ ɪᴅ:</b> <code>{chat_id}</code>{admin_status}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"➣ <b>sᴛᴀᴛᴜs:</b> ☑️ ᴀᴄᴛɪᴠᴇ\n"
                    f"➣ <b>ᴘʀᴇᴍɪᴜᴍ:</b> ʏᴇs ✨\n"
                    f"➣ <b>ᴘʟᴀɴ:</b> {plan_text}\n"
                    f"➣ <b>ᴇxᴘɪʀʏ:</b> {expiry_text}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"➣ <b>ʙɪᴏ:</b> <code>{bio}</code>"
                )

                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("• ғʀᴇᴇ ᴛʀɪᴀʟ •", callback_data="free_trial"), InlineKeyboardButton("• ᴜᴘɢʀᴀᴅᴇ ᴘʀᴇᴍɪᴜᴍ •", callback_data="premium")]
                ])

            else:
                profile_text = (
                    f"👤 <b>𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"➣ <b>ɴᴀᴍᴇ:</b> {chat_name}\n"
                    f"➣ <b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{chat_username if chat_username != 'N/A' else 'Not set'}\n"
                    f"➣ <b>ᴜsᴇʀ ɪᴅ:</b> <code>{chat_id}</code>{admin_status}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"➣ <b>sᴛᴀᴛᴜs:</b> ❌ ɴᴏᴛ ᴀᴄᴛɪᴠᴇ\n"
                    f"➣ <b>ᴘʀᴇᴍɪᴜᴍ:</b> ɴᴏ 🥀\n"
                    f"➣ <b>ᴘʟᴀɴ:</b> N/A\n"
                    f"➣ <b>ᴇxᴘɪʀʏ:</b> N/A\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"➣ <b>ʙɪᴏ:</b> <code>{bio}</code>"
                )

                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("• ғʀᴇᴇ ᴛʀɪᴀʟ •", callback_data="free_trial"), InlineKeyboardButton("• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •", callback_data="premium")]
                ])

        # Send message with profile photo (use backup only if no profile photo found)
        try:
            if profile_photo:
                await message.reply_photo(profile_photo, caption=profile_text, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
            else:
                await message.reply_photo(backup_photo, caption=profile_text, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
        except Exception as e:
            # If photo sending fails, try with backup
            try:
                await message.reply_photo(backup_photo, caption=profile_text, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
            except:
                # If photo completely fails, send as text
                await message.reply_text(profile_text, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)

    except Exception as e:
        # Send error message to user instead of silently failing
        error_msg = f"❌ <b>Error:</b> An error occurred while processing your request.\n\n<code>{str(e)}</code>"
        logging.error(f"[INFO_CMD] Error in user_profile for user {message.from_user.id}: {e}", exc_info=True)
        try:
            await message.reply_text(error_msg, quote=True, protect_content=PROTECT_CONTENT)
        except Exception as reply_error:
            # If even error message fails, try without quote
            try:
                await message.reply_text(error_msg, protect_content=PROTECT_CONTENT)
            except Exception as final_error:
                # Last resort - try to send a simple message
                try:
                    await message.reply_text("❌ An error occurred. Please try again later.", quote=True, protect_content=PROTECT_CONTENT)
                except:
                    logging.error(f"[INFO_CMD] Failed to send any error message: {reply_error}, {final_error}")


#=======================================================================================================
# HELPERS
#=======================================================================================================

from .helper import sid_txt, sid_fnc, sid_hpr, sid_qry, SidBot, sid_adp, OWNER_ID, sid_sys, PROTECT_CONTENT
from bot.FORMATS import *
import re, io, qrcode, urllib.parse, unicodedata, asyncio, time
import random, logging, os, uuid, aiohttp, string
from asyncio import sleep
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatAction, ChatMemberStatus, ChatType
from PIL import Image
from datetime import datetime, timedelta
from pyrogram.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton, Message
from pytz import timezone
from math import ceil
from database import db
from config import sid_cfg
# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

from bot.premium_helper import *

#========================================================================#
ADMINS = sid_adp.create_admin_filter()
SHELL_ADMINS = sid_adp.create_admin_filter(shell_cmd=True)
INDIA_TZ = timezone("Asia/Kolkata")
now = datetime.now(INDIA_TZ)
PREMIUM_LOGS=sid_cfg.PREMIUM_LOGS
LOG_CHANNEL=sid_cfg.LOG_CHANNEL

#=======================================================================================================
# ADD PREMIUM COMMAND TO ADD PREMIUM USERS
#=======================================================================================================

@SidBot.on_message(filters.command("add_premium") & ADMINS)
@sid_hpr.on_log_exception
async def add_premium(client: SidBot, message: Message):
    # /add_premium user_id duration [plan_type...]
    if len(message.command) < 3:
        await message.reply_text(ADD_PREMIUM_TXT, protect_content=PROTECT_CONTENT)
        return

    try:
        user_id = int(message.command[1])
        duration_str = message.command[2]
        duration = parse_duration(duration_str)   # returns timedelta

        # Optional plan type (e.g. Silver / Gold / Platinum / Diamond / Custom)
        plan_type = None
        if len(message.command) >= 4:
            plan_type = " ".join(message.command[3:]).title()  # "gold" -> "Gold"

        current_time_ist = datetime.now(INDIA_TZ).strftime('%Y-%m-%d %I:%M:%S %p')
    except ValueError as e:
        await message.reply_text(f"❌ {str(e)}", protect_content=PROTECT_CONTENT)
        return

    user_name = await fetch_user_info(client, user_id)
    if not user_name:
        await message.reply_text(f"❌ Uɴᴀʙʟᴇ ᴛᴏ ғᴇᴛᴄʜ ᴜsᴇʀ ɪɴғᴏ ғᴏʀ ID {user_id}.")
        return

    if not await db.is_premium(user_id):
        # 🔹 Add premium using timedelta + optional plan_type
        new_expiry = await db.add_premium(user_id, duration, plan_type=plan_type)
        # Convert to IST if needed
        if new_expiry.tzinfo is None:
            expiry_ist = INDIA_TZ.localize(new_expiry)
        else:
            expiry_ist = new_expiry.astimezone(INDIA_TZ)
        expiry_str = expiry_ist.strftime('%Y-%m-%d %I:%M:%S %p IST')

        # Fallback if admin didn't give a plan
        display_plan = plan_type if plan_type else "Custom"

        await message.reply_text(
            f"✅ User <b>{user_name}</b> (ID: <code>{user_id}</code>) "
            f"ʜᴀs ʙᴇᴇɴ ɢʀᴀɴᴛᴇᴅ <b>{display_plan}</b> ᴘʀᴇᴍɪᴜᴍ ғᴏʀ <b>{duration_str}</b>.\n"
            f"📅 Aᴄᴛɪᴠᴇ ᴛɪʟʟ: <code>{expiry_str} (IST)</code>",
            protect_content=PROTECT_CONTENT
        )

        # Notify user about their premium activation
        try:
            await client.send_message(
                user_id,
                f"<blockquote>🎉 <b>Congratulations!</b></blockquote>\n"
                f"<blockquote>Yᴏᴜʀ <b>{display_plan}</b> ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀsʜɪᴘ ɪs ɴᴏᴡ ᴀᴄᴛɪᴠᴇ "
                f"ғᴏʀ <b>{duration_str}</b>. Enjoy! 🎊</blockquote>",
                disable_web_page_preview=True
            )
        except Exception as e:
            logging.warning(f"Failed to notify user {user_id}: {e}")

        # Log the admin action (PREMIUM_LOGS)
        if PREMIUM_LOGS:
            try:
                admin_user = message.from_user
                log_text = (
                    f"<b><blockquote>✦ 𝗠𝗔𝗡𝗨𝗔𝗟 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗔𝗗𝗗𝗘𝗗 ✦</b></blockquote>\n\n"
                    f"<b><blockquote>❐  Usᴇʀ:</b> <a href='tg://user?id={user_id}'>{user_name}</a> (`{user_id}`)</b></blockquote>\n"
                    f"<b><blockquote>❐  Aᴅᴅᴇᴅ Bʏ:</b> {admin_user.mention} (`{admin_user.id}`)</b></blockquote>\n"
                    f"<b><blockquote>❐  Pʟᴀɴ Tʏᴘᴇ:</b> {display_plan}</b></blockquote>\n"
                    f"<b><blockquote>❐  Dᴜʀᴀᴛɪᴏɴ:</b> {duration_str}</b></blockquote>\n"
                    f"<b><blockquote>❐  Aᴅᴅᴇᴅ Oɴ:</b> {current_time_ist}</b></blockquote>\n\n"
                    f"<b><blockquote>❐  Pʀᴇᴍɪᴜᴍ ᴀᴄᴛɪᴠᴇ ᴛɪʟʟ <b>{expiry_str}</b></blockquote>"
                )
                await client.send_message(
                    PREMIUM_LOGS,
                    log_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            except Exception as e:
                print(f"[PREMIUM_LOGS] Error: {e}")

    else:
        await message.reply_text(
            f"ℹ️ User <b>{user_name}</b> (ID: <code>{user_id}</code>) is already a premium user.",
            protect_content=PROTECT_CONTENT
        )


        
@SidBot.on_message(filters.command("rem_premium") & ADMINS)
@sid_hpr.on_log_exception
async def remove_premium(client: SidBot, message: Message):
    if len(message.command) < 2:
        await message.reply_text(REM_PREMIUM_TXT, protect_content=PROTECT_CONTENT)
        return

    argument = message.command[1].lower()
    current_time_ist = datetime.now(INDIA_TZ).strftime('%Y-%m-%d %I:%M:%S %p')
    reason = "Nᴏ sᴘᴇᴄɪғɪᴄ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ."  

    if len(message.command) > 2:
        reason = " ".join(message.command[2:])  

    if argument == "all":
        premium_users = await db.get_premium_users()
        if not premium_users:
            await message.reply_text("ℹ️ Nᴏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ғᴏᴜɴᴅ.", protect_content=PROTECT_CONTENT)
            return

        # Remove all premium users
        for user_id in premium_users.keys():
            await db.remove_premium(user_id)
            try:
                await client.send_message(
                    user_id,
                    f"❗<blockquote> <b>Yᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀsʜɪᴘ ʜᴀs ʙᴇᴇɴ ʀᴇᴠᴏᴋᴇᴅ.</b></blockquote>\n"
                    f"<blockquote>📌 <b>Rᴇᴀsᴏɴ:</b> {reason}</blockquote>\n"
                    f"<b><blockquote><a href='{ADMIN_LINK}'>✦ 💬 Cʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ Cᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴs</a></b></blockquote>",
    disable_web_page_preview=True
                )
            except Exception as e:
                logging.warning(f"Failed to notify user {user_id}: {e}")

            # Log to PREMIUM_LOGS
            if PREMIUM_LOGS:
                try:
                    log_text = (
                        f"🚫 <b>Premium Revoked</b>\n\n"
                        f"👤 <b>User ID:</b> <code>{user_id}</code>\n"
                        f"🧾 <b>Action:</b> All Users Removal\n"
                        f"📅 <b>Time:</b> {current_time_ist}\n"
                        f"📌 <b>Reason:</b> {reason}"
                    )
                    await client.send_message(PREMIUM_LOGS, log_text, parse_mode=ParseMode.HTML)
                except Exception as e:
                    print(f"[PREMIUM_LOGS] Error: {e}")

        await message.reply_text(f"<blockquote>✅ Aʟʟ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ.\n\n📌 Rᴇᴀsᴏɴ: {reason}</blockquote>", protect_content=PROTECT_CONTENT)

    else:
        try:
            user_id = int(argument)
        except ValueError:
            await message.reply_text("❌ Iɴᴠᴀʟɪᴅ ᴜsᴇʀ ID ғᴏʀᴍᴀᴛ ᴏʀ ᴜɴsᴜᴘᴘᴏʀᴛᴇᴅ ᴀʀɢᴜᴍᴇɴᴛ.", protect_content=PROTECT_CONTENT)
            return

        user_name = await fetch_user_info(client, user_id)
        if not user_name:
            await message.reply_text(f"❌ Uɴᴀʙʟᴇ ᴛᴏ ғᴇᴛᴄʜ ᴜsᴇʀ ɪɴғᴏ ғᴏʀ ID {user_id}.")
            return

        if await db.is_premium(user_id):
            await db.remove_premium(user_id)
            await message.reply_text(
                f"✅ User <b>{user_name}</b> (ID: <code>{user_id}</code>) is no longer a premium user.\n"
                f"📌 <b>Reason:</b> {reason}",
                protect_content=PROTECT_CONTENT
            )
            try:
                await client.send_message(
                    user_id,
                    f"❗<blockquote> <b>Yᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀsʜɪᴘ ʜᴀs ʙᴇᴇɴ ʀᴇᴠᴏᴋᴇᴅ.</b></blockquote>\n"
                    f"<blockquote>📌 <b>Rᴇᴀsᴏɴ:</b> {reason}</blockquote>\n"
                    f"<b><blockquote><a href='{ADMIN_LINK}'>✦ 💬 Cʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ Cᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴs</a></b></blockquote>",
    disable_web_page_preview=True
                )
            except Exception as e:
                logging.warning(f"Failed to notify user {user_id}: {e}")

            # Log to PREMIUM_LOGS
            if PREMIUM_LOGS:
                try:
                    log_text = (
                        f"🚫 <b>Premium Revoked</b>\n\n"
                        f"👤 <b>User:</b> {user_name} (<code>{user_id}</code>)\n"
                        f"🧾 <b>Action By:</b> {message.from_user.mention} (<code>{message.from_user.id}</code>)\n"
                        f"📅 <b>Time:</b> {current_time_ist}\n"
                        f"📌 <b>Reason:</b> {reason}"
                    )
                    await client.send_message(PREMIUM_LOGS, log_text, parse_mode=ParseMode.HTML)
                except Exception as e:
                    print(f"[PREMIUM_LOGS] Error: {e}")

        else:
            await message.reply_text(f"ℹ️ User <b>{user_name}</b> (ID: <code>{user_id}</code>) is not a premium user.", protect_content=PROTECT_CONTENT)


# user profile 


# Command handler
@SidBot.on_message(filters.command("premium_users") & ADMINS)
@sid_hpr.on_log_exception
async def list_premium(client: SidBot, message: Message):
    premium_users = await db.get_premium_users()
    current_page[message.chat.id] = 1 
    
    if not premium_users:
        await message.reply_text(
            "<b>ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs</b>\n\n"
            "<i>▫️ No premium users found.</i>",
            protect_content=PROTECT_CONTENT
        )
        return
    
    await show_premium_page(client, message.chat.id, premium_users, message.id)


@SidBot.on_message(filters.command("profile"))
@sid_hpr.on_log_exception
async def user_detail(bot: SidBot, message: Message):
    user = message.from_user
    user_id = user.id
    user_name = user.username or "N/A"
    full_name = user.first_name + (f" {user.last_name}" if user.last_name else "")


    # Check if user is banned
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        caption = BAN_MSG.format(
            mention=message.from_user.mention
        )

        return await message.reply_photo(
            photo=BAN_PIC,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🚨 Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ", url=ADMIN_LINK)]]
            ),
            protect_content=PROTECT_CONTENT,
        )


    wait_msg = await message.reply_text("<b>⏳ ɢᴇɴᴇʀᴀᴛɪɴɢ ᴜsᴇʀ ɪɴғᴏ...</b>", protect_content=PROTECT_CONTENT)
    await asyncio.sleep(1)
    await wait_msg.delete()

    # ============================
    # 🔹 FETCH USER PROFILE PHOTO
    # ============================
    try:
        photos = await bot.get_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            profile_photo = photos[0].file_id
        else:
            profile_photo = None
    except:
        profile_photo = None

    # ============================
    # 🔹 CHECK PREMIUM STATUS
    # ============================
    is_premium_user = await db.is_premium(user_id)

    if is_premium_user:
        # Use the IST-normalized expiry from DB
        expiry_time = await db.get_premium_expiry(user_id)
        if expiry_time:
            # Convert to IST if needed
            if expiry_time.tzinfo is None:
                expiry_ist = INDIA_TZ.localize(expiry_time)
            else:
                expiry_ist = expiry_time.astimezone(INDIA_TZ)
            expiry_text = expiry_ist.strftime('%Y-%m-%d %I:%M:%S %p IST')
        else:
            expiry_text = "Unknown"

        plan_type = await db.get_premium_plan(user_id)
        plan_text = plan_type if plan_type else "Not set"

        backup_photo = "https://telegra.ph/file/1c4fe47a4aaf5a3313f69-201afdedf112e512d3.jpg"

        profile_text = USER_INFO_TXT.format(
            name=full_name,
            username=f"@{user_name}" if user_name != "N/A" else "Not set",
            user_id=user_id,
            status="✅ Active",
            premium="✅ Yes",
            plan=plan_text,
            expiry=expiry_text
        )

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("• ғʀᴇᴇ ᴛʀɪᴀʟ •", callback_data="free_trial"), InlineKeyboardButton("• ᴜᴘɢʀᴀᴅᴇ ᴘʀᴇᴍɪᴜᴍ •", callback_data="premium")]
        ])

    else:
        backup_photo = "https://telegra.ph/file/1c4fe47a4aaf5a3313f69-201afdedf112e512d3.jpg"

        profile_text = USER_INFO_TXT.format(
            name=full_name,
            username=f"@{user_name}" if user_name != "N/A" else "Not set",
            user_id=user_id,
            status="❌ Not Active (Gareeb)",
            premium="❌ No",
            plan="N/A",
            expiry="N/A"
        )

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("• ғʀᴇᴇ ᴛʀɪᴀʟ •", callback_data="free_trial"), InlineKeyboardButton("• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •", callback_data="premium")]
        ])

    # ============================
    # 🔹 SEND PROFILE PHOTO
    # ============================
    try:
        if profile_photo:
            await message.reply_photo(profile_photo, caption=profile_text, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
        else:
            await message.reply_photo(backup_photo, caption=profile_text, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
    except:
        await message.reply_photo(backup_photo, caption=profile_text, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)


#=======================================================================================================
# REDEEM SYSTEM COMMANDS
#=======================================================================================================

@SidBot.on_message(filters.command("addredeem") & ADMINS)
@sid_hpr.on_log_exception
async def add_redeem_code(client: SidBot, message: Message):
    """Create a new redeem code for premium plans."""
    # /addredeem Silver 1month
    if len(message.command) < 3:
        await message.reply_text(ADD_REDEEM_TXT, protect_content=False)
        return

    try:
        plan_type = message.command[1].title()  # "silver" -> "Silver"
        duration_str = message.command[2]
        duration = parse_duration(duration_str)   # returns timedelta
        
        # Validate plan type
        valid_plans = ["Silver", "Gold", "Platinum", "Diamond"]
        if plan_type not in valid_plans:
            await message.reply_text(f"❌ Invalid plan type. Valid plans: {', '.join(valid_plans)}", protect_content=False)
            return
            
        current_time_ist = datetime.now(INDIA_TZ).strftime('%Y-%m-%d %I:%M:%S %p')
    except ValueError as e:
        await message.reply_text(f"❌ {str(e)}", protect_content=False)
        return

    # Generate a unique redeem code
    max_attempts = 10
    code = None
    for _ in range(max_attempts):
        new_code = generate_redeem_code()
        existing_code = await db.get_redeem_code(new_code)
        if not existing_code:
            code = new_code
            break
    
    if not code:
        await message.reply_text("❌ Failed to generate a unique redeem code. Please try again.", protect_content=PROTECT_CONTENT)
        return

    # Create the redeem code in database
    try:
        redeem_data = await db.create_redeem_code(code, plan_type, duration)
        expiry_time = redeem_data["expiry_time"]
        # Convert to IST if needed
        if expiry_time.tzinfo is None:
            expiry_ist = INDIA_TZ.localize(expiry_time)
        else:
            expiry_ist = expiry_time.astimezone(INDIA_TZ)
        expiry_date = expiry_ist.strftime('%Y-%m-%d %I:%M:%S %p IST')
        
        await message.reply_text(
            REDEEM_CODE_CREATED_TXT.format(
                plan_type=plan_type,
                duration=duration_str,
                code=code,
                expiry_date=expiry_date
            ),
            protect_content=False
        )
        
        # Log the action (PREMIUM_LOGS)
        if PREMIUM_LOGS:
            try:
                admin_user = message.from_user
                log_text = (
                    f"<b><blockquote>✦ 𝗥𝗘𝗗𝗘𝗘𝗠 𝗖𝗢𝗗𝗘 𝗖𝗥𝗘𝗔𝗧𝗘𝗗 ✦</b></blockquote>\n\n"
                    f"<b><blockquote>❐  Aᴅᴅᴇᴅ Bʏ:</b> {admin_user.mention} (`{admin_user.id}`)</b></blockquote>\n"
                    f"<b><blockquote>❐  Pʟᴀɴ Tʏᴘᴇ:</b> {plan_type}</b></blockquote>\n"
                    f"<b><blockquote>❐  Dᴜʀᴀᴛɪᴏɴ:</b> {duration_str}</b></blockquote>\n"
                    f"<b><blockquote>❐  Cᴏᴅᴇ:</b> <code>{code}</code></b></blockquote>\n"
                    f"<b><blockquote>❐  Aᴅᴅᴇᴅ Oɴ:</b> {current_time_ist}</b></blockquote>\n\n"
                    f"<b><blockquote>❐  Expiry: <b>{expiry_date} (IST)</b></blockquote>"
                )
                await client.send_message(
                    PREMIUM_LOGS,
                    log_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            except Exception as e:
                print(f"[PREMIUM_LOGS] Error: {e}")
                
    except Exception as e:
        await message.reply_text(f"❌ Failed to create redeem code: {str(e)}", protect_content=False)


@SidBot.on_message(filters.command("redeem"))
@sid_hpr.on_log_exception
async def redeem_code(client: SidBot, message: Message):
    """Allow users to redeem premium codes."""
    # /redeem ABC123XYZ
    if len(message.command) < 2:
        await message.reply_text(REDEEM_HELP_TXT, protect_content=False)
        return

    user = message.from_user
    user_id = user.id
    user_name = f"{user.first_name} {user.last_name or ''}".strip()
    code = message.command[1].upper()  # Convert to uppercase for consistency


    # Add user if not already present
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except:
            pass

    # Check if user is banned
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        caption = BAN_MSG.format(
            mention=message.from_user.mention
        )

        return await message.reply_photo(
            photo=BAN_PIC,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🚨 Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ", url=ADMIN_LINK)]]
            ),
            protect_content=PROTECT_CONTENT,
        )

    
    # Check if user is already premium (admins are always premium, so they can't redeem)
    if await db.is_premium(user_id):
        await message.reply_text("❌ You are already a premium user!", protect_content=False)
        return

    # Get redeem code details
    redeem_data = await db.get_redeem_code(code)
    if not redeem_data:
        await message.reply_text(REDEEM_INVALID_CODE_TXT, protect_content=False)
        return

    # Check if code is already used
    if redeem_data.get("is_used", False):
        await message.reply_text(REDEEM_ALREADY_USED_TXT, protect_content=False)
        return

    # Check if code is expired
    expiry_time = redeem_data.get("expiry_time")
    if expiry_time:
        # Normalize expiry_time to IST for comparison
        if expiry_time.tzinfo is None:
            expiry_ist = INDIA_TZ.localize(expiry_time)
        else:
            expiry_ist = expiry_time.astimezone(INDIA_TZ)
        now_ist = datetime.now(INDIA_TZ)
        if expiry_ist < now_ist:
            await message.reply_text(REDEEM_INVALID_CODE_TXT, protect_content=False)
            return

    # Get plan and duration details
    plan_type = redeem_data.get("plan_type", "Premium")
    # Convert duration_seconds back to timedelta
    duration_seconds = redeem_data.get("duration_seconds")
    if duration_seconds:
        duration = timedelta(seconds=duration_seconds)
    else:
        # Fallback to default 30 days if duration_seconds not found
        duration = timedelta(days=30)
    
    # Format duration for display
    duration_str = ""
    if duration.days >= 365:
        years = duration.days // 365
        duration_str = f"{years} year{'s' if years > 1 else ''}"
    elif duration.days >= 30:
        months = duration.days // 30
        duration_str = f"{months} month{'s' if months > 1 else ''}"
    elif duration.days >= 7:
        weeks = duration.days // 7
        duration_str = f"{weeks} week{'s' if weeks > 1 else ''}"
    elif duration.days > 0:
        duration_str = f"{duration.days} day{'s' if duration.days > 1 else ''}"
    else:
        hours = duration.seconds // 3600
        duration_str = f"{hours} hour{'s' if hours > 1 else ''}"

    try:
        # Activate premium for user
        new_expiry = await db.add_premium(user_id, duration, plan_type=plan_type)
        # Convert to IST if needed
        if new_expiry.tzinfo is None:
            expiry_ist = INDIA_TZ.localize(new_expiry)
        else:
            expiry_ist = new_expiry.astimezone(INDIA_TZ)
        expiry_date = expiry_ist.strftime('%Y-%m-%d %I:%M:%S %p IST')
        
        # Mark code as used
        await db.use_redeem_code(code, user_id)
        
        # Notify user
        await message.reply_text(
            REDEEM_SUCCESS_TXT.format(
                plan_type=plan_type,
                duration=duration_str,
                expiry_date=expiry_date
            ),
            protect_content=False
        )
        
        # Log the redemption (PREMIUM_LOGS)
        if PREMIUM_LOGS:
            try:
                current_time_ist = datetime.now(INDIA_TZ).strftime('%Y-%m-%d %I:%M:%S %p')
                log_text = (
                    f"<b><blockquote>✦ 𝗥𝗘𝗗𝗘𝗘𝗠 𝗖𝗢𝗗𝗘 𝗨𝗦𝗘𝗗 ✦</b></blockquote>\n\n"
                    f"<b><blockquote>❐  Usᴇʀ:</b> {user.mention} (`{user_id}`)</b></blockquote>\n"
                    f"<b><blockquote>❐  Cᴏᴅᴇ:</b> <code>{code}</code></b></blockquote>\n"
                    f"<b><blockquote>❐  Pʟᴀɴ Tʏᴘᴇ:</b> {plan_type}</b></blockquote>\n"
                    f"<b><blockquote>❐  Dᴜʀᴀᴛɪᴏɴ:</b> {duration_str}</b></blockquote>\n"
                    f"<b><blockquote>❐  Usᴇᴅ Oɴ:</b> {current_time_ist}</b></blockquote>\n\n"
                    f"<b><blockquote>❐  Pʀᴇᴍɪᴜᴍ ᴀᴄᴛɪᴠᴇ ᴛɪʟʟ <b>{expiry_date} (IST)</b></blockquote>"
                )
                await client.send_message(
                    PREMIUM_LOGS,
                    log_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            except Exception as e:
                print(f"[PREMIUM_LOGS] Error: {e}")
                
    except Exception as e:
        await message.reply_text(f"❌ Failed to activate premium: {str(e)}", protect_content=False)


#----------------------

#-----------------------

@SidBot.on_message(filters.command(["info", "userinfo", "whois"]))
@sid_hpr.on_log_exception
async def user_profile(bot: SidBot, message: Message):
    # Quick check: ensure message.from_user exists
    if not message.from_user:
        return
    
    # Wrap in try-except to handle all errors and ensure response
    try:
        # Determine target: reply > argument > sender
        target_chat = None
        target_id = None
        is_channel = False
        
        # Check if replying to a message
        if message.reply_to_message:
            if message.reply_to_message.from_user:
                target_chat = message.reply_to_message.from_user
                target_id = target_chat.id
            elif message.reply_to_message.sender_chat:
                target_chat = message.reply_to_message.sender_chat
                target_id = target_chat.id
                is_channel = True
        # Check if user/channel ID or username provided as argument
        elif len(message.command) > 1:
            try:
                query = message.command[1].strip()
                # Try to get chat by ID or username
                if query.isdigit() or (query.startswith('-') and query[1:].isdigit()):
                    target_id = int(query)
                    # Try to get as chat (for channels)
                    try:
                        target_chat = await bot.get_chat(target_id)
                        is_channel = target_chat.type in (ChatType.CHANNEL, ChatType.SUPERGROUP)
                    except:
                        # If chat fails, try as user
                        try:
                            target_chat = await bot.get_users(target_id)
                            is_channel = False
                        except:
                            raise
                elif query.startswith('@'):
                    target_chat = await bot.get_chat(query)
                    target_id = target_chat.id
                    is_channel = target_chat.type in (ChatType.CHANNEL, ChatType.SUPERGROUP)
                else:
                    # Try as chat first (for channels), then as user
                    try:
                        target_chat = await bot.get_chat(query)
                        target_id = target_chat.id
                        is_channel = target_chat.type in (ChatType.CHANNEL, ChatType.SUPERGROUP)
                    except:
                        target_chat = await bot.get_users(query)
                        target_id = target_chat.id
                        is_channel = False
            except Exception as e:
                return await message.reply_text(
                    f"❌ <b>Error:</b> Could not find user/channel. Please provide a valid ID or username.\n\n"
                    f"<b>Usage:</b>\n"
                    f"• <code>/info</code> - Your info\n"
                    f"• <code>/info @username</code> - User/channel info by username\n"
                    f"• <code>/info 123456789</code> - User/channel info by ID\n"
                    f"• Reply to a message with <code>/info</code> - Get info of replied user/channel",
                    quote=True,
                    protect_content=False
                )
        # Default to sender
        else:
            target_chat = message.from_user
            target_id = target_chat.id
            is_channel = False
        
        # If we only have ID, fetch chat/user object
        if not target_chat and target_id:
            try:
                # Try as chat first (for channels)
                try:
                    target_chat = await bot.get_chat(target_id)
                    is_channel = target_chat.type in (ChatType.CHANNEL, ChatType.SUPERGROUP)
                except:
                    # If chat fails, try as user
                    target_chat = await bot.get_users(target_id)
                    is_channel = False
            except Exception as e:
                return await message.reply_text(
                    f"❌ <b>Error:</b> Could not fetch information for ID <code>{target_id}</code>.",
                    quote=True,
                    protect_content=False
                )
        
        # Check if command sender is banned (not target) - but allow admins/owner
        sender_id = message.from_user.id
        
        # Allow owner and admins to bypass ban check
        # Check owner first (fastest check, no DB call needed)
        is_admin_or_owner = (sender_id == OWNER_ID)
        
        # Only check admin status if not owner (to avoid unnecessary DB calls)
        if not is_admin_or_owner:
            try:
                from utils import sid_db
                # Use asyncio.wait_for to add timeout to admin check
                try:
                    is_admin_or_owner = await asyncio.wait_for(
                        sid_db.admin_exists(sender_id),
                        timeout=2.0  # 2 second timeout
                    )
                except asyncio.TimeoutError:
                    logging.warning(f"[INFO_CMD] Admin check timed out for {sender_id}")
                    is_admin_or_owner = False
                except Exception as admin_check_error:
                    # If admin check fails, log but don't block - assume not admin for ban check
                    logging.warning(f"[INFO_CMD] Admin check failed for {sender_id}: {admin_check_error}")
                    is_admin_or_owner = False
            except Exception as import_error:
                # If import fails, at least check owner
                logging.error(f"[INFO_CMD] Failed to import sid_db: {import_error}")
                is_admin_or_owner = False
        
        # Only check ban list for non-admins
        if not is_admin_or_owner:
            try:
                banned_users = await db.get_ban_users()
                if sender_id in banned_users:
                    caption = BAN_MSG.format(
                        mention=message.from_user.mention
                    )

                    return await message.reply_photo(
                        photo=BAN_PIC,
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("🚨 Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ", url=ADMIN_LINK)]]
                        ),
                        protect_content=PROTECT_CONTENT,
                    )
            except Exception as ban_check_error:
                # If ban check fails, log but continue - don't block execution
                logging.warning(f"[INFO_CMD] Ban check failed for {sender_id}: {ban_check_error}")

        wait_msg = await message.reply_text("<b>⏳ ɢᴇɴᴇʀᴀᴛɪɴɢ ɪɴғᴏ...</b>", protect_content=PROTECT_CONTENT)
        await asyncio.sleep(1)
        await wait_msg.delete()

        # Fetch profile photo - use async iteration for better reliability
        profile_photo = None
        try:
            async for photo in bot.get_chat_photos(target_id, limit=1):
                profile_photo = photo.file_id
                break
        except Exception:
            profile_photo = None

        # Get chat/user info
        if is_channel:
            chat_name = target_chat.title or "N/A"
            chat_username = target_chat.username or "N/A"
            chat_id = target_id
            bio = target_chat.description or "ɴᴏ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ"
            member_count = "N/A"
            try:
                if hasattr(target_chat, 'members_count'):
                    member_count = target_chat.members_count or "N/A"
            except:
                pass
        else:
            # Set chat_id and get user info
            chat_id = target_id
            chat_name = target_chat.first_name + (f" {target_chat.last_name}" if hasattr(target_chat, 'last_name') and target_chat.last_name else "")
            chat_username = target_chat.username or "N/A"
            
            # Fetch bio safely - use get_chat() to get bio (works for both own and others)
            # This is the correct method as shown in working code
            try:
                # Use get_chat() instead of get_users() - this returns Chat object with bio
                chat_user = await bot.get_chat(chat_id)
                bio = chat_user.bio if chat_user.bio else "ɴᴏ ʙɪᴏ"
            except Exception as bio_error:
                logging.warning(f"[INFO_CMD] Bio fetch error for {chat_id}: {bio_error}")
                bio = "ɴᴏ ʙɪᴏ"
            
            member_count = "N/A"
            
            # Check if target user is admin/owner
            from utils import sid_db
            is_target_admin = False
            try:
                is_target_admin = (chat_id == OWNER_ID) or (await sid_db.admin_exists(chat_id))
            except Exception:
                is_target_admin = (chat_id == OWNER_ID)

        backup_photo = "https://telegra.ph/file/1c4fe47a4aaf5a3313f69-201afdedf112e512d3.jpg"

        # Build profile text based on user or channel
        if is_channel:
            # Channel info
            profile_text = (
                f"📢 <b>𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗜𝗡𝗙𝗢</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"➣ <b>ɴᴀᴍᴇ:</b> {chat_name}\n"
                f"➣ <b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{chat_username if chat_username != 'N/A' else 'Not set'}\n"
                f"➣ <b>ᴄʜᴀᴛ ɪᴅ:</b> <code>{chat_id}</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"➣ <b>ᴛʏᴘᴇ:</b> {'Channel' if target_chat.type == ChatType.CHANNEL else 'Supergroup'}\n"
                f"➣ <b>ᴍᴇᴍʙᴇʀs:</b> {member_count}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"➣ <b>ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:</b> <code>{bio}</code>"
            )
            reply_markup = None
        else:
            # User info - check premium
            is_premium_user = await db.is_premium(chat_id)
            
            # Add admin status indicator
            admin_status = ""
            if is_target_admin:
                if chat_id == OWNER_ID:
                    admin_status = "\n➣ <b>ʀᴏʟᴇ:</b>ᴍʏ ᴍᴀsᴛᴇʀ<"
                else:
                    admin_status = "\n➣ <b>ʀᴏʟᴇ:</b>ɢᴜᴀʀᴅɪᴀɴ"

            if is_premium_user:
                expiry_time = await db.get_premium_expiry(chat_id)
                if expiry_time:
                    # Ensure timezone-aware and convert to IST
                    if expiry_time.tzinfo is None:
                        expiry_ist = INDIA_TZ.localize(expiry_time)
                    else:
                        expiry_ist = expiry_time.astimezone(INDIA_TZ)
                    expiry_text = expiry_ist.strftime('%Y-%m-%d %I:%M:%S %p IST')
                else:
                    expiry_text = "Unknown"

                plan_type = await db.get_premium_plan(chat_id)
                plan_text = plan_type if plan_type else "Not set"

                profile_text = (
                    f"👤 <b>𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"➣ <b>ɴᴀᴍᴇ:</b> {chat_name}\n"
                    f"➣ <b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{chat_username if chat_username != 'N/A' else 'Not set'}\n"
                    f"➣ <b>ᴜsᴇʀ ɪᴅ:</b> <code>{chat_id}</code>{admin_status}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"➣ <b>sᴛᴀᴛᴜs:</b> ☑️ ᴀᴄᴛɪᴠᴇ\n"
                    f"➣ <b>ᴘʀᴇᴍɪᴜᴍ:</b> ʏᴇs ✨\n"
                    f"➣ <b>ᴘʟᴀɴ:</b> {plan_text}\n"
                    f"➣ <b>ᴇxᴘɪʀʏ:</b> {expiry_text}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"➣ <b>ʙɪᴏ:</b> <code>{bio}</code>"
                )

                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("• ғʀᴇᴇ ᴛʀɪᴀʟ •", callback_data="free_trial"), InlineKeyboardButton("• ᴜᴘɢʀᴀᴅᴇ ᴘʀᴇᴍɪᴜᴍ •", callback_data="premium")]
                ])

            else:
                profile_text = (
                    f"👤 <b>𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"➣ <b>ɴᴀᴍᴇ:</b> {chat_name}\n"
                    f"➣ <b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{chat_username if chat_username != 'N/A' else 'Not set'}\n"
                    f"➣ <b>ᴜsᴇʀ ɪᴅ:</b> <code>{chat_id}</code>{admin_status}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"➣ <b>sᴛᴀᴛᴜs:</b> ❌ ɴᴏᴛ ᴀᴄᴛɪᴠᴇ\n"
                    f"➣ <b>ᴘʀᴇᴍɪᴜᴍ:</b> ɴᴏ 🥀\n"
                    f"➣ <b>ᴘʟᴀɴ:</b> N/A\n"
                    f"➣ <b>ᴇxᴘɪʀʏ:</b> N/A\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"➣ <b>ʙɪᴏ:</b> <code>{bio}</code>"
                )

                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("• ғʀᴇᴇ ᴛʀɪᴀʟ •", callback_data="free_trial"), InlineKeyboardButton("• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •", callback_data="premium")]
                ])

        # Send message with profile photo (use backup only if no profile photo found)
        try:
            if profile_photo:
                await message.reply_photo(profile_photo, caption=profile_text, reply_markup=reply_markup, protect_content=False)
            else:
                await message.reply_photo(backup_photo, caption=profile_text, reply_markup=reply_markup, protect_content=False)
        except Exception as e:
            # If photo sending fails, try with backup
            try:
                await message.reply_photo(backup_photo, caption=profile_text, reply_markup=reply_markup, protect_content=False)
            except:
                # If photo completely fails, send as text
                await message.reply_text(profile_text, reply_markup=reply_markup, protect_content=False)
    
    except Exception as e:
        # Send error message to user instead of silently failing
        error_msg = f"❌ <b>Error:</b> An error occurred while processing your request.\n\n<code>{str(e)}</code>"
        logging.error(f"[INFO_CMD] Error in user_profile for user {message.from_user.id}: {e}", exc_info=True)
        try:
            await message.reply_text(error_msg, quote=True, protect_content=False)
        except Exception as reply_error:
            # If even error message fails, try without quote
            try:
                await message.reply_text(error_msg, protect_content=False)
            except Exception as final_error:
                # Last resort - try to send a simple message
                try:
                    await message.reply_text("❌ An error occurred. Please try again later.", quote=True, protect_content=False)
                except:
                    logging.error(f"[INFO_CMD] Failed to send any error message: {reply_error}, {final_error}")
