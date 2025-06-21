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
    """التقاط شارت من TradingView بثيم داكن"""
    symbol = symbol_info["symbol"]
    name = symbol_info["name"]
    
    logger.info(f"📈 معالجة {name} ({symbol}) بثيم داكن...")
    
    try:
        # بناء رابط TradingView مع إعدادات Renko والثيم الداكن
        url = (f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}"
               f"&interval=1M"
               f"&style=4"  # Renko style
               f"&theme=dark"  # الثيم الداكن
               f"&hide_side_toolbar=1"  # إخفاء الشريط الجانبي
               f"&hide_top_toolbar=1"  # إخفاء الشريط العلوي
               f"&hide_legend=0"  # إظهار المفتاح
               f"&save_image=1")  # تحسين جودة الصورة
        
        logger.info(f"🌐 الذهاب إلى: {url}")
        driver.get(url)
        
        # انتظار تحميل الصفحة والثيم الداكن
        logger.info("⏳ انتظار تحميل الشارت بالثيم الداكن...")
        time.sleep(20)  # انتظار أطول للتأكد من تطبيق الثيم الداكن
        
        # محاولة تطبيق الثيم الداكن عبر JavaScript إذا لم يتم تطبيقه تلقائياً
        try:
            # تنفيذ JavaScript لضمان الثيم الداكن
            driver.execute_script("""
                // تطبيق الثيم الداكن على الجسم
                document.body.style.backgroundColor = '#131722';
                document.body.classList.add('theme-dark');
                
                // البحث عن عناصر الشارت وتطبيق الثيم الداكن
                const chartElements = document.querySelectorAll('[data-name="legend-series-item"]');
                chartElements.forEach(el => {
                    el.style.color = '#ffffff';
                });
                
                // تطبيق الثيم الداكن على منطقة الشارت
                const chartContainer = document.querySelector('.chart-container');
                if (chartContainer) {
                    chartContainer.style.backgroundColor = '#131722';
                }
                
                // تطبيق الثيم الداكن على منطقة الرسم
                const layoutCenter = document.querySelector('.layout__area--center');
                if (layoutCenter) {
                    layoutCenter.style.backgroundColor = '#131722';
                }
            """)
            logger.info("🎨 تم تطبيق الثيم الداكن عبر JavaScript")
        except Exception as js_error:
            logger.warning(f"⚠️ خطأ في تطبيق JavaScript للثيم الداكن: {js_error}")
        
        # انتظار إضافي للتأكد من تطبيق التغييرات
        time.sleep(5)
        
        # أخذ لقطة شاشة
        file_name = f"{symbol}_dark_chart.png"
        
        try:
            # محاولة العثور على منطقة الشارت
            wait = WebDriverWait(driver, 10)
            chart_area = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".layout__area--center"))
            )
            
            # أخذ لقطة شاشة للشارت فقط
            chart_area.screenshot(file_name)
            logger.info(f"📸 تم التقاط شارت {symbol} بالثيم الداكن")
            
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
                text=f"🌙 **شارت {name} ({symbol}) - ثيم داكن**\n📊 TradingView - Renko Chart\n🎨 الوضع: الثيم الداكن\n📅 {time.strftime('%Y-%m-%d %H:%M UTC')}",
                parse_mode="Markdown"
            )
            
            # إرسال الصورة
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption=f"🌙 {name} - Renko Chart (Dark Theme)"
            )
            
            # حذف الملف
            os.remove(file_name)
            logger.info(f"✅ تم إرسال شارت {symbol} بالثيم الداكن بنجاح")
            return True
            
        else:
            logger.error(f"❌ فشل في إنشاء ملف صحيح لـ {symbol}")
            return False
            
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة {symbol}: {e}")
        return False

