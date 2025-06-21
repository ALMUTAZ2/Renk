import asyncio
import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from aiogram import Bot
from aiogram.types import FSInputFile
import logging
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# قراءة إعدادات تليجرام من متغيرات البيئة أو القيم المباشرة
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7762932301:AAHkbmxRKhvjeKV9uJNfh8t382cO0Ty7i2M")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "521974594")

# التحقق من وجود البيانات
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("❌ بيانات تليجرام غير مضبوطة!")
    sys.exit(1)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def setup_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument("--user-agent=Mozilla/5.0")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد Chrome: {e}")
        sys.exit(1)

SYMBOLS = [
    {"symbol": "BTCUSDT", "name": "Bitcoin"},
    {"symbol": "ETHUSDT", "name": "Ethereum"},
    {"symbol": "BNBUSDT", "name": "BNB"},
    {"symbol": "SOLUSDT", "name": "Solana"},
    {"symbol": "XRPUSDT", "name": "XRP"}
]

async def capture_tradingview_chart(symbol_info, driver):
    symbol = symbol_info["symbol"]
    name = symbol_info["name"]

    logger.info(f"📈 معالجة {name} ({symbol})...")

    try:
        url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}&interval=1M&style=4"
        logger.info(f"🌐 الذهاب إلى: {url}")
        driver.get(url)

        # تفعيل الوضع الداكن
        logger.info("🌓 تفعيل الوضع الداكن...")
        try:
            driver.execute_script("""
                localStorage.setItem('theme', 'Dark');
                location.reload();
            """)
            time.sleep(5)
        except Exception as e:
            logger.warning(f"⚠️ فشل في تفعيل الوضع الداكن: {e}")

        logger.info("⏳ انتظار تحميل الشارت...")
        time.sleep(15)

        file_name = f"{symbol}_chart.png"

        try:
            wait = WebDriverWait(driver, 10)
            chart_area = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".layout__area--center")))
            chart_area.screenshot(file_name)
        except Exception as e:
            logger.warning(f"⚠️ فشل تحديد الشارت: {e}")
            driver.save_screenshot(file_name)

        if os.path.exists(file_name) and os.path.getsize(file_name) > 1000:
            photo = FSInputFile(file_name)

            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"📊 **شارت {name} ({symbol})**\n🔗 TradingView - Renko Chart\n📅 {time.strftime('%Y-%m-%d %H:%M UTC')}",
                parse_mode="Markdown"
            )
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption=f"📈 {name} - Renko Chart"
            )
            os.remove(file_name)
            return True
        else:
            logger.error(f"❌ فشل حفظ صورة {symbol}")
            return False

    except Exception as e:
        logger.error(f"❌ خطأ أثناء معالجة {symbol}: {e}")
        return False

async def send_summary_message(successful_charts):
    total = len(SYMBOLS)
    success = len(successful_charts)
    date = datetime.now()
    months_ar = {
        1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
        5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
        9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
    }

    summary = f"""
🌙 **التقرير الشهري - شارتات العملات**
📅 {months_ar[date.month]} {date.year}
🕒 {time.strftime('%Y-%m-%d %H:%M UTC')}

✅ تم بنجاح: {success}/{total}
❌ فشل: {total - success}/{total}

🪙 العملات التي نجحت:
{chr(10).join([f"• {c['name']} ({c['symbol']})" for c in successful_charts])}

📈 النوع: Renko - Binance - 1M
💡 المصدر: TradingView
    """.strip()

    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=summary, parse_mode="Markdown")

async def send_monthly_greeting():
    date = datetime.now()
    months_ar = {
        1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
        5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
        9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
    }

    greeting = f"""
🚀 **بدء التقرير الشهري**
📅 {months_ar[date.month]} {date.year}
🕒 {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 سيتم إرسال شارتات Renko
⏳ جارٍ التنفيذ...
    """.strip()

    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=greeting, parse_mode="Markdown")

async def main():
    logger.info("🚀 بدء التنفيذ")
    await send_monthly_greeting()

    driver = setup_chrome_driver()
    success, failed = [], []

    try:
        for i, symbol_info in enumerate(SYMBOLS):
            logger.info(f"🔄 ({i+1}/{len(SYMBOLS)}) {symbol_info['name']}")
            result = await capture_tradingview_chart(symbol_info, driver)

            if result:
                success.append(symbol_info)
            else:
                failed.append(symbol_info)

            if i < len(SYMBOLS) - 1:
                time.sleep(10)

        await send_summary_message(success)

        if failed:
            fail_msg = "\n".join([f"• {f['name']} ({f['symbol']})" for f in failed])
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"⚠️ العملات التي فشل البوت في معالجتها:\n{fail_msg}",
                parse_mode="Markdown"
            )

    except Exception as e:
        logger.error(f"❌ خطأ عام: {e}")
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f"❌ حدث خطأ:\n```\n{str(e)}\n```",
            parse_mode="Markdown"
        )

    finally:
        try:
            driver.quit()
            await bot.session.close()
        except:
            pass
        logger.info("✅ انتهى التنفيذ")

if __name__ == "__main__":
    asyncio.run(main())
