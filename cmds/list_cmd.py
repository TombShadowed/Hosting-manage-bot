# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

from pyrogram import filters


def init(app, manager, OWNER_IDS):
    @app.on_message(filters.command('list'))
    async def list_cmd(client, message):
        uid = message.from_user.id
        try:
            admins = manager.get_admins()
        except Exception:
            admins = []
        if uid not in admins and uid not in OWNER_IDS:
            await message.reply_text('<b><blockquote>◉ 𝗨𝗡𝗔𝗨𝗧𝗛𝗢𝗥𝗜𝗭𝗘𝗗</blockquote></b>')
            return
        d = manager.list_bots()
        if not d:
            await message.reply_text('<b><blockquote>◉ 𝗡𝗢 𝗕𝗢𝗧𝗦 𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥𝗘𝗗</blockquote></b>')
            return
        lines = ['<b><blockquote>◉ 𝗔𝗖𝗧𝗜𝗩𝗘 𝗕𝗢𝗧 𝗟𝗜𝗦𝗧</blockquote></b>']
        for k, v in d.items():
            status = (v.get('status', 'stopped') or 'stopped').lower()
            branch = v.get('branch') or 'main'
            lines.append(f'• <b>{k}</b> — <i>{status}</i> • branch: <code>{branch}</code>')
        await message.reply_text('\n'.join(lines), disable_web_page_preview=True)
