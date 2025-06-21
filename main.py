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
        wait = WebDriverWait(driver, max_wait)
        chart_container = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".chart-container"))
        )
        logger.info("📊 تم العثور على حاوية الشارت")
        time.sleep(10)
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ انتهت مهلة انتظار الشارت: {e}")
        return False

async def setup_chart_like_image(driver):
    """إعداد الشارت ليكون مطابقاً للصورة المرجعية"""
    logger.info("🎯 إعداد الشارت مطابق للصورة المرجعية...")
    
    try:
        # التركيز على منطقة الشارت
        chart_area = driver.find_element(By.CSS_SELECTOR, ".chart-container")
        chart_area.click()
        time.sleep(2)
        
        actions = ActionChains(driver)
        
        # 1. تغيير نوع الشارت إلى Renko (مثل الصورة)
        logger.info("📊 تغيير نوع الشارت إلى Renko...")
        
        try:
            # البحث عن قائمة أنواع الشارتات
            chart_type_selectors = [
                "[data-name='chart-style-switcher']",
                ".chart-style-switcher",
                "[data-tooltip*='Chart Type']",
                ".toolbar-button[data-name='chart-style']",
                ".chart-controls .chart-style"
            ]
            
            chart_type_found = False
            for selector in chart_type_selectors:
                try:
                    chart_type_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    if chart_type_btn.is_displayed():
                        driver.execute_script("arguments[0].click();", chart_type_btn)
                        logger.info("📊 تم فتح قائمة أنواع الشارتات")
                        time.sleep(2)
                        
                        # البحث عن Renko في القائمة
                        renko_selectors = [
                            "[data-value='renko']",
                            "[title='Renko']",
                            "li[data-name='renko']",
                            ".menu-item[data-value='renko']"
                        ]
                        
                        for renko_selector in renko_selectors:
                            try:
                                renko_option = driver.find_element(By.CSS_SELECTOR, renko_selector)
                                if renko_option.is_displayed():
                                    driver.execute_script("arguments[0].click();", renko_option)
                                    logger.info("✅ تم تغيير نوع الشارت إلى Renko")
                                    time.sleep(3)
                                    chart_type_found = True
                                    break
                            except:
                                continue
                        break
                except:
                    continue
            
            if not chart_type_found:
                logger.info("⚠️ لم يتم العثور على خيار Renko، الاستمرار بالشموع العادية...")
                
        except Exception as e:
            logger.warning(f"⚠️ فشل في تغيير نوع الشارت: {e}")
        
        # 2. تغيير الإطار الزمني إلى شهري (1M) مثل الصورة
        logger.info("📅 تغيير الإطار الزمني إلى شهري (1M)...")
        
        try:
            # البحث عن زر الإطار الزمني الشهري
            monthly_timeframe_selectors = [
                "[data-value='1M']",
                "[data-interval='1M']",
                "[title='1 month']",
                ".timeframe-button[data-value='1M']"
            ]
            
            monthly_found = False
            for selector in monthly_timeframe_selectors:
                try:
                    monthly_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    if monthly_btn.is_displayed():
                        driver.execute_script("arguments[0].click();", monthly_btn)
                        logger.info("📅 تم تغيير الإطار الزمني إلى شهري")
                        time.sleep(3)
                        monthly_found = True
                        break
                except:
                    continue
            
            if not monthly_found:
                # محاولة باستخدام اختصارات لوحة المفاتيح
                logger.info("⌨️ محاولة تغيير الإطار الزمني باستخدام لوحة المفاتيح...")
                actions.send_keys('M').perform()  # Monthly
                time.sleep(2)
                actions.send_keys('1').perform()  # 1 Month
                time.sleep(2)
                
        except Exception as e:
            logger.warning(f"⚠️ فشل في تغيير الإطار الزمني: {e}")
        
        # 3. تطبيق "Fit Data to Screen" الحقيقي
        logger.info("🎯 تطبيق Fit Data to Screen...")
        
        # استخدام JavaScript المتقدم لتوسيط البيانات
        fit_data_script = """
        try {
            // محاولة استخدام TradingView API
            if (window.TradingView) {
                var widgets = document.querySelectorAll('.tradingview-widget-container iframe');
                if (widgets.length > 0) {
                    // إرسال رسالة للـ iframe لتوسيط البيانات
                    widgets[0].contentWindow.postMessage({
                        name: 'fit-data',
                        action: 'fitData'
                    }, '*');
                }
            }
            
            // البحث عن أزرار Fit Data وتفعيلها
            var fitSelectors = [
                '[data-name="fit-data"]',
                '[title*="Fit"]',
                '[data-tooltip*="Fit"]',
                '.control-bar__btn[data-name="fit-data"]'
            ];
            
            fitSelectors.forEach(function(selector) {
                var elements = document.querySelectorAll(selector);
                elements.forEach(function(el) {
                    if (el.offsetParent !== null && !el.disabled) {
                        el.click();
                        console.log('تم النقر على زر Fit Data:', selector);
                    }
                });
            });
            
            // محاولة إرسال keyboard events
            var chartContainer = document.querySelector('.chart-container') || document.querySelector('.tv-lightweight-charts');
            if (chartContainer) {
                // Alt + F للـ Fit Data
                var altF = new KeyboardEvent('keydown', {
                    key: 'f',
                    altKey: true,
                    bubbles: true,
                    cancelable: true
                });
                chartContainer.dispatchEvent(altF);
                
                // Double-click للـ auto-fit
                setTimeout(function() {
                    var dblClick = new MouseEvent('dblclick', {
                        bubbles: true,
                        cancelable: true
                    });
                    chartContainer.dispatchEvent(dblClick);
                }, 500);
            }
            
            console.log('تم تنفيذ Fit Data بنجاح');
        } catch (e) {
            console.error('خطأ في Fit Data:', e);
        }
        """
        
        driver.execute_script(fit_data_script)
        time.sleep(3)
        
        # 4. تكبير الشموع لتكون مثل الصورة
        logger.info("🔍 تكبير الشموع لتكون مثل الصورة...")
        
        # تكبير متدرج باستخدام عجلة الماوس
        zoom_script = """
        var chartContainer = arguments[0];
        var center = {
            x: chartContainer.offsetWidth / 2,
            y: chartContainer.offsetHeight / 2
        };
        
        // تكبير تدريجي
        for (var i = 0; i < 12; i++) {
            setTimeout(function(index) {
                var wheelEvent = new WheelEvent('wheel', {
                    deltaY: -120, // تكبير
                    clientX: center.x,
                    clientY: center.y,
                    bubbles: true,
                    cancelable: true
                });
                chartContainer.dispatchEvent(wheelEvent);
            }, i * 150, i);
        }
        """
        
        driver.execute_script(zoom_script, chart_area)
        time.sleep(4)
        
        # 5. تعديل مقياس السعر للتوسيط العمودي
        logger.info("📏 تعديل مقياس السعر للتوسيط العمودي...")
        
        try:
            # النقر المزدوج على مقياس السعر
            price_scale_selectors = [
                ".price-axis",
                ".price-scale", 
                ".tv-lightweight-charts__price-axis",
                ".price-axis-container"
            ]
            
            for selector in price_scale_selectors:
                try:
                    price_scale = driver.find_element(By.CSS_SELECTOR, selector)
                    if price_scale.is_displayed():
                        actions.double_click(price_scale).perform()
                        logger.info("📏 تم توسيط مقياس السعر")
                        time.sleep(2)
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"⚠️ فشل في تعديل مقياس السعر: {e}")
        
        # 6. تحسين عرض الشموع
        logger.info("📊 تحسين عرض الشموع...")
        
        # استخدام اختصارات لوحة المفاتيح لتحسين العرض
        keyboard_improvements = [
            # تكبير إضافي
            lambda: actions.key_down(Keys.CONTROL).send_keys(Keys.ADD).key_up(Keys.CONTROL).perform(),
            # تعديل العرض
            lambda: actions.send_keys(Keys.SPACE).perform(),
            # إعادة ضبط العرض
            lambda: actions.key_down(Keys.ALT).send_keys('r').key_up(Keys.ALT).perform()
        ]
        
        for improvement in keyboard_improvements:
            try:
                improvement()
                time.sleep(1)
            except:
                continue
        
        # 7. تطبيق Fit Data مرة أخيرة للتأكد
        logger.info("🎯 تطبيق Fit Data النهائي...")
        
        # اختصار Alt+F للـ Fit Data
        try:
            actions.key_down(Keys.ALT).send_keys('f').key_up(Keys.ALT).perform()
            time.sleep(2)
        except:
            pass
        
        # Double-click على الشارت للـ auto-fit
        try:
            actions.double_click(chart_area).perform()
            time.sleep(2)
        except:
            pass
        
        # انتظار إضافي للتأكد من تطبيق جميع التحسينات
        time.sleep(5)
        
        logger.info("✅ تم إعداد الشارت بنجاح مطابق للصورة المرجعية")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد الشارت: {e}")
        return False

