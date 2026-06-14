import discord
from discord.ext import commands
import json
import os
import random
import math
import time
from datetime import datetime, timedelta

# --- ✨ CÀI ĐẶT VÀ BIẾN TOÀN CỤC ✨ ---

# Load cấu hình từ config.json
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    TOKEN = config['TOKEN']
    PREFIX = config['PREFIX']
    MESSAGE_XP_RANGE = (config['MESSAGE_XP_MIN'], config['MESSAGE_XP_MAX'])
    VOICE_XP_RANGE = (config['VOICE_XP_MIN'], config['VOICE_XP_MAX'])
    MESSAGE_COOLDOWN = config['MESSAGE_COOLDOWN']
    VOICE_COOLDOWN = config['VOICE_COOLDOWN']
except FileNotFoundError:
    print("Lỗi: Không tìm thấy file config.json! Hãy tạo file và điền thông tin.")
    exit()
except KeyError as e:
    print(f"Lỗi: Thiếu key '{e}' trong file config.json!")
    exit()

LEVEL_DATA_FILE = 'levels.json'

# Cần Intents để đọc tin nhắn và theo dõi trạng thái voice
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Dictionary lưu dữ liệu level (sẽ load từ file)
# Cấu trúc: {guild_id: {user_id: {"xp": 0, "level": 1, "last_msg_xp": 0, "last_voice_xp": 0}}}
user_levels = {}

# --- ⚙️ HÀM HỖ TRỢ LƯU/LOAD DỮ LIỆU ⚙️ ---

def load_level_data():
    global user_levels
    if os.path.exists(LEVEL_DATA_FILE):
        try:
            with open(LEVEL_DATA_FILE, 'r') as f:
                # Đảm bảo convert key từ string (trong JSON) sang int (cho guild_id, user_id)
                data = json.load(f)
                user_levels = {int(gid): {int(uid): udata for uid, udata in users.items()}
                               for gid, users in data.items()}
            print("✨ Dữ liệu level đã được tải thành công!")
        except json.JSONDecodeError:
            print(f"⚠️ Lỗi: File {LEVEL_DATA_FILE} bị lỗi hoặc trống. Bắt đầu với dữ liệu mới.")
            user_levels = {}
    else:
        print(f"File {LEVEL_DATA_FILE} không tồn tại. Sẽ tạo mới khi cần.")
        user_levels = {}

def save_level_data():
    try:
        with open(LEVEL_DATA_FILE, 'w') as f:
             # Convert keys sang string trước khi lưu vào JSON
             data_to_save = {str(gid): {str(uid): udata for uid, udata in users.items()}
                            for gid, users in user_levels.items()}
             json.dump(data_to_save, f, indent=4)
        # print("💾 Dữ liệu level đã được lưu.") # Bỏ comment nếu muốn log mỗi lần lưu
    except IOError as e:
        print(f"❌ Lỗi nghiêm trọng khi lưu dữ liệu level: {e}")

# --- 🧮 LOGIC TÍNH XP VÀ LEVEL 🧮 ---

# Công thức siêu khó: XP cần cho level n = 5 * (n^3) + 50 * n + 100
# (Có thể điều chỉnh các hệ số 5, 50, 100 để tăng/giảm độ khó)
def xp_for_level(level):
    if level <= 0: return 0
    # Dùng int() để tránh số float lớn và đảm bảo kết quả là số nguyên
    return int(5 * (level ** 3) + 50 * level + 100)

def get_user_data(guild_id, user_id):
    """Lấy hoặc tạo mới dữ liệu cho user trong guild cụ thể."""
    if guild_id not in user_levels:
        user_levels[guild_id] = {}
    if user_id not in user_levels[guild_id]:
        user_levels[guild_id][user_id] = {
            "xp": 0,
            "level": 1,
            "last_msg_xp": 0,  # Timestamp
            "last_voice_xp": 0 # Timestamp
        }
    # Đảm bảo các key cooldown luôn tồn tại
    if "last_msg_xp" not in user_levels[guild_id][user_id]:
        user_levels[guild_id][user_id]["last_msg_xp"] = 0
    if "last_voice_xp" not in user_levels[guild_id][user_id]:
        user_levels[guild_id][user_id]["last_voice_xp"] = 0
    return user_levels[guild_id][user_id]

