import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

# --- 1. DUMMY HTTP SERVER CHO RENDER ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 2. CẤU HÌNH BOT ---
TELEGRAM_TOKEN = "9123226079:AAE80zwXdY1D__getorP6tKjaj8XFq6RB4I"
WEATHER_API_KEY = "239fbaf1535ca9d7fe042649d50290b"

# Danh sách lưu trữ tất cả những người dùng đã bấm /start
active_chat_ids = set()

def get_hanoi_weather():
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
            f"🌤️ **CHÀO BUỔI SÁNG - THỜI TIẾT HÀ NỘI** 🇻🇳\n\n"
            f"🌡️ **Nhiệt độ:** {temp}°C (Cảm giác như {feels_like}°C)\n"
            f"📌 **Trạng thái:** {status_icon} {description}\n"
            f"💧 **Độ ẩm:** {humidity}%\n\n"
            f"Chúc bạn một ngày làm việc hiệu quả và tràn đầy năng lượng!"
        )
        return text
    except Exception as e:
        return f"Lỗi lấy thời tiết: {str(e)}"

# Lệnh /start khi người dùng nhắn cho bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    active_chat_ids.add(chat_id)  # Lưu lại ID của người dùng này
    
    # Gửi ngay thông tin thời tiết chào mừng
    weather_text = get_hanoi_weather()
    await update.message.reply_text(weather_text, parse_mode="Markdown")

# Hàm gửi lịch trình tự động mỗi sáng cho tất cả mọi người
async def send_daily_weather(context: ContextTypes.DEFAULT_TYPE):
    weather_text = get_hanoi_weather()
    for chat_id in active_chat_ids:
        try:
            await context.bot.send_message(chat_id=chat_id, text=weather_text, parse_mode="Markdown")
        except Exception as e:
            print(f"Không gửi được cho {chat_id}: {e}")

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    # Thiết lập lịch chạy tự động lúc 7:00 sáng hàng ngày (giờ hệ thống UTC, hoặc chỉnh múi giờ)
    scheduler = BackgroundScheduler()
    # Chạy công việc định kỳ bằng cách gọi qua job_queue của telegram bot
    # Ở đây dùng APScheduler chạy ngầm gọi trực tiếp bot gửi tin
    
    application.run_polling()

if __name__ == "__main__":
    main()
    
