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
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
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
            EC.presence_of_element_located((By.CSS_SELECTOR, ".chart-container"))
        )
        logger.info("📊 تم العثور على حاوية الشارت")
        
        # انتظار إضافي لتحميل البيانات
        time.sleep(10)
        
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ انتهت مهلة انتظار الشارت: {e}")
        return False

async def center_and_zoom_chart_data(driver):
    """توسيط وتكبير بيانات الشارت (الشموع)"""
    logger.info("🎯 توسيط وتكبير بيانات الشارت...")
    
    try:
        # التركيز على منطقة الشارت
        chart_area = driver.find_element(By.CSS_SELECTOR, ".chart-container")
        chart_area.click()
        time.sleep(2)
        
        # 1. تكبير الشموع باستخدام عجلة الماوس (محاكاة)
        logger.info("🔍 تكبير الشموع...")
        actions = ActionChains(driver)
        
        # تحريك الماوس لوسط الشارت
        actions.move_to_element(chart_area).perform()
        time.sleep(1)
        
        # تكبير باستخدام اختصارات لوحة المفاتيح
        for i in range(5):  # تكبير 5 مرات
            actions.key_down(Keys.CONTROL).send_keys('+').key_up(Keys.CONTROL).perform()
            time.sleep(0.5)
        
        logger.info("✅ تم تكبير الشموع")
        
        # 2. توسيط البيانات باستخدام "Fit Data to Screen"
        logger.info("🎯 توسيط البيانات في الشاشة...")
        
        try:
            # محاولة استخدام اختصار لوحة المفاتيح لتوسيط البيانات
            # Ctrl+Alt+R عادة يقوم بـ Reset/Fit to screen في TradingView
            actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('r').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
            time.sleep(2)
            
            # أو محاولة استخدام مفاتيح أخرى
            # Home key لبداية البيانات ثم End للنهاية
            actions.send_keys(Keys.HOME).perform()
            time.sleep(1)
            actions.send_keys(Keys.END).perform()
            time.sleep(1)
            
            logger.info("✅ تم توسيط البيانات")
            
        except Exception as e:
            logger.warning(f"⚠️ فشل في توسيط البيانات تلقائياً: {e}")
        
        # 3. محاولة استخدام أزرار TradingView للتوسيط
        try:
            # البحث عن زر "Fit Data to Screen" أو ما شابه
            fit_buttons = [
                "[data-name='fit-data']",
                "[title*='fit']",
                "[title*='Fit']",
                ".control-bar__btn[title*='fit']"
            ]
            
            for selector in fit_buttons:
                try:
                    fit_button = driver.find_element(By.CSS_SELECTOR, selector)
                    driver.execute_script("arguments[0].click();", fit_button)
                    logger.info(f"🎯 تم النقر على زر التوسيط: {selector}")
                    time.sleep(2)
                    break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"⚠️ لم يتم العثور على زر التوسيط: {e}")
        
        # 4. تعديل مقياس الوقت لإظهار المزيد من البيانات
        try:
            logger.info("📊 تعديل مقياس الوقت...")
            
            # استخدام اختصارات لتغيير الإطار الزمني
            # الضغط على مفاتيح الأرقام لتغيير الإطار الزمني
            actions.send_keys('4').perform()  # 4H timeframe
            time.sleep(2)
            actions.send_keys('D').perform()  # Daily timeframe
            time.sleep(2)
            
            logger.info("✅ تم تعديل مقياس الوقت")
            
        except Exception as e:
            logger.warning(f"⚠️ فشل في تعديل مقياس الوقت: {e}")
        
        # 5. تحسين عرض الشموع
        try:
            logger.info("🕯️ تحسين عرض الشموع...")
            
            # محاولة تغيير نوع الشارت إذا لزم الأمر
            # الضغط على Alt+1 للشموع اليابانية
            actions.key_down(Keys.ALT).send_keys('1').key_up(Keys.ALT).perform()
            time.sleep(2)
            
            logger.info("✅ تم تحسين عرض الشموع")
            
        except Exception as e:
            logger.warning(f"⚠️ فشل في تحسين عرض الشموع: {e}")
        
        # انتظار إضافي للتأكد من تطبيق جميع التغييرات
        time.sleep(5)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في توسيط وتكبير الشارت: {e}")
        return False

