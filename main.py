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

# إعداد البوت
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def setup_chrome_driver():
    """إعداد Chrome Driver لـ GitHub Actions مع تحسينات للشارتات"""
    logger.info("🔧 إعداد Chrome Driver المحسن...")
    
    chrome_options = Options()
    
    # إعدادات ضرورية لـ GitHub Actions
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")  # حجم شاشة كبير للشارتات
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    # إزالة تعطيل الصور والجافاسكريبت لأننا نحتاجها للشارتات
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # إعدادات إضافية لتحسين الأداء
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    
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

async def wait_for_chart_to_load(driver, max_wait=30):
    """انتظار تحميل الشارت بالكامل"""
    logger.info("⏳ انتظار تحميل الشارت...")
    
    try:
        # انتظار ظهور الشارت
        wait = WebDriverWait(driver, max_wait)
        
        # انتظار عنصر الشارت الرئيسي
        chart_container = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-name='legend-source-item']"))
        )
        logger.info("📊 تم العثور على حاوية الشارت")
        
        # انتظار إضافي لتحميل البيانات
        time.sleep(10)
        
        # التحقق من تحميل البيانات
        try:
            # البحث عن عناصر الشموع أو البيانات
            candles = driver.find_elements(By.CSS_SELECTOR, "[data-name='candle']")
            if len(candles) > 0:
                logger.info(f"📈 تم تحميل {len(candles)} شمعة")
            else:
                logger.info("📊 تم تحميل الشارت (نوع آخر)")
        except:
            logger.info("📊 تم تحميل الشارت")
            
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ انتهت مهلة انتظار الشارت: {e}")
        return False

async def maximize_and_center_chart(driver):
    """تكبير وتوسيط الشارت"""
    logger.info("🔍 تكبير وتوسيط الشارت...")
    
    try:
        # محاولة إخفاء الشريط الجانبي
        try:
            sidebar_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-name='toggle-sidebar']"))
            )
            driver.execute_script("arguments[0].click();", sidebar_button)
            logger.info("📱 تم إخفاء الشريط الجانبي")
            time.sleep(2)
        except:
            logger.info("📱 لم يتم العثور على زر الشريط الجانبي")
        
        # محاولة إخفاء الشريط السفلي
        try:
            bottom_panel_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-name='toggle-bottom-panel']"))
            )
            driver.execute_script("arguments[0].click();", bottom_panel_button)
            logger.info("📊 تم إخفاء الشريط السفلي")
            time.sleep(2)
        except:
            logger.info("📊 لم يتم العثور على زر الشريط السفلي")
        
        # تكبير الشارت باستخدام اختصارات لوحة المفاتيح
        try:
            # التركيز على منطقة الشارت
            chart_area = driver.find_element(By.CSS_SELECTOR, ".layout__area--center")
            chart_area.click()
            
            # استخدام اختصار التكبير
            actions = ActionChains(driver)
            actions.key_down(Keys.CONTROL).send_keys('+').key_up(Keys.CONTROL).perform()
            time.sleep(1)
            actions.key_down(Keys.CONTROL).send_keys('+').key_up(Keys.CONTROL).perform()
            time.sleep(1)
            
            logger.info("🔍 تم تكبير الشارت")
            
        except Exception as e:
            logger.warning(f"⚠️ فشل في تكبير الشارت: {e}")
        
        # محاولة ملء الشاشة
        try:
            # الضغط على F11 لملء الشاشة (قد لا يعمل في headless)
            actions = ActionChains(driver)
            actions.send_keys(Keys.F11).perform()
            time.sleep(2)
            logger.info("🖥️ تم تفعيل وضع ملء الشاشة")
        except:
            logger.info("🖥️ لم يتم تفعيل وضع ملء الشاشة")
        
        # انتظار إضافي للتأكد من التطبيق
        time.sleep(3)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في تكبير الشارت: {e}")
        return False

async def capture_optimized_chart(driver, symbol):
    """التقاط شارت محسن"""
    logger.info(f"📸 التقاط شارت محسن لـ {symbol}...")
    
    try:
        file_name = f"{symbol}_chart.png"
        
        # محاولة التقاط منطقة الشارت فقط
        try:
            # البحث عن منطقة الشارت الرئيسية
            chart_selectors = [
                ".layout__area--center",
                "[data-name='chart-container']",
                ".chart-container",
                ".tv-lightweight-charts"
            ]
            
            chart_element = None
            for selector in chart_selectors:
                try:
                    chart_element = driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"📊 تم العثور على الشارت باستخدام: {selector}")
                    break
                except:
                    continue
            
            if chart_element:
                # التقاط صورة للعنصر المحدد
                chart_element.screenshot(file_name)
                logger.info(f"📸 تم التقاط شارت {symbol} (عنصر محدد)")
            else:
                # التقاط صورة كاملة كبديل
                driver.save_screenshot(file_name)
                logger.info(f"📸 تم التقاط شارت {symbol} (شاشة كاملة)")
            
        except Exception as e:
            logger.warning(f"⚠️ فشل في التقاط العنصر المحدد، استخدام الشاشة الكاملة: {e}")
            driver.save_screenshot(file_name)
        
        # التحقق من جودة الصورة
        if os.path.exists(file_name):
            file_size = os.path.getsize(file_name)
            if file_size > 5000:  # على الأقل 5KB
                logger.info(f"✅ تم إنشاء صورة بحجم {file_size} بايت")
                return file_name
            else:
                logger.error(f"❌ حجم الصورة صغير جداً: {file_size} بايت")
                return None
        else:
            logger.error(f"❌ لم يتم إنشاء ملف الصورة")
            return None
            
    except Exception as e:
        logger.error(f"❌ خطأ في التقاط الشارت: {e}")
        return None

