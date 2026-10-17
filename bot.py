import os
import asyncio
import csv
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, PeerFloodError, UserAlreadyParticipantError

# ================= CONFIGURATION =================
API_ID = 34964566
API_HASH = '0e1adb6860c9e1a4269c87b22ecfd46a'

# Aapka String Session
SESSION_STRING = '1BVtsOI8Bu7i5-PDX59dETiHwjjlXt33honD5lf1iZ4FIcyGHPUErGVshLvu6TvNeaN6Aj7RfyERFLGKn3Dm6omgTgkNDwgCF0EqJSL5QdvsUpCCEW8bV0l8LWAQ1Fnz8J98F32f6S8ZEkmfOFeo8mEayP9a5SX1bc8OdCVyQa9W2S8ZVm0bKbfq3BFAbFQj24dsy1rqZPIn4RCrfrLxwv2usakCuAr6ItviI3DQe3nLU7Piwbqu-kRsoYYmbZZEI3kfkJfbM2vq58SGAZLnPXvDnqyqzDxcyHDomC2-OuFB09_-oSkMxGcNvOAni08wXforrPp1wEwpsrAHm_Sbb7LX70kh93bY='

# Aapka Bot Token aur User ID
BOT_TOKEN = '8981912802:AAFsnyjNngocpEgQ82VzH-iX7cigxeJ5e6I'
YOUR_USER_ID = 7569969750 

TARGET_GROUP = 'https://t.me/wingomaxhelpline'

MIN_DELAY = 60  # 1 minute gap
MAX_DELAY = 120 # 2 minute gap
# =================================================

# Dummy Server (Render ko zinda rakhne ke liye)
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running!")

def run_dummy_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

# Telegram Clients
user_client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

@bot_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    if event.sender_id != YOUR_USER_ID:
        return
    await event.reply("✅ Bot Ready!\n\nKripya mujhe ek CSV file bhejein jisme usernames hon (ek line me ek username).")

@bot_client.on(events.NewMessage(func=lambda e: e.document is not None))
async def handle_file(event):
    if event.sender_id != YOUR_USER_ID:
        return

    await event.reply("📥 File mil gayi. Padh raha hoon...")
    
    file_path = await event.download_media()
    
    usernames = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    user = row[0].strip()
                    if user and not user.startswith('username'):
                        usernames.append(user)
    except Exception as e:
        await event.reply(f"❌ File read error: {e}")
        return

    await event.reply(f"✅ Total {len(usernames)} usernames mile. Ab add karna shuru kar raha hoon...")

    async with user_client:
        try:
            target_entity = await user_client.get_entity(TARGET_GROUP)
        except Exception as e:
            await event.reply(f"❌ Target group connect nahi hua: {e}")
            return

        added = 0
        for index, username in enumerate(usernames, 1):
            try:
                user_entity = await user_client.get_input_entity(username)
                await user_client(InviteToChannelRequest(channel=target_entity, users=[user_entity]))
                added += 1
                await event.reply(f"✅ [{index}/{len(usernames)}] Added: {username}")
                
                delay = random.randint(MIN_DELAY, MAX_DELAY)
                await asyncio.sleep(delay)

            except FloodWaitError as e:
                await event.reply(f"⏳ Flood wait: {e.seconds} sec...")
                await asyncio.sleep(e.seconds + 10)
            except UserPrivacyRestrictedError:
                await event.reply(f"❌ Privacy restricted: {username}")
            except PeerFloodError:
                await event.reply("🚫 Account ban ho gaya! 24 ghante rest karein.")
                break
            except UserAlreadyParticipantError:
                await event.reply(f"⏩ Already in group: {username}")
            except Exception as e:
                await event.reply(f"⚠️ Error: {username} - {e}")

    await event.reply(f"🎉 Kaam khatam! Total {added} members add hue.")

async def main():
    print("Bot Start Ho Raha Hai...")
    await bot_client.start(bot_token=BOT_TOKEN)
    print("Bot Online Hai! Telegram par message karein.")
    await bot_client.run_until_disconnected()

if __name__ == '__main__':
    # Web server start karein background me
    threading.Thread(target=run_dummy_server, daemon=True).start()
    # Bot start karein
    asyncio.run(main())