async def maximize_chart_area(driver):
    """تكبير منطقة الشارت وإخفاء العناصر غير الضرورية"""
    logger.info("🖥️ تكبير منطقة الشارت...")
    
    try:
        # إخفاء الشريط الجانبي الأيسر
        try:
            # محاولة عدة طرق لإخفاء الشريط الجانبي
            sidebar_selectors = [
                "[data-name='toggle-sidebar']",
                ".icon-button[title*='sidebar']",
                ".sidebar-toggle"
            ]
            
            for selector in sidebar_selectors:
                try:
                    sidebar_button = driver.find_element(By.CSS_SELECTOR, selector)
                    driver.execute_script("arguments[0].click();", sidebar_button)
                    logger.info("📱 تم إخفاء الشريط الجانبي")
                    time.sleep(2)
                    break
                except:
                    continue
        except:
            logger.info("📱 لم يتم العثور على زر الشريط الجانبي")
        
        # إخفاء الشريط السفلي
        try:
            bottom_selectors = [
                "[data-name='toggle-bottom-panel']",
                ".bottom-panel-toggle",
                ".icon-button[title*='bottom']"
            ]
            
            for selector in bottom_selectors:
                try:
                    bottom_button = driver.find_element(By.CSS_SELECTOR, selector)
                    driver.execute_script("arguments[0].click();", bottom_button)
                    logger.info("📊 تم إخفاء الشريط السفلي")
                    time.sleep(2)
                    break
                except:
                    continue
        except:
            logger.info("📊 لم يتم العثور على زر الشريط السفلي")
        
        # إخفاء شريط الأدوات العلوي إن أمكن
        try:
            # استخدام CSS لإخفاء عناصر غير ضرورية
            hide_elements_script = """
            // إخفاء عناصر غير ضرورية
            var elementsToHide = [
                '.header-chart-panel',
                '.chart-page-header',
                '.top-toolbar',
                '.chart-toolbar'
            ];
            
            elementsToHide.forEach(function(selector) {
                var elements = document.querySelectorAll(selector);
                elements.forEach(function(el) {
                    el.style.display = 'none';
                });
            });
            """
            
            driver.execute_script(hide_elements_script)
            logger.info("🎨 تم إخفاء العناصر الإضافية")
            time.sleep(2)
            
        except Exception as e:
            logger.warning(f"⚠️ فشل في إخفاء العناصر الإضافية: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في تكبير منطقة الشارت: {e}")
        return False