async def add_experience(message, user_id, guild_id, xp_source):
    """Cộng XP và kiểm tra level up."""
    now = time.time()
    user_data = get_user_data(guild_id, user_id)
    
    xp_to_add = 0
    cooldown_key = ""
    cooldown_duration = 0
    
    if xp_source == "message":
        cooldown_key = "last_msg_xp"
        cooldown_duration = MESSAGE_COOLDOWN
        if now - user_data.get(cooldown_key, 0) > cooldown_duration:
             xp_to_add = random.randint(*MESSAGE_XP_RANGE)
             user_data[cooldown_key] = now # Cập nhật thời gian cooldown
    elif xp_source == "voice":
        cooldown_key = "last_voice_xp"
        cooldown_duration = VOICE_COOLDOWN
        if now - user_data.get(cooldown_key, 0) > cooldown_duration:
            xp_to_add = random.randint(*VOICE_XP_RANGE)
            user_data[cooldown_key] = now # Cập nhật thời gian cooldown
            
    if xp_to_add > 0:
        user_data["xp"] += xp_to_add
        print(f"✅ [{message.guild.name}] User {message.author.name} +{xp_to_add} XP ({xp_source}). Total: {user_data['xp']}") # Log XP
        
        leveled_up = await check_level_up(message.author, message.channel, guild_id, user_id)
        if leveled_up:
            save_level_data() # Lưu ngay khi có thay đổi level
        elif xp_source == "message": # Nếu chỉ tăng xp tin nhắn và không lên cấp, cũng nên lưu định kỳ
             # Có thể thêm logic lưu sau một số lượng tin nhắn hoặc thời gian nhất định
             # Hiện tại, để đơn giản, lưu khi có thay đổi level hoặc dùng lệnh rank
             pass
             
# --- ✨ KIỂM TRA VÀ THÔNG BÁO LEVEL UP ✨ ---

async def check_level_up(user, channel, guild_id, user_id):
    """Kiểm tra xem user có đủ XP để lên level không và gửi thông báo."""
    user_data = get_user_data(guild_id, user_id)
    current_level = user_data["level"]
    xp_needed = xp_for_level(current_level + 1)
    leveled_up = False

    while user_data["xp"] >= xp_needed:
        user_data["level"] += 1
        current_level = user_data["level"]
        # Không trừ XP khi lên cấp để tiến trình luôn tăng
        # user_data["xp"] -= xp_needed_for_prev_level # Nếu muốn reset XP về 0 mỗi level
        print(f"🎉 [{channel.guild.name}] User {user.name} ĐÃ LÊN LEVEL {current_level}!")
        await send_level_up_embed(user, channel, current_level, user_data["xp"])
        leveled_up = True
        xp_needed = xp_for_level(current_level + 1) # Tính XP cho cấp tiếp theo

    return leveled_up

# --- 🎨 THIẾT KẾ EMBED THÔNG BÁO LEVEL UP "ĐỈNH CAO" 🎨 ---
# Cậu có thể tùy chỉnh màu sắc, icon, ảnh/gif tại đây!
level_up_images = [
    "https://media.giphy.com/media/3oKIPEh5Lk3ws4s4wg/giphy.gif", # Power up chung
    "https://media.giphy.com/media/5DQdWDnoGoNe6QS6Az/giphy.gif", # Anime style power up
    "https://media.giphy.com/media/sJWNLTclcvVmw/giphy.gif",     # Anime cool pose
    "https://media.giphy.com/media/u6IxJBggWu9z6PJQXu/giphy.gif", # Neon city
    "https://media.giphy.com/media/jUSov6kRaogla/giphy.gif"      # Futuristic / Scifi
    # Thêm các link ảnh/gif khác vào đây
]

async def send_level_up_embed(user, channel, new_level, current_xp):
    xp_next = xp_for_level(new_level + 1)
    xp_prev = xp_for_level(new_level) # XP cần để đạt level hiện tại

    embed = discord.Embed(
        title=f"🌌✨ CHÚC MỪNG THĂNG HOA SỨC MẠNH! ✨🌌",
        description=f"**{user.mention}** đã phá vỡ giới hạn, đạt đến **Vùng Đất Huyền Thoại Level {new_level}!**",
        color=discord.Color.from_rgb(176, 38, 255) # Màu tím plasma (#B026FF)
    )
    
    # Hình ảnh ngầu lòi
    embed.set_thumbnail(url=user.display_avatar.url) # Avatar người dùng
    embed.set_image(url=random.choice(level_up_images)) # Ảnh/gif random

    embed.add_field(
        name="🚀 **HÀNH TRÌNH TIẾN CẤP** 🚀",
        value=f">>> `Level {new_level-1}` ➔ `✨ Level {new_level} ✨`\n"
              f">>> *\"Sức mạnh này... thật không thể tin nổi!\"*",
        inline=False
    )

    embed.add_field(
        name="📊 **THÔNG SỐ HIỆN TẠI** 📊",
        value=f"> **Tổng EXP:** `{current_xp:,}`\n" # Dấu phẩy cho dễ đọc
              f"> **EXP Cần Cho Lv.{new_level + 1}:** `{xp_next:,}`",
        inline=True
    )

    # Tạo thanh tiến trình đơn giản
    xp_in_current_level = current_xp - xp_prev
    total_xp_for_next = xp_next - xp_prev
    progress = max(0.0, min(1.0, xp_in_current_level / total_xp_for_next if total_xp_for_next > 0 else 0)) # Tránh chia cho 0
    bar_length = 15 # Độ dài thanh tiến trình
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '░' * (bar_length - filled_length) # Dùng ký tự khối và đổ bóng
    
    embed.add_field(
        name="💡 **CON ĐƯỜNG PHÍA TRƯỚC** 💡",
         value=f"> **Tiến độ Lv.{new_level + 1}:**\n`[{bar}] {progress*100:.1f}%`", # Hiển thị %
        inline=True
    )

    embed.set_footer(text=f"⚡ Kaguya Level System | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ⚡",
                     icon_url="https://img.icons8.com/fluency/48/000000/crown.png") # Có thể thay icon vương miện

    await channel.send(embed=embed)