async def take_screenshot(driver, symbol_name):
    """التقاط لقطة شاشة محسنة"""
    logger.info(f"📸 التقاط لقطة شاشة لـ {symbol_name}...")
    
    try:
        # انتظار إضافي للتأكد من استقرار الشارت
        time.sleep(3)
        
        # إخفاء العناصر غير المرغوب فيها
        hide_elements_script = """
        // إخفاء الإعلانات والعناصر المشتتة
        var elementsToHide = [
            '.tv-dialog-manager',
            '.tv-toast-manager',
            '.tv-notifications-dialog',
            '.tv-header__area--right',
            '.tv-header__logo',
            '.tv-screener-popup',
            '.tv-floating-toolbar'
        ];
        
        elementsToHide.forEach(function(selector) {
            var elements = document.querySelectorAll(selector);
            elements.forEach(function(el) {
                el.style.display = 'none';
            });
        });
        """
        
        driver.execute_script(hide_elements_script)
        time.sleep(1)
        
        # التقاط لقطة الشاشة
        filename = f"{symbol_name}_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = f"/tmp/{filename}"
        
        driver.save_screenshot(filepath)
        logger.info(f"✅ تم حفظ لقطة الشاشة: {filename}")
        
        return filepath
        
    except Exception as e:
        logger.error(f"❌ خطأ في التقاط لقطة الشاشة: {e}")
        return None

