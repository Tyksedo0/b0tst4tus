import subprocess
import psutil
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = "TOKEN"

async def get_neofetch():
    try:
        result = subprocess.run(["neofetch", "--off", "--stdout"], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else "Ошибка: не удалось получить данные"
    except Exception as e:
        return f"Ошибка: {e}"

async def info(update: Update, context) -> None:
    text = await get_neofetch()
    await update.message.reply_text(f"🖥 System Info:\n```\n{text}\n```", parse_mode="Markdown")

async def status(update: Update, context) -> None:
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    
    text = (
        f"📊 *System Status*\n"
        f"CPU Load: {cpu}%\n"
        f"RAM Usage: {ram.used / (1024**3):.2f}GB / {ram.total / (1024**3):.2f}GB ({ram.percent}%)\n"
        f"Disk Usage: {disk.used / (1024**3):.2f}GB / {disk.total / (1024**3):.2f}GB ({disk.percent}%)"
    )
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def disp(update: Update, context) -> None:
    processes = sorted(psutil.process_iter(attrs=['pid', 'name', 'cpu_percent']), key=lambda p: p.info['cpu_percent'], reverse=True)[:5]
    text = "🔝 *Top Processes:*\n" + "\n".join([f"PID {p.info['pid']}: {p.info['name']} - {p.info['cpu_percent']}%" for p in processes])
    await update.message.reply_text(text, parse_mode="Markdown")

async def net(update: Update, context) -> None:
    net_io = psutil.net_io_counters()
    text = f"📡 *Network Usage:*\nUpload: {net_io.bytes_sent / (1024**2):.2f} MB\nDownload: {net_io.bytes_recv / (1024**2):.2f} MB"
    await update.message.reply_text(text, parse_mode="Markdown")

async def restart_service(update: Update, context) -> None:
    if context.args:
        service = context.args[0]
        subprocess.run(["systemctl", "restart", service])
        await update.message.reply_text(f"🔄 Сервис *{service}* перезапущен", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠ Укажите имя сервиса: `/restart nginx`", parse_mode="Markdown")

async def check_users(update: Update, context) -> None:
    result = subprocess.run(["who"], capture_output=True, text=True)
    text = f"👤 *Active Users:*\n```\n{result.stdout}\n```" if result.stdout else "Нет активных пользователей"
    await update.message.reply_text(text, parse_mode="Markdown")

async def logs(update: Update, context) -> None:
    if context.args:
        service = context.args[0]
        result = subprocess.run(["journalctl", "-u", service, "-n", "20", "--no-pager"], capture_output=True, text=True)
        text = f"📜 *Logs for {service}:*\n```\n{result.stdout[-4000:]}\n```" if result.stdout else "Логов нет"
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠ Укажите имя сервиса: `/logs nginx`", parse_mode="Markdown")

# Новая команда /uptime - время работы системы
async def uptime(update: Update, context) -> None:
    result = subprocess.run(["uptime", "-p"], capture_output=True, text=True)
    await update.message.reply_text(f"⏳ *System Uptime:*\n{result.stdout.strip()}", parse_mode="Markdown")

# Новая команда /temp - температура CPU
async def temp(update: Update, context) -> None:
    try:
        # Чтение температуры процессора
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read()) / 1000  # Температура в Цельсиях
        text = f"🌡 *CPU Temperature:* {temp}°C"
    except FileNotFoundError:
        text = "❌ Не удалось получить температуру. Возможно, ваш процессор не поддерживает этот способ."
    
    await update.message.reply_text(text, parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("disp", disp))
    app.add_handler(CommandHandler("net", net))
    app.add_handler(CommandHandler("restart", restart_service))
    app.add_handler(CommandHandler("who", check_users))
    app.add_handler(CommandHandler("logs", logs))
    app.add_handler(CommandHandler("uptime", uptime))  # Добавили uptime
    app.add_handler(CommandHandler("temp", temp))      # Добавили temp

    app.run_polling()

if __name__ == "__main__":
    main()