async def capture_tradingview_chart(symbol_info, driver):
    """التقاط شارت من TradingView مع تحسينات"""
    symbol = symbol_info["symbol"]
    name = symbol_info["name"]
    
    logger.info(f"📈 معالجة {name} ({symbol}) مع تحسينات...")
    
    try:
        # بناء رابط TradingView مع إعدادات محسنة
        url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}&interval=1M&style=4&theme=dark"
        
        logger.info(f"🌐 الذهاب إلى: {url}")
        driver.get(url)
        
        # انتظار تحميل الشارت
        chart_loaded = await wait_for_chart_to_load(driver)
        if not chart_loaded:
            logger.warning(f"⚠️ قد لا يكون الشارت محمل بالكامل لـ {symbol}")
        
        # تكبير وتوسيط الشارت
        await maximize_and_center_chart(driver)
        
        # انتظار إضافي بعد التحسينات
        time.sleep(5)
        
        # التقاط الشارت المحسن
        file_name = await capture_optimized_chart(driver, symbol)
        
        if file_name and os.path.exists(file_name):
            # إرسال الصورة
            photo = FSInputFile(file_name)
            
            # إرسال رسالة نصية أولاً
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"📊 **شارت {name} ({symbol})**\n🔗 TradingView - Renko Chart (محسن)\n📅 {time.strftime('%Y-%m-%d %H:%M UTC')}",
                parse_mode="Markdown"
            )
            
            # إرسال الصورة
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption=f"📈 {name} - شارت رينكو محسن وموسط"
            )
            
            # حذف الملف
            os.remove(file_name)
            logger.info(f"✅ تم إرسال شارت {symbol} المحسن بنجاح")
            return True
            
        else:
            logger.error(f"❌ فشل في إنشاء شارت صحيح لـ {symbol}")
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
🌙 **التقرير الشهري  - بوت شارتات RENKO **
📅 الشهر: {current_month} {current_year}
🕒 التاريخ والوقت: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **نتائج هذا الشهر:**
✅ نجح: {success_count}/{total_symbols}
❌ فشل: {total_symbols - success_count}/{total_symbols}

✅ **الشارتات المُرسلة (محسنة):**
{chr(10).join([f"• {info['name']} ({info['symbol']})" for info in successful_charts])}


📊 **معلومات إضافية:**
• نوع الشارت: Renko Charts
• المصدر: TradingView
• البورصة: Binance
• الإطار الزمني: 1 شهر
• الثيم: داكن

🔄 **الموعد القادم:** 
📅 أول يوم من شهر {next_month} {next_year}
🕒 الساعة 3:00 صباحاً (UTC)

🤖 **المصدر:** GitHub Actions Bot
💡 **حالة البوت:** نشط ويعمل تلقائياً  
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=summary,
            parse_mode="Markdown"
        )
        
        logger.info("📋 تم إرسال ملخص التقرير الشهري المحسن")
        
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
🚀 **مرحباً بك في التقرير الشهري !**

📅 **{current_month} {current_year}**
🕒 بدء التشغيل: {time.strftime('%Y-%m-%d %H:%M UTC')}



📈 **ما سيتم عمله:**
• جلب شارتات Renko 
• التقاط صور للشارت
• إرسال شارتات رينكو شهرية الى بوت تليجرام

⏳ **جاري المعالجة ...**
يرجى الانتظار بينما نجلب أحدث الشارتات لك
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=greeting,
            parse_mode="Markdown"
        )
        
        logger.info("👋 تم إرسال رسالة الترحيب الشهرية المحسنة")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال رسالة الترحيب: {e}")

async def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل بوت الشارتات الشهري المحسن...")
    
    # إرسال رسالة ترحيب شهرية
    await send_monthly_greeting()
    
    # إعداد Driver
    driver = setup_chrome_driver()
    successful_charts = []
    failed_charts = []
    
    try:
        # معالجة كل عملة
        for i, symbol_info in enumerate(SYMBOLS):
            logger.info(f"🔄 معالجة العملة {i+1}/{len(SYMBOLS)}: {symbol_info['name']}")
            
            success = await capture_tradingview_chart(symbol_info, driver)
            
            if success:
                successful_charts.append(symbol_info)
            else:
                failed_charts.append(symbol_info)
            
            # انتظار بين العملات لتجنب الحظر
            if i < len(SYMBOLS) - 1:
                logger.info("⏳ انتظار بين العملات...")
                time.sleep(15)  # انتظار أطول للتحسينات
        
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
❌ **خطأ في البوت الشهري المحسن**

🕒 الوقت: {time.strftime('%Y-%m-%d %H:%M UTC')}
📋 تفاصيل الخطأ:
```
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
            
        logger.info("🏁 انتهى التشغيل الشهري المحسن")

if __name__ == "__main__":
    asyncio.run(main())
