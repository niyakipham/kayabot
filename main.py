# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import random
import os
from dotenv import load_dotenv
import datetime
import discord.utils 

load_dotenv()
TOKEN = os.getenv('WE') 
PREFIX = "!" 


WELCOME_CHANNEL_ID = 1367429679765524522     
GOODBYE_CHANNEL_ID = 1367425504038223872   


THEME_COLORS = {
    "welcome": discord.Color.from_rgb(176, 38, 255),   
    "goodbye": discord.Color.from_rgb(0, 209, 245),    
    "info": discord.Color.from_rgb(224, 224, 255),       
    "error": discord.Color.from_rgb(255, 80, 80)         
}


WELCOME_IMAGES = [
    "https://i.pinimg.com/originals/3d/5c/9b/3d5c9b194b47a5ccba39d775c064f9a3.gif", # Kaguya vẫy tay
    "https://media1.tenor.com/m/a-bs_QvS9y0AAAAC/kaguya-shinomiya-kaguya.gif",      # Kaguya nghĩ ngợi
    "https://media1.tenor.com/m/Is1zQZhpiIYAAAAd/kaguya-sama-love-is-war.gif",     # Chika dance chào mừng?
    "https://i.pinimg.com/originals/ee/79/16/ee7916d3557829b955c03bbef045ce4a.gif", # Ishigami + Kaguya
]

GOODBYE_IMAGES = [
    "https://media1.tenor.com/m/Hlr5Gbl_iBUAAAAC/kaguya-sama-love-is-war-kaguya.gif", # Kaguya buồn bã nhẹ
    "https://media1.tenor.com/m/F8v1RNbDIwEAAAAC/kaguya-sama-anime.gif",          # Kaguya "Hmph"
    "https://i.pinimg.com/originals/bc/7f/1a/bc7f1abd12c2e14b6c87373ac78730bf.gif", # Kaguya quay đi
]


WELCOME_MESSAGES = [
    "*Ara ara~* Một thành viên ưu tú mới, **{member.mention}**, đã gia nhập **{guild.name}**! Chào mừng đến với Hội Học Sinh... à nhầm, server của chúng ta! ✨",
    "Hệ thống phân tích ghi nhận tín hiệu mới! Chào mừng **{member.mention}** đến với chiến trường tình yêu... ý tôi là **{guild.name}**! (*≧ω≦*)",
    "**O kawaii koto...** (**{member.mention}** thật đáng yêu khi tham gia **{guild.name}** đó). Hiện tại server có `{guild.member_count}` thành viên thiên tài!",
    "✦・━━━━━━━━━・✦\nChào mừng **{member.mention}**! Đừng ngần ngại thể hiện trí tuệ của bạn tại **{guild.name}**. Cánh cửa tri thức luôn rộng mở!",
    "💌 Một lá thư mời đã được chấp nhận! **{member.mention}** chính thức là thành viên của **{guild.name}**. Hãy cùng nhau tạo nên những điều tuyệt vời!",
]

GOODBYE_MESSAGES = [
    "Thật đáng tiếc... **{member.display_name}** đã quyết định rời khỏi **{guild.name}**. Mong rằng đây không phải là lời tạm biệt cuối cùng... 💔",
    "Hệ thống lưu trữ đã cập nhật: **{member.display_name}** không còn là thành viên của **{guild.name}**. Chúc bạn thành công trên con đường mình đã chọn. 🌠",
    "Một vì sao đã rời khỏi bầu trời **{guild.name}**... Tạm biệt nhé, **{member.display_name}**. Đừng quên những kỷ niệm ở đây.",
    "✦・━━━━━━━━━・✦\nNhiệm vụ của **{member.display_name}** tại **{guild.name}** đã hoàn thành. Cảm ơn vì đã đồng hành. *Sayonara~*",
    "Có vẻ như **{member.display_name}** đã tìm thấy một 'chiến trường' khác thú vị hơn. Tạm biệt và hẹn gặp lại (nếu duyên phận cho phép) tại **{guild.name}**.",
]