async def send_summary_message(successful_charts):
    """إرسال رسالة ملخص شهرية"""
    try:
        total_symbols = len(SYMBOLS)
        success_count = len(successful_charts)
        
        # تحديد الشهر والسنة الحاليين
        current_date = datetime.now()
        month_names = {
            1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
            5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
            9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
        }
        current_month = month_names[current_date.month]
        current_year = current_date.year
        
        # تحديد الشهر القادم
        next_month_num = current_date.month + 1 if current_date.month < 12 else 1
        next_year = current_year if current_date.month < 12 else current_year + 1
        next_month = month_names[next_month_num]
        
        summary = f"""
🌙 **التقرير الشهري - بوت الشارتات (ثيم داكن)**
📅 الشهر: {current_month} {current_year}
🕒 التاريخ والوقت: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **نتائج هذا الشهر:**
✅ نجح: {success_count}/{total_symbols}
❌ فشل: {total_symbols - success_count}/{total_symbols}

✅ **الشارتات المُرسلة (ثيم داكن):**
{chr(10).join([f"🌙 {info['name']} ({info['symbol']})" for info in successful_charts])}

📈 **معلومات إضافية:**
• نوع الشارت: Renko Charts
• المصدر: TradingView
• البورصة: Binance
• الإطار الزمني: 1 شهر
• 🎨 الثيم: داكن (Dark Theme)

🔄 **الموعد القادم:** 
📅 أول يوم من شهر {next_month} {next_year}
🕒 الساعة 3:00 صباحاً (UTC)

🤖 **المصدر:** GitHub Actions Bot
💡 **حالة البوت:** نشط ويعمل تلقائياً بالثيم الداكن
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=summary,
            parse_mode="Markdown"
        )
        
        logger.info("📋 تم إرسال ملخص التقرير الشهري")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال الملخص: {e}")

async def send_monthly_greeting():
    """إرسال رسالة ترحيب شهرية"""
    try:
        current_date = datetime.now()
        month_names = {
            1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
            5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
            9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
        }
        current_month = month_names[current_date.month]
        current_year = current_date.year
        
        greeting = f"""
🚀 **مرحباً بك في التقرير الشهري!**

📅 **{current_month} {current_year}**
🕒 بدء التشغيل: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **ما سيتم عمله:**
• جلب شارتات Renko للعملات الرقمية
• التقاط صور عالية الجودة من TradingView
• 🌙 إرسال شارت رينكو شهري بالثيم الداكن
• 🎨 تطبيق الوضع الليلي للحصول على مظهر أنيق

⏳ **جاري المعالجة...**
يرجى الانتظار بينما نجلب أحدث الشارتات لك بالثيم الداكن
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=greeting,
            parse_mode="Markdown"
        )
        
        logger.info("👋 تم إرسال رسالة الترحيب الشهرية")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال رسالة الترحيب: {e}")

async def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل بوت الشارتات الشهري بالثيم الداكن...")
    
    # إرسال رسالة ترحيب شهرية
    await send_monthly_greeting()
    
    # إعداد Driver
    driver = setup_chrome_driver()
    successful_charts = []
    failed_charts = []
    
    try:
        # معالجة كل عملة
        for i, symbol_info in enumerate(SYMBOLS):
            logger.info(f"🔄 معالجة العملة {i+1}/{len(SYMBOLS)}: {symbol_info['name']} بالثيم الداكن")
            
            success = await capture_tradingview_chart(symbol_info, driver)
            
            if success:
                successful_charts.append(symbol_info)
            else:
                failed_charts.append(symbol_info)
            
            # انتظار بين العملات لتجنب الحظر
            if i < len(SYMBOLS) - 1:
                logger.info("⏳ انتظار بين العملات...")
                time.sleep(10)
        
        # إرسال ملخص النتائج الشهري
        await send_summary_message(successful_charts)
        
        # إرسال تفاصيل إضافية إذا كان هناك فشل
        if failed_charts:
            failed_list = "\n".join([f"• {info['name']} ({info['symbol']})" for info in failed_charts])
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"⚠️ **العملات التي فشل في معالجتها:**\n{failed_list}\n\n🔧 سيتم إعادة المحاولة في التقرير القادم",
                parse_mode="Markdown"
            )
                
    except Exception as e:
        logger.error(f"❌ خطأ عام: {e}")
        
        # إرسال رسالة خطأ مفصلة
        try:
            error_message = f"""
❌ **خطأ في البوت الشهري (ثيم داكن)**

🕒 الوقت: {time.strftime('%Y-%m-%d %H:%M UTC')}
📋 تفاصيل الخطأ:

{str(e)}
```

🔧 **الإجراءات:**
• سيتم إعادة المحاولة في الموعد القادم
• تحقق من حالة GitHub Actions
• راجع سجلات الأخطاء للمزيد من التفاصيل
            """.strip()
            
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=error_message,
                parse_mode="Markdown"
            )
        except:
            logger.error("فشل في إرسال رسالة الخطأ")
        
    finally:
        # إغلاق Driver والبوت
        try:
            driver.quit()
            logger.info("🔒 تم إغلاق Chrome Driver")
        except:
            logger.warning("⚠️ خطأ في إغلاق Driver")
            
        try:
            await bot.session.close()
            logger.info("🔒 تم إغلاق جلسة البوت")
        except:
            logger.warning("⚠️ خطأ في إغلاق جلسة البوت")
            
        logger.info("🏁 انتهى التشغيل الشهري بالثيم الداكن")

if __name__ == "__main__":
    asyncio.run(main())