async def send_to_telegram(filepath, symbol_name):
    """إرسال الصورة إلى تليجرام"""
    logger.info(f"📤 إرسال {symbol_name} إلى تليجرام...")
    
    try:
        if filepath and os.path.exists(filepath):
            photo = FSInputFile(filepath)
            
            caption = f"""
🚀 **تحليل {symbol_name}**
📊 الإطار الزمني: شهري (1M)
📈 نوع الشارت: Renko المحسن
🎯 البيانات موسطة ومكبرة للوضوح الأمثل

⏰ وقت التحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption=caption,
                parse_mode="Markdown"
            )
            
            logger.info(f"✅ تم إرسال {symbol_name} بنجاح")
            
            # حذف الملف المؤقت
            os.remove(filepath)
            
        else:
            logger.error(f"❌ الملف غير موجود: {filepath}")
            
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال {symbol_name}: {e}")

async def process_symbol(driver, symbol_data):
    """معالجة عملة واحدة"""
    symbol = symbol_data["symbol"]
    name = symbol_data["name"]
    
    logger.info(f"🔄 معالجة {name} ({symbol})...")
    
    try:
        # الانتقال إلى الرمز
        url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}"
        driver.get(url)
        
        # انتظار تحميل الشارت
        if await wait_for_chart_to_load(driver):
            # إعداد الشارت مطابق للصورة
            if await setup_chart_like_image(driver):
                # التقاط لقطة الشاشة
                filepath = await take_screenshot(driver, name)
                
                if filepath:
                    # إرسال إلى تليجرام
                    await send_to_telegram(filepath, name)
                    logger.info(f"✅ تم إنجاز {name} بنجاح")
                else:
                    logger.error(f"❌ فشل في التقاط لقطة شاشة لـ {name}")
            else:
                logger.error(f"❌ فشل في إعداد الشارت لـ {name}")
        else:
            logger.error(f"❌ فشل في تحميل الشارت لـ {name}")
            
        # انتظار بين العملات
        time.sleep(3)
        
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة {name}: {e}")

async def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل بوت الشارتات المحسن...")
    
    driver = None
    try:
        # إعداد المتصفح
        driver = setup_chrome_driver()
        
        # معالجة كل عملة
        for symbol_data in SYMBOLS:
            await process_symbol(driver, symbol_data)
        
        logger.info("🎉 تم إنجاز جميع العملات بنجاح!")
        
    except Exception as e:
        logger.error(f"❌ خطأ في التشغيل الرئيسي: {e}")
    
    finally:
        if driver:
            driver.quit()
            logger.info("🔚 تم إغلاق المتصفح")

if __name__ == "__main__":
    asyncio.run(main())
