# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic
# ALONE-CODER

import os
import time
import shutil
import asyncio
from pathlib import Path

from AloneX import logger, app, config

DOWNLOAD_DIR = "downloads"

def ensure_dirs():
    """
    Ensure that the necessary directories exist.
    """
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg must be installed and accessible in the system PATH.")

    for d in ["cache", DOWNLOAD_DIR]:
        Path(d).mkdir(parents=True, exist_ok=True)
    logger.info("Cache directories updated.") 


async def auto_clean_downloads():
    """
    Background task to monitor storage:
    - 1 Week se purani files delete karega.
    - Agar storage 90% full ho gayi, toh 10 sabse purane songs delete karega.
    """
    while True:
        try:
            # Har 10 minute mein storage check karega (warna 1 week wait karne me storage full ho sakti hai)
            await asyncio.sleep(600) 
            
            if not os.path.exists(DOWNLOAD_DIR):
                continue

            current_time = time.time()
            one_week_ago = current_time - (7 * 24 * 60 * 60) # 7 Days in seconds
            
            # Saari downloaded files ki list nikal rahe hain
            files = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))]
            if not files:
                continue

            # 1. DELETE 1 WEEK OLD FILES
            weekly_deleted = 0
            for file_path in files:
                if os.path.getctime(file_path) < one_week_ago:
                    os.remove(file_path)
                    weekly_deleted += 1
            
            if weekly_deleted > 0:
                log_msg = f"🗑 **Auto-Clean (1 Week Old):**\nSuccessfully deleted {weekly_deleted} old audio files."
                logger.info(log_msg)
                try:
                    await app.send_message(config.LOGGER_ID, log_msg)
                except:
                    pass

            # 2. CHECK STORAGE & DELETE OLDEST 10 IF FULL
            total, used, free = shutil.disk_usage(DOWNLOAD_DIR)
            percent_used = (used / total) * 100
            
            if percent_used > 90.0:  # Agar 90% se zyada full hai
                # Update file list after weekly deletion
                files = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))]
                
                # File creation time ke hisaab se sort karo (Purani files sabse pehle)
                files.sort(key=os.path.getctime)
                
                oldest_deleted = 0
                # Sabse purani 10 files uda do
                for file_path in files[:10]:
                    os.remove(file_path)
                    oldest_deleted += 1
                    
                if oldest_deleted > 0:
                    warn_msg = f"⚠️ **Storage Almost Full ({percent_used:.1f}%)!**\nDeleted the {oldest_deleted} oldest downloaded songs to free up space."
                    logger.warning(warn_msg)
                    try:
                        await app.send_message(config.LOGGER_ID, warn_msg)
                    except:
                        pass

        except Exception as e:
            logger.error(f"[Auto-Clean] Error during cleanup: {e}")
