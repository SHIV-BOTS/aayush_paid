import os
from pyrogram import filters
from pyrogram.types import Message
from AloneX import app, config
from AloneX.misc import SUDOERS

DOWNLOAD_DIR = "downloads"

@app.on_message(filters.command(["clean"]) & SUDOERS)
async def clean_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Ghalat Format!\nUse: `/clean 10` ya `/clean all`")
    
    arg = message.command[1].lower()
    
    if not os.path.exists(DOWNLOAD_DIR):
        return await message.reply_text("Downloads folder abhi empty hai.")

    files = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))]
    
    if not files:
        return await message.reply_text("📁 Koi downloaded songs nahi mile.")

    # Sort files by oldest first
    files.sort(key=os.path.getctime)
    
    deleted_count = 0
    
    if arg == "all":
        for f in files:
            os.remove(f)
            deleted_count += 1
        msg = f"🗑 **Cleaned All!**\nTotal {deleted_count} downloaded songs remove kar diye gaye hain."
        
    elif arg.isdigit():
        count = int(arg)
        for f in files[:count]:
            os.remove(f)
            deleted_count += 1
        msg = f"🗑 **Cleaned Oldest Songs!**\nSabse purane {deleted_count} downloaded songs remove kar diye gaye hain."
        
    else:
        return await message.reply_text("⚠️ Sirf number ya 'all' use karein. Example: `/clean 5`")

    await message.reply_text(msg)
    
    # Send report to Logger Group
    try:
        log_report = f"👤 {message.from_user.mention} ne manual cleanup run kiya.\n\n{msg}"
        await app.send_message(config.LOGGER_ID, log_report)
    except Exception as e:
        pass


@app.on_message(filters.command(["downloads"]) & SUDOERS)
async def list_downloads(client, message: Message):
    if not os.path.exists(DOWNLOAD_DIR):
        return await message.reply_text("Downloads folder exist nahi karta.")
        
    files = [f for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))]
    
    if not files:
        return await message.reply_text("📁 Server par filhal koi downloaded song nahi hai.")
        
    text = f"📁 **Total Downloaded Songs: {len(files)}**\n\n"
    
    # Message lamba na ho isliye sirf 30 dikhayenge
    for i, f in enumerate(files[:30], 1):
        text += f"**{i}.** `{f}`\n"
        
    if len(files) > 30:
        text += f"\n*...and {len(files) - 30} more.*"
        
    await message.reply_text(text)