intents = discord.Intents.default()
intents.guilds = True   
intents.members = True  


bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None, 
    case_insensitive=True 
)


@bot.event
async def on_ready():
    print("+" + "="*48 + "+")
    print(f"| {'🤖 KAGUYA BOT ĐÃ KÍCH HOẠT 🤖':^48} |")
    print("+" + "="*48 + "+")
    print(f"| 👤 Tên Bot: {bot.user.name} ({bot.user.id})")
    print(f"| 📚 discord.py Version: {discord.__version__}")
    print(f"| 📡 Trạng Thái: Online & Sẵn sàng quan sát!")
    print(f"| ✨ Prefix Lệnh: {PREFIX}")
    print("+" + "="*48 + "+")
    
    activity = discord.Activity(
        name=f"Quan sát {len(bot.guilds)} server | {PREFIX}help",
        type=discord.ActivityType.watching # Hoạt động "Watching"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("🎭 Trạng thái hoạt động đã được cập nhật.")
    print("+" + "="*48 + "+")



@bot.event
async def on_member_join(member: discord.Member):
    print(f"📥 [Gia Nhập] {member} ({member.id}) vừa đặt chân đến server {member.guild.name} ({member.guild.id})")
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    guild = member.guild

    if not welcome_channel:
        print(f"❌ [Lỗi Chào Mừng] Không tìm thấy kênh chào mừng ID: {WELCOME_CHANNEL_ID} tại server {guild.name}")
        
        try:
            if guild.owner:
                await guild.owner.send(
                    f"⚠️ **Kaguya Bot Cảnh Báo [Server: {guild.name}]** ⚠️\n"
                    f"Không thể tìm thấy kênh chào mừng đã cấu hình (ID: `{WELCOME_CHANNEL_ID}`). "
                    f"Thành viên `{member.name}` vừa tham gia nhưng tôi không thể gửi lời chào. "
                    f"Vui lòng kiểm tra lại `WELCOME_CHANNEL_ID` trong mã nguồn của bot."
                )
                print(f"📢 Đã gửi cảnh báo thiếu kênh chào mừng đến Owner: {guild.owner.name}")
        except discord.Forbidden:
            print("🚫 [Lỗi Quyền] Không thể gửi DM cảnh báo kênh chào mừng cho chủ server.")
        except Exception as e:
            print(f"💥 [Lỗi Bất Ngờ] Khi gửi cảnh báo kênh chào mừng: {e}")
        return

    
    try:
        embed = discord.Embed(
            
            description=random.choice(WELCOME_MESSAGES).format(member=member, guild=guild),
            color=THEME_COLORS["welcome"],
            timestamp=discord.utils.utcnow() 
        )

        embed.set_author(
            name=f"Thông Báo Gia Nhập Hội Đồng Tối Cao Tại {guild.name.upper()}",
            icon_url=guild.icon.url if guild.icon else bot.user.display_avatar.url
        )
        
        embed.set_thumbnail(url=member.display_avatar.url) # Dùng display_avatar để lấy avatar mặc định nếu cần

        
        if WELCOME_IMAGES:
            embed.set_image(url=random.choice(WELCOME_IMAGES))

        
        embed.add_field(name="✨ Danh Hiệu Thành Viên", value=f"```{member}```", inline=True)
        embed.add_field(name="🆔 Mã Định Danh Duy Nhất", value=f"```{member.id}```", inline=True)
        embed.add_field(name="📊 Tổng Số Thiên Tài Hiện Tại", value=f"```{guild.member_count}```", inline=True)


        creation_info = f"{discord.utils.format_dt(member.created_at, style='f')} ({discord.utils.format_dt(member.created_at, style='R')})"
        embed.add_field(name="⏳ Tài Khoản Tạo Vào Lúc", value=creation_info, inline=False)


        embed.set_footer(
            text="Được gửi bởi Kaguya Shinomiya | Trợ lý hoàn hảo của bạn",
            icon_url=bot.user.display_avatar.url
        )

        await welcome_channel.send(content=f"Chào mừng chiến binh mới {member.mention}! 💖", embed=embed)
        print(f"✅ [Chào Mừng] Đã gửi lời chào đến {member.name} tại kênh #{welcome_channel.name}")

    except discord.Forbidden:
        print(f"🚫 [Lỗi Quyền] Bot không có quyền gửi tin nhắn/embed vào kênh chào mừng #{welcome_channel.name} ({WELCOME_CHANNEL_ID})")
        
    except discord.HTTPException as e:
        print(f"💥 [Lỗi HTTP] Khi gửi lời chào: Mã lỗi {e.status}, {e.text}")
    except Exception as e:
        print(f"💥 [Lỗi Bất Ngờ] Khi xử lý sự kiện on_member_join cho {member.name}: {e}")


@bot.event
async def on_member_remove(member: discord.Member):
    print(f"🚪 [Rời Đi] {member} ({member.id}) đã rời khỏi server {member.guild.name} ({member.guild.id})")
    goodbye_channel = bot.get_channel(GOODBYE_CHANNEL_ID)
    guild = member.guild

    if not goodbye_channel:
        print(f"❌ [Lỗi Tạm Biệt] Không tìm thấy kênh tạm biệt ID: {GOODBYE_CHANNEL_ID} tại server {guild.name}")
        
        try:
            if guild.owner:
                await guild.owner.send(
                     f"⚠️ **Kaguya Bot Cảnh Báo [Server: {guild.name}]** ⚠️\n"
                    f"Không thể tìm thấy kênh tạm biệt đã cấu hình (ID: `{GOODBYE_CHANNEL_ID}`). "
                    f"Thành viên `{member.name}` vừa rời đi nhưng tôi không thể gửi thông báo. "
                    f"Vui lòng kiểm tra lại `GOODBYE_CHANNEL_ID` trong mã nguồn của bot."
                )
                print(f"📢 Đã gửi cảnh báo thiếu kênh tạm biệt đến Owner: {guild.owner.name}")
        except discord.Forbidden:
            print("🚫 [Lỗi Quyền] Không thể gửi DM cảnh báo kênh tạm biệt cho chủ server.")
        except Exception as e:
            print(f"💥 [Lỗi Bất Ngờ] Khi gửi cảnh báo kênh tạm biệt: {e}")
        return

    try:
        embed = discord.Embed(
            description=random.choice(GOODBYE_MESSAGES).format(member=member, guild=guild),
            color=THEME_COLORS["goodbye"],
            timestamp=discord.utils.utcnow()
        )

        # --- Phần Trang Trí ---
        embed.set_author(
            name=f"Thông Báo Cập Nhật Thành Viên Tại {guild.name.upper()}",
            icon_url=guild.icon.url if guild.icon else bot.user.display_avatar.url
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        if GOODBYE_IMAGES:
            embed.set_image(url=random.choice(GOODBYE_IMAGES))

        
        embed.add_field(name="👤 Tài Khoản Đã Rời Đi", value=f"```{member}```", inline=True)
        embed.add_field(name="🏷️ Tên Hiển Thị Cuối Cùng", value=f"```{member.display_name}```", inline=True)

        
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        role_str = ", ".join(roles) if roles else "_Không có vai trò đặc biệt_"
        
        if len(role_str) > 1020:
            role_str = role_str[:1020] + "..."
        embed.add_field(name="🎭 Vai Trò Đã Có", value=role_str, inline=False)

        

        embed.set_footer(
            text="Kaguya ghi nhận sự thay đổi này.",
            icon_url=bot.user.display_avatar.url
        )

        # --- Gửi Thông Điệp ---
        await goodbye_channel.send(embed=embed)
        print(f"✅ [Tạm Biệt] Đã gửi lời tiễn biệt {member.name} tại kênh #{goodbye_channel.name}")

    except discord.Forbidden:
        print(f"🚫 [Lỗi Quyền] Bot không có quyền gửi tin nhắn/embed vào kênh tạm biệt #{goodbye_channel.name} ({GOODBYE_CHANNEL_ID})")
    except discord.HTTPException as e:
        print(f"💥 [Lỗi HTTP] Khi gửi lời tạm biệt: Mã lỗi {e.status}, {e.text}")
    except Exception as e:
         print(f"💥 [Lỗi Bất Ngờ] Khi xử lý sự kiện on_member_remove cho {member.name}: {e}")



if __name__ == "__main__":
    print("\n" + "="*15 + " KIỂM TRA CẤU HÌNH BAN ĐẦU " + "="*15)
    valid_config = True

    
    if not TOKEN:
        print("🚨 [LỖI CẤU HÌNH] BIẾN MÔI TRƯỜNG 'DISCORD_BOT_TOKEN' KHÔNG TỒN TẠI HOẶC RỖNG!")
        print("   Vui lòng tạo file `.env` và thêm dòng: DISCORD_BOT_TOKEN=TOKEN_CUA_BAN")
        valid_config = False
    elif not isinstance(TOKEN, str) or len(TOKEN) < 50: # Token thường khá dài
        print(f"⚠️ [CẢNH BÁO CẤU HÌNH] Token '{TOKEN[:10]}...' trông có vẻ không hợp lệ. Vui lòng kiểm tra lại.")



    if not isinstance(WELCOME_CHANNEL_ID, int) or WELCOME_CHANNEL_ID <= 0:
        print("🚨 [LỖI CẤU HÌNH] `WELCOME_CHANNEL_ID` phải là một số ID kênh Discord hợp lệ (số nguyên dương).")
        valid_config = False
    if not isinstance(GOODBYE_CHANNEL_ID, int) or GOODBYE_CHANNEL_ID <= 0:
         print("🚨 [LỖI CẤU HÌNH] `GOODBYE_CHANNEL_ID` phải là một số ID kênh Discord hợp lệ (số nguyên dương).")
         valid_config = False

    if WELCOME_CHANNEL_ID == 123456789012345678 or GOODBYE_CHANNEL_ID == 123456789012345678:
         print("️️️⚠️ [LƯU Ý CẤU HÌNH] Bạn đang sử dụng ID kênh mặc định ví dụ (123...678).")
         print("   Hãy chắc chắn thay thế bằng ID kênh thực tế trên server của bạn, nếu không bot sẽ không gửi được thông báo.")

    print("="*58 + "\n")

    if not valid_config:
        print("🚫 Bot không thể khởi động do lỗi cấu hình nghiêm trọng. Vui lòng kiểm tra lại các thông báo lỗi ở trên.")
    else:
        try:
            print(f"📡 Đang dùng Token: '{TOKEN[:5]}...{TOKEN[-5:]}' để kết nối đến Discord...")
            bot.run(TOKEN)
        except discord.errors.LoginFailure:
            print("💥 [LỖI ĐĂNG NHẬP] Token không hợp lệ! Hãy kiểm tra kỹ token trong file `.env` và trên Discord Developer Portal.")
            print("   Đảm bảo bạn đã copy đúng TOÀN BỘ token.")
        except discord.errors.PrivilegedIntentsRequired:
             print("💥 [LỖI QUYỀN INTENTS] Bot thiếu quyền Intents cần thiết (Đặc biệt là SERVER MEMBERS INTENT).")
             print("   Bot cần quyền này để nhận diện thành viên ra/vào server.")
             print("   Vui lòng truy cập trang quản lý bot của bạn trên Discord Developer Portal:")
             print("     https://discord.com/developers/applications -> [Tên Bot Của Bạn] -> Bot")
             print("     -> Kéo xuống mục 'Privileged Gateway Intents'")
             print("     -> Bật [ON] công tắc 'SERVER MEMBERS INTENT'")
             print("     -> Lưu thay đổi và khởi động lại bot.")
        except Exception as e:
             print(f"💥 [LỖI KHỞI ĐỘNG KHÁC] Một lỗi không mong muốn đã xảy ra: {e}")
             print(f"   Loại lỗi: {type(e).__name__}")
             
