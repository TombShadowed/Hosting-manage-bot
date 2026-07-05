# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

import asyncio
from pyrogram import filters, enums, types
from pyrogram.errors import PeerIdInvalid, RPCError, FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_full_name(user):
    if not user:
        return "Unknown"
    return f"{user.first_name} {user.last_name}" if user.last_name else user.first_name


def get_last_seen(status):
    if isinstance(status, str):
        status = status.replace("UserStatus.", "").lower()
    elif isinstance(status, enums.UserStatus):
        status = status.name.lower()

    return {
        "online": "✓ ᴏɴʟɪɴᴇ",
        "offline": "✘ ᴏғғʟɪɴᴇ",
        "recently": "⏱ ʀᴇᴄᴇɴᴛʟʏ",
        "last_week": "🗓 ʟᴀsᴛ ᴡᴇᴇᴋ",
        "last_month": "ೱ ʟᴀsᴛ ᴍᴏɴᴛʜ",
        "long_ago": "∞ ʟᴏɴɢ ᴛɪᴍᴇ ᴀɢᴏ"
    }.get(status, "❔ ᴜɴᴋɴᴏᴡɴ")


def init(app, manager, OWNER_IDS):
    @app.on_message(filters.command(["info", "userinfo", "whois"]))
    async def whois_handler(client, message):
        try:
            if message.reply_to_message:
                user = message.reply_to_message.from_user
            elif len(message.command) > 1:
                user = await client.get_users(message.command[1])
            else:
                user = message.from_user

            loading = await message.reply("<b>ɢᴀᴛʜᴇʀɪɴɢ ᴜsᴇʀ ɪɴғᴏ...</b>", parse_mode=enums.ParseMode.HTML)
            await asyncio.sleep(0.5)

            chat_user = await client.get_chat(user.id)

            name = get_full_name(user)
            username = f"@{user.username}" if user.username else "ɴ/ᴀ"
            bio = chat_user.bio or "ɴᴏ ʙɪᴏ"
            dc_id = getattr(user, "dc_id", "ɴ/ᴀ")
            last_seen = get_last_seen(user.status)
            lang = getattr(user, "language_code", "ɴ/ᴀ")

            text = (
                f"👤 <b>𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"➣ <b>ɴᴀᴍᴇ:</b> {name}\n"
                f"➣ <b>ᴜsᴇʀɴᴀᴍᴇ:</b> {username}\n"
                f"➣ <b>ᴜsᴇʀ ɪᴅ:</b> <code>{user.id}</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"➣ <b>sᴛᴀᴛᴜs::</b> {'ᴀᴄᴛɪᴠᴇ ✓' if user.is_verified else 'ɴᴏᴛ ᴀᴄᴛɪᴠᴇ ✗'}\n"
                f"➣ <b>ᴘʀᴇᴍɪᴜᴍ:</b> {'ʏᴇs ✓' if user.is_premium else 'ɴᴏ ✗'}\n"
                f"➣ <b>ᴘʟᴀɴ:</b> {'ʏᴇs ✓' if user.is_bot else 'N/A'}\n"
                f"➣ <b>ᴇxᴘɪʀʏ:</b> {'ʏᴇs ✓' if getattr(user, 'is_scam', False) else 'N/A'}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"➣ <b>ʙɪᴏ:</b> <code>{bio}</code>"
            )

            buttons = InlineKeyboardMarkup([[
                InlineKeyboardButton("• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ • ", url="t.me/ShadowedTomb")
            ]])

            if user.photo:
                photo = await client.download_media(user.photo.big_file_id)
                await client.edit_message_media(
                    chat_id=message.chat.id,
                    message_id=loading.id,
                    media=types.InputMediaPhoto(media=photo, caption=text, parse_mode=enums.ParseMode.HTML),
                    reply_markup=buttons
                )
            else:
                await client.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=loading.id,
                    text=text,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=buttons
                )
        except PeerIdInvalid:
            await message.reply("<b>ɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴛʜᴀᴛ ᴜsᴇʀ.</b>")
        except FloodWait as e:
            await asyncio.sleep(e.value)
            return await whois_handler(client, message)
        except RPCError as e:
            await message.reply(f"<b>ʀᴘᴄ ᴇʀʀᴏʀ:\n<code>{e}</code></b>")
        except Exception as e:
            await message.reply(f"<b>ᴇʀʀᴏʀ:\n<code>{e}</code></b>")

    @app.on_message(filters.command("id"))
    async def get_id(client, message):
        chat = message.chat
        user = message.from_user
        reply = message.reply_to_message

        text = f"**[ᴍᴇssᴀɢᴇ ɪᴅ:]({message.link})** `{message.id}`\n"
        text += f"**[ʏᴏᴜʀ ɪᴅ:](tg://user?id={user.id})** `{user.id}`\n"

        if len(message.command) == 2:
            try:
                target = message.text.split(None, 1)[1].strip()
                target_user = await client.get_users(target)
                text += f"**[ᴜsᴇʀ ɪᴅ:](tg://user?id={target_user.id})** `{target_user.id}`\n"
            except Exception:
                return await message.reply_text("**ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ.**", quote=True)

        if chat.username:
            text += f"**[ᴄʜᴀᴛ ɪᴅ:](https://t.me/{chat.username})** `{chat.id}`\n\n"
        else:
            text += f"**ᴄʜᴀᴛ ɪᴅ:** `{chat.id}`\n\n"

        if reply:
            if reply.from_user:
                text += f"**[ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪᴅ:]({reply.link})** `{reply.id}`\n"
                text += f"**[ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ:](tg://user?id={reply.from_user.id})** `{reply.from_user.id}`\n\n"

            if reply.forward_from_chat:
                text += f"ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ, {reply.forward_from_chat.title}, ʜᴀs ᴀɴ ɪᴅ ᴏғ `{reply.forward_from_chat.id}`\n\n"

            if reply.sender_chat:
                text += f"ɪᴅ ᴏғ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴄʜᴀᴛ/ᴄʜᴀɴɴᴇʟ: `{reply.sender_chat.id}`"

        await message.reply_text(
            text,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
