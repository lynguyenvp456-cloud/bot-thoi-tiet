import requests
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

# Token Bot Telegram và OpenWeatherMap API Key của bạn
TELEGRAM_TOKEN = "9123226079:AAE80zwXDy1D__gEtorP6tKjaj8XFq6rB4I"
WEATHER_API_KEY = "239fbaf1535ca9df7fe042649d50290b"

# Biến lưu trữ Chat ID của bạn (để bot biết gửi tin nhắn cho ai)
MY_CHAT_ID = None

async def get_hanoi_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Hanoi&appid={WEATHER_API_KEY}&units=metric&lang=vi"
    try:
        response = requests.get(url).json()
        if response.get("cod") != 200:
            return "Không lấy được dữ liệu thời tiết lúc này!"

        temp = round(response["main"]["temp"])
        feels_like = round(response["main"]["feels_like"])
        humidity = response["main"]["humidity"]
        description = response["weather"][0]["description"].capitalize()
        
        status_icon = "☀️" if "nắng" in description.lower() or "quang" in description.lower() else "☁️"
        if "mưa" in description.lower():
            status_icon = "🌧️"

        text = (
            f"🌅 **CHÀO BUỔI SÁNG - THỜI TIẾT HÀ NỘI** 🌅\n\n"
            f"🌡️ **Nhiệt độ:** {temp}°C (Cảm giác như {feels_like}°C)\n"
            f"{status_icon} **Trạng thái:** {description}\n"
            f"💧 **Độ ẩm:** {humidity}%\n"
            f"Have a nice day! 🚀"
        )
        return text
    except Exception as e:
        return f"Lỗi kết nối: {str(e)}"

# Hàm khi người dùng chat với bot (để bot tự động ghi nhận Chat ID của bạn)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MY_CHAT_ID
    MY_CHAT_ID = update.effective_chat.id
    await update.message.reply_text(
        "Đã kết nối thành công! Bot sẽ tự động gửi dự báo thời tiết vào 7:00 sáng hàng ngày cho bạn."
    )

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MY_CHAT_ID
    MY_CHAT_ID = update.effective_chat.id
    weather_info = await get_hanoi_weather()
    await update.message.reply_text(weather_info, parse_mode="Markdown")

# Hàm gửi tin nhắn tự động theo lịch
def job_send_morning_weather():
    if MY_CHAT_ID:
        bot = Bot(token=TELEGRAM_TOKEN)
        # Lấy thời tiết đồng bộ bằng requests
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Hanoi&appid={WEATHER_API_KEY}&units=metric&lang=vi"
        response = requests.get(url).json()
        if response.get("cod") == 200:
            temp = round(response["main"]["temp"])
            feels_like = round(response["main"]["feels_like"])
            humidity = response["main"]["humidity"]
            description = response["weather"][0]["description"].capitalize()
            
            status_icon = "☀️" if "nắng" in description.lower() or "quang" in description.lower() else "☁️"
            if "mưa" in description.lower():
                status_icon = "🌧️"

            text = (
                f"🌅 **CHÀO BUỔI SÁNG - THỜI TIẾT HÀ NỘI** 🌅\n\n"
                f"🌡️ **Nhiệt độ:** {temp}°C (Cảm giác như {feels_like}°C)\n"
                f"{status_icon} **Trạng thái:** {description}\n"
                f"💧 **Độ ẩm:** {humidity}%\n"
                f"Chúc bạn một ngày làm việc hiệu quả! 🔥"
            )
            # Gửi tin nhắn ngầm đến Telegram của bạn
            bot.send_message(chat_id=MY_CHAT_ID, text=text, parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("thoitiet", weather_command))
    
    # Cấu hình lịch chạy tự động mỗi ngày vào 7:00 sáng
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_send_morning_weather, 'cron', hour=7, minute=0)
    scheduler.start()
    
    print("Bot đã bật tính năng thông báo tự động mỗi sáng! Đang chạy...")
    app.run_polling()