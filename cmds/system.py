# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb
# BY OXIDISED XD, NAME HUH, BLACKITE RAVII, ShadowedTomb & REXY
import time
import psutil
from pyrogram import filters
from datetime import timedelta


_bot_start_time = time.time()

### SYSTEM INFO ###
def init(app, manager, OWNER_IDS):
    @app.on_message(filters.command('system'))
    async def system_cmd(client, message):
        uid = message.from_user.id
        try:
            admins = manager.get_admins()
        except Exception:
            admins = []
        if uid not in admins and uid not in OWNER_IDS:
            await message.reply_text('<b><blockquote>◉ 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗\n\n𝗬𝗢𝗨 𝗗𝗢 𝗡𝗢𝗧 𝗛𝗔𝗩𝗘 𝗣𝗘𝗥𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗧𝗢 𝗨𝗦𝗘 𝗧𝗛𝗜𝗦 𝗖𝗢𝗠𝗠𝗔𝗡𝗗.</blockquote></b>')
            return

        uptime_seconds = int(time.time() - _bot_start_time)
        uptime = timedelta(seconds=uptime_seconds)
        uptime_str = str(uptime).split('.')[0]

        ping_start = time.time()
        try:
            await client.get_me()
            ping_ms = (time.time() - ping_start) * 1000
        except Exception:
            ping_ms = 0

        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count(logical=True)

        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        ram_used_gb = ram.used / (1024 ** 3)
        ram_total_gb = ram.total / (1024 ** 3)

        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used_gb = disk.used / (1024 ** 3)
        disk_total_gb = disk.total / (1024 ** 3)

        status_text = (
            '<b><blockquote>◉ 𝗕𝗢𝗧 𝗦𝗬𝗦𝗧𝗘𝗠 𝗦𝗧𝗔𝗧𝗨𝗦\n\n'
            f'🤖 𝗨𝗣𝗧𝗜𝗠𝗘: {uptime_str}\n'
            f'📡 𝗣𝗜𝗡𝗚: {ping_ms:.2f} ms\n'
            f'🧠 𝗖𝗣𝗨: {cpu_percent:.2f}% ({cpu_count} 𝗰𝗼𝗿𝗲𝘀)\n'
            f'💾 𝗥𝗔𝗠: {ram_percent:.1f}% ({ram_used_gb:.2f} GB / {ram_total_gb:.2f} GB)\n'
            f'💿 𝗗𝗜𝗦𝗞: {disk_percent:.2f}% ({disk_used_gb:.2f} GB / {disk_total_gb:.2f} GB)</blockquote></b>'
        )

        await message.reply_text(status_text)

    @app.on_message(filters.command('health'))
    async def health_cmd(client, message):
        try:
            await message.reply_text('✅ <b>OK</b>')
        except Exception:
            pass

#####################################
   ###       OXIDISED XD       ###
###     GITHUB.COM/OXIDISEDXD     ###
#####################################