# --- 🎧 SỰ KIỆN DISCORD 🎧 ---

@bot.event
async def on_ready():
    print(f'✅ Bot đã đăng nhập với tên {bot.user.name} (ID: {bot.user.id})')
    print(f'✨ Prefix lệnh: {PREFIX}')
    print(f'📊 Đang tải dữ liệu levels từ {LEVEL_DATA_FILE}...')
    load_level_data()
    print('------')
    await bot.change_presence(activity=discord.Game(name=f"Theo dõi XP | {PREFIX}rank"))

@bot.event
async def on_message(message):
    # Bỏ qua tin nhắn từ bot và tin nhắn riêng
    if message.author.bot or message.guild is None:
        return

    # Xử lý lệnh trước
    await bot.process_commands(message)

    # Sau đó cộng XP nếu không phải lệnh
    # Kiểm tra xem tin nhắn có bắt đầu bằng prefix không để tránh cộng xp cho lệnh
    if not message.content.startswith(PREFIX):
      await add_experience(message, message.author.id, message.guild.id, "message")

@bot.event
async def on_voice_state_update(member, before, after):
     # Bỏ qua bot
     if member.bot:
         return

     guild_id = member.guild.id

     # Phát hiện khi user vừa *vào* một kênh voice (không phải khi bị ngắt kết nối hoặc đã ở trong kênh khác rồi chuyển)
     if before.channel is None and after.channel is not None:
         # Tạo một "pseudo message" object để hàm add_experience dùng chung
         class MockMessage:
            def __init__(self, author, guild, channel):
                 self.author = author
                 self.guild = guild
                 self.channel = channel # Dùng kênh text mặc định hoặc kênh thông báo bot nếu có

         # Tìm một kênh text phù hợp để gửi thông báo nếu lên level (ví dụ: kênh hệ thống hoặc kênh đầu tiên bot thấy)
         notification_channel = member.guild.system_channel
         if notification_channel is None: # Nếu ko có kênh system, lấy kênh text đầu tiên
            text_channels = [ch for ch in member.guild.text_channels if ch.permissions_for(member.guild.me).send_messages]
            if text_channels:
                notification_channel = text_channels[0]
            else: # Ko có kênh nào để gửi thông báo
                 print(f"⚠️ Không tìm thấy kênh text phù hợp để gửi thông báo level up cho {member.name} trong {member.guild.name}")
                 return

         mock_message = MockMessage(member, member.guild, notification_channel)
         print(f"🎤 User {member.name} đã tham gia kênh voice {after.channel.name} tại {member.guild.name}.")
         await add_experience(mock_message, member.id, guild_id, "voice")


# --- 💻 LỆNH CHO NGƯỜI DÙNG 💻 ---