async def capture_optimized_chart(driver, symbol):
    """التقاط شارت محسن ومتوسط"""
    logger.info(f"📸 التقاط شارت محسن ومتوسط لـ {symbol}...")
    
    try:
        file_name = f"{symbol}_chart.png"
        
        # محاولة التقاط منطقة الشارت فقط
        try:
            # البحث عن منطقة الشارت الرئيسية
            chart_selectors = [
                ".chart-container",
                ".layout__area--center", 
                "[data-name='chart-container']",
                ".tv-lightweight-charts",
                ".chart-widget"
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
    """التقاط شارت من TradingView مع توسيط وتكبير الشموع"""
    symbol = symbol_info["symbol"]
    name = symbol_info["name"]
    
    logger.info(f"📈 معالجة {name} ({symbol}) مع توسيط وتكبير الشموع...")
    
    try:
        # بناء رابط TradingView مع إعدادات محسنة
        # استخدام إطار زمني أكبر لإظهار المزيد من البيانات
        url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}&interval=1D&style=1&theme=dark"
        
        logger.info(f"🌐 الذهاب إلى: {url}")
        driver.get(url)
        
        # انتظار تحميل الشارت
        chart_loaded = await wait_for_chart_to_load(driver)
        if not chart_loaded:
            logger.warning(f"⚠️ قد لا يكون الشارت محمل بالكامل لـ {symbol}")
        
        # تكبير منطقة الشارت وإخفاء العناصر غير الضرورية
        await maximize_chart_area(driver)
        
        # توسيط وتكبير بيانات الشارت (الشموع)
        await center_and_zoom_chart_data(driver)
        
        # انتظار إضافي بعد جميع التحسينات
        time.sleep(8)
        
        # التقاط الشارت المحسن
        file_name = await capture_optimized_chart(driver, symbol)
        
        if file_name and os.path.exists(file_name):
            # إرسال الصورة
            photo = FSInputFile(file_name)
            
            # إرسال رسالة نصية أولاً
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"📊 **شارت {name} ({symbol})**\n🎯 شموع متوسطة ومكبرة\n📅 {time.strftime('%Y-%m-%d %H:%M UTC')}",
                parse_mode="Markdown"
            )
            
            # إرسال الصورة
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption=f"📈 {name} - شموع متوسطة ومكبرة تلقائياً"
            )
            
            # حذف الملف
            os.remove(file_name)
            logger.info(f"✅ تم إرسال شارت {symbol} المتوسط والمكبر بنجاح")
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
🌙 **التقرير الشهري - شموع متوسطة ومكبرة**
📅 الشهر: {current_month} {current_year}
🕒 التاريخ والوقت: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **نتائج هذا الشهر:**
✅ نجح: {success_count}/{total_symbols}
❌ فشل: {total_symbols - success_count}/{total_symbols}

✅ **الشارتات المُرسلة (متوسطة ومكبرة):**
{chr(10).join([f"• {info['name']} ({info['symbol']})" for info in successful_charts])}

🎯 **التحسينات المطبقة:**
• 🔍 تكبير الشموع 5 مرات تلقائياً
• 🎯 توسيط البيانات في الشاشة
• 📊 إطار زمني يومي لوضوح أفضل
• 🖥️ تكبير منطقة الشارت
• 🎨 إخفاء العناصر المشتتة

📈 **معلومات إضافية:**
• نوع الشارت: شموع يابانية
• المصدر: TradingView
• البورصة: Binance
• الإطار الزمني: يومي
• الثيم: داكن

🔄 **الموعد القادم:** 
📅 أول يوم من شهر {next_month} {next_year}
🕒 الساعة 3:00 صباحاً (UTC)

🤖 **المصدر:** GitHub Actions Bot (شموع متوسطة)
💡 **حالة البوت:** نشط مع توسيط وتكبير تلقائي
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
🚀 **مرحباً بك في التقرير الشهري - شموع متوسطة!**

📅 **{current_month} {current_year}**
🕒 بدء التشغيل: {time.strftime('%Y-%m-%d %H:%M UTC')}

🎯 **التحسينات الجديدة للشموع:**
• 🔍 تكبير الشموع 5 مرات تلقائياً
• 🎯 توسيط البيانات في وسط الشاشة
• 📊 إطار زمني يومي للوضوح
• 🖥️ تكبير منطقة الشارت
• 🎨 إخفاء العناصر المشتتة
• 🌙 ثيم داكن للراحة

📈 **ما سيتم عمله:**
• جلب شارتات الشموع اليابانية
• توسيط وتكبير الشموع تلقائياً
• التقاط صور عالية الجودة ومتوسطة
• إرسال شارتات شموع واضحة ومكبرة

⏳ **جاري المعالجة مع التوسيط والتكبير...**
يرجى الانتظار بينما نجلب أحدث الشارتات المتوسطة والمكبرة لك
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
    logger.info("🚀 بدء تشغيل بوت الشارتات الشهري - شموع متوسطة ومكبرة...")
    
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
                time.sleep(15)
        
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
❌ **خطأ في البوت الشهري - شموع متوسطة**

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
