import asyncio
import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aiogram import Bot
from aiogram.types import FSInputFile
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إعدادات تليجرام (مضمنة مباشرة)
TELEGRAM_BOT_TOKEN = "7762932301:AAHkbmxRKhvjeKV9uJNfh8t382cO0Ty7i2M"
TELEGRAM_CHAT_ID = "521974594"

# التحقق من وجود البيانات
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("❌ بيانات تليجرام غير مضبوطة!")
    sys.exit(1)

# إعداد البوت
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def setup_chrome_driver():
    """إعداد Chrome Driver لـ GitHub Actions"""
    logger.info("🔧 إعداد Chrome Driver...")
    
    chrome_options = Options()
    
    # إعدادات ضرورية لـ GitHub Actions
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("✅ تم إعداد Chrome Driver بنجاح")
        return driver
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد Chrome: {e}")
        sys.exit(1)

# العملات المطلوبة
SYMBOLS = [
    {"symbol": "BTCUSDT", "name": "Bitcoin"},
    {"symbol": "ETHUSDT", "name": "Ethereum"},
    {"symbol": "BNBUSDT", "name": "BNB"},
    {"symbol": "SOLUSDT", "name": "Solana"},
    {"symbol": "XRPUSDT", "name": "XRP"}
]

async def capture_tradingview_chart(symbol_info, driver):
    """التقاط شارت من TradingView"""
    symbol = symbol_info["symbol"]
    name = symbol_info["name"]
    
    logger.info(f"📈 معالجة {name} ({symbol})...")
    
    try:
        # بناء رابط TradingView مع إعدادات Renko
        url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}&interval=1M&style=12"
        
        logger.info(f"🌐 الذهاب إلى: {url}")
        driver.get(url)
        
        # انتظار تحميل الصفحة
        logger.info("⏳ انتظار تحميل الشارت...")
        time.sleep(15)  # انتظار أطول للتأكد من التحميل
        
        # أخذ لقطة شاشة
        file_name = f"{symbol}_chart.png"
        
        try:
            # محاولة العثور على منطقة الشارت
            wait = WebDriverWait(driver, 10)
            chart_area = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".layout__area--center"))
            )
            
            # أخذ لقطة شاشة للشارت فقط
            chart_area.screenshot(file_name)
            logger.info(f"📸 تم التقاط شارت {symbol}")
            
        except Exception as e:
            logger.warning(f"⚠️ فشل في العثور على الشارت، أخذ لقطة شاشة كاملة: {e}")
            driver.save_screenshot(file_name)
        
        # التحقق من وجود الملف
        if os.path.exists(file_name) and os.path.getsize(file_name) > 1000:
            # إرسال الصورة
            photo = FSInputFile(file_name)
            
            # إرسال رسالة نصية أولاً
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"📊 **شارت {name} ({symbol})**\n🔗 TradingView - Renko Chart\n📅 {time.strftime('%Y-%m-%d %H:%M UTC')}",
                parse_mode="Markdown"
            )
            
            # إرسال الصورة
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption=f"📈 {name} - Renko Chart"
            )
            
            # حذف الملف
            os.remove(file_name)
            logger.info(f"✅ تم إرسال شارت {symbol} بنجاح")
            return True
            
        else:
            logger.error(f"❌ فشل في إنشاء ملف صحيح لـ {symbol}")
            return False
            
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة {symbol}: {e}")
        return False

async def send_summary_message(successful_charts):
    """إرسال رسالة ملخص"""
    try:
        total_symbols = len(SYMBOLS)
        success_count = len(successful_charts)
        
        summary = f"""
🤖 **تقرير بوت الشارتات**
📅 التاريخ: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **النتائج:**
✅ نجح: {success_count}/{total_symbols}
❌ فشل: {total_symbols - success_count}/{total_symbols}

✅ **الشارتات المرسلة:**
{chr(10).join([f"• {info['name']}" for info in successful_charts])}

🔄 **التشغيل التالي:** خلال 6 ساعات
🤖 **المصدر:** GitHub Actions Bot
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=summary,
            parse_mode="Markdown"
        )
        
        logger.info("📋 تم إرسال ملخص التقرير")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال الملخص: {e}")

async def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل بوت الشارتات...")
    
    # إرسال رسالة بداية
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="🚀 **بدء تشغيل بوت الشارتات**\n⏳ جاري جلب الشارتات من TradingView...",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال رسالة البداية: {e}")
    
    # إعداد Driver
    driver = setup_chrome_driver()
    successful_charts = []
    
    try:
        # معالجة كل عملة
        for i, symbol_info in enumerate(SYMBOLS):
            success = await capture_tradingview_chart(symbol_info, driver)
            
            if success:
                successful_charts.append(symbol_info)
            
            # انتظار بين العملات لتجنب الحظر
            if i < len(SYMBOLS) - 1:
                logger.info("⏳ انتظار بين العملات...")
                time.sleep(10)
        
        # إرسال ملخص النتائج
        await send_summary_message(successful_charts)
                
    except Exception as e:
        logger.error(f"❌ خطأ عام: {e}")
        
        # إرسال رسالة خطأ
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"❌ **خطأ في البوت**\n```{str(e)}```",
                parse_mode="Markdown"
            )
        except:
            pass
        
    finally:
        # إغلاق Driver والبوت
        driver.quit()
        await bot.session.close()
        logger.info("🏁 انتهى التشغيل")

if __name__ == "__main__":
    asyncio.run(main())