@bot.command(name='rank', help='Xem cấp độ và XP hiện tại của bạn.')
async def rank(ctx, member: discord.Member = None):
    """Hiển thị rank card của user hoặc người được tag."""
    user = member or ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    user_data = get_user_data(guild_id, user_id) # Đảm bảo user có trong data
    
    level = user_data["level"]
    xp = user_data["xp"]
    
    xp_curr_level = xp_for_level(level)
    xp_next_level = xp_for_level(level + 1)
    
    xp_have_in_level = xp - xp_curr_level
    xp_needed_for_next = xp_next_level - xp_curr_level

    # Tính toán xếp hạng (có thể tối ưu nếu server đông)
    leaderboard = sorted(user_levels.get(guild_id, {}).items(), key=lambda item: item[1]['xp'], reverse=True)
    rank = -1
    for i, (uid, data) in enumerate(leaderboard):
         if uid == user_id:
             rank = i + 1
             break

    # Thanh tiến trình
    progress = max(0.0, min(1.0, xp_have_in_level / xp_needed_for_next if xp_needed_for_next > 0 else 0))
    bar_length = 18
    filled_length = int(bar_length * progress)
    bar = '⚡' * filled_length + '▪' * (bar_length - filled_length) # Icon khác cho rank card

    # Embed Rank Card
    embed = discord.Embed(
        title=f"⚜️ BẢNG PHONG THẦN CỦA {user.display_name} ⚜️",
        color=discord.Color.from_rgb(0, 209, 245) # Xanh AI (#00D1F5)
    )
    embed.set_thumbnail(url=user.display_avatar.url)

    rank_text = f"**#{rank}**" if rank != -1 else "Chưa xếp hạng"
    
    embed.add_field(name="🏆 **CẤP ĐỘ (LEVEL)**", value=f"`{level}`", inline=True)
    embed.add_field(name="🔮 **KINH NGHIỆM (EXP)**", value=f"`{xp:,} / {xp_next_level:,}`", inline=True)
    embed.add_field(name="👑 **THỨ HẠNG SERVER**", value=f"{rank_text}", inline=True)

    embed.add_field(
        name="📈 **TIẾN TRÌNH LÊN CẤP**",
        value=f"`[{bar}]`\n`{xp_have_in_level:,} / {xp_needed_for_next:,} EXP tới Level {level+1}`\n`({progress*100:.1f}%)`",
        inline=False
    )

    embed.set_footer(text=f"Hệ thống Level Siêu Khó | Powered by Kaguya", icon_url=bot.user.display_avatar.url if bot.user else None)

    await ctx.send(embed=embed)
    save_level_data() # Lưu lại dữ liệu sau khi kiểm tra rank (đảm bảo dữ liệu mới nhất)

@bot.command(name='leaderboard', aliases=['lb', 'top'], help='Hiển thị bảng xếp hạng XP cao nhất server.')
async def leaderboard(ctx, top_n: int = 5):
    """Hiển thị top N người dùng có XP cao nhất."""
    guild_id = ctx.guild.id
    
    if guild_id not in user_levels or not user_levels[guild_id]:
        await ctx.send("😢 Hiện tại chưa có ai trên bảng xếp hạng cả.")
        return
        
    # Giới hạn top_n để không quá dài
    top_n = max(1, min(top_n, 15)) 

    # Sắp xếp user trong guild theo XP giảm dần
    sorted_users = sorted(user_levels[guild_id].items(), key=lambda item: item[1]['xp'], reverse=True)

    embed = discord.Embed(
        title=f"🏆 BẢNG XẾP HẠNG ANH HÙNG SERVER (TOP {top_n}) 🏆",
        description="Những chiến binh tích cực nhất vũ trụ Discord này!",
        color=discord.Color.gold() # Màu vàng gold
    )

    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None) # Icon server

    rank_list = ""
    for i, (user_id, data) in enumerate(sorted_users[:top_n]):
         member = ctx.guild.get_member(user_id)
         member_name = member.display_name if member else f"User ID: {user_id}"
         rank_icon = ["🥇", "🥈", "🥉"][i] if i < 3 else f"`#{i+1}`"
         rank_list += f"{rank_icon} **{member_name}** - Level `{data['level']}` ({data['xp']:,} XP)\n"
         
    if not rank_list:
         rank_list = "Chưa có dữ liệu."

    embed.add_field(name="✨ VINH DANH ✨", value=rank_list, inline=False)
    embed.set_footer(text="Hãy tương tác để leo rank nhé!", icon_url=bot.user.display_avatar.url if bot.user else None)

    await ctx.send(embed=embed)

# --- 🏁 CHẠY BOT 🏁 ---
try:
    bot.run(TOKEN)
except discord.errors.LoginFailure:
    print("❌ Lỗi: Token không hợp lệ. Hãy kiểm tra lại file config.json.")
except discord.errors.PrivilegedIntentsRequired:
     print("❌ Lỗi: Bot thiếu Intents cần thiết. Hãy vào Discord Developer Portal bật 'Server Members Intent' và 'Message Content Intent'.")
finally:
     # Đảm bảo lưu dữ liệu khi bot dừng (kể cả khi có lỗi)
     print("\n💾 Đang lưu dữ liệu level trước khi thoát...")
     save_level_data()
     print("✅ Lưu dữ liệu hoàn tất. Bot đã tắt.")
