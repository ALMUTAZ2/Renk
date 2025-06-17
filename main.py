import asyncio
import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from aiogram import Bot
from aiogram.types import FSInputFile
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إعدادات تليجرام
TELEGRAM_BOT_TOKEN = "7762932301:AAHkbmxRKhvjeKV9uJNfh8t382cO0Ty7i2M"
TELEGRAM_CHAT_ID = "521974594"

# إعداد البوت
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def setup_chrome_driver():
    """إعداد Chrome Driver محسن"""
    logger.info("🔧 إعداد Chrome Driver...")
    
    chrome_options = Options()
    
    # إعدادات Chrome محسنة
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        logger.info("✅ تم إعداد Chrome Driver بنجاح")
        return driver
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد Chrome: {e}")
        sys.exit(1)

# قائمة العملات
SYMBOLS = [
    {"symbol": "BTCUSDT", "name": "Bitcoin"},
    {"symbol": "ETHUSDT", "name": "Ethereum"},
    {"symbol": "BNBUSDT", "name": "BNB"},
    {"symbol": "SOLUSDT", "name": "Solana"},
    {"symbol": "XRPUSDT", "name": "XRP"}
]

async def wait_for_chart_load(driver, timeout=30):
    """انتظار تحميل الشارت بالكامل"""
    logger.info("⏳ انتظار تحميل الشارت...")
    
    wait = WebDriverWait(driver, timeout)
    
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas")))
        time.sleep(8)  # انتظار أطول
        
        try:
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".tv-spinner")))
        except:
            pass
        
        time.sleep(5)
        logger.info("✅ تم تحميل الشارت")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ انتهت مهلة انتظار تحميل الشارت: {e}")
        return False

async def setup_renko_candlesticks(driver, symbol):
    """إعداد شارت Renko Candlesticks بدقة"""
    try:
        logger.info(f"🕯️ إعداد Renko Candlesticks لـ {symbol}...")
        
        wait = WebDriverWait(driver, 25)
        
        # انتظار تحميل الصفحة
        await wait_for_chart_load(driver)
        
        # 1. إغلاق النوافذ المنبثقة
        await close_popups(driver)
        
        # 2. تغيير نوع الشارت إلى Renko
        renko_success = await change_to_renko_chart(driver)
        if not renko_success:
            logger.warning("⚠️ فشل في تغيير نوع الشارت إلى Renko")
            return False
        
        # 3. تغيير إلى Renko Candlesticks (الشمعات)
        candlesticks_success = await enable_renko_candlesticks(driver)
        if not candlesticks_success:
            logger.warning("⚠️ فشل في تفعيل Renko Candlesticks")
        
        # 4. تغيير الفريم إلى شهري
        timeframe_success = await change_to_monthly_timeframe(driver)
        if not timeframe_success:
            logger.warning("⚠️ فشل في تغيير الفريم إلى شهري")
        
        # 5. تنظيف الشارت
        await clean_chart_interface(driver)
        
        # انتظار إضافي لتحميل الشارت الجديد
        await wait_for_chart_load(driver, 20)
        
        logger.info("✅ تم إعداد Renko Candlesticks بنجاح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد Renko Candlesticks: {e}")
        return False

async def close_popups(driver):
    """إغلاق النوافذ المنبثقة"""
    try:
        close_selectors = [
            "[data-name='close']",
            ".tv-dialog__close",
            ".js-dialog__close",
            "[aria-label='Close']",
            ".tv-button--ghost",
            "[data-role='button'][aria-label*='close']"
        ]
        
        for selector in close_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(1)
            except:
                continue
    except Exception as e:
        logger.warning(f"⚠️ خطأ في إغلاق النوافذ: {e}")

async def change_to_renko_chart(driver):
    """تغيير نوع الشارت إلى Renko"""
    try:
        logger.info("📊 تغيير نوع الشارت إلى Renko...")
        
        # البحث عن زر نوع الشارت
        chart_type_selectors = [
            "[data-name='chart-style-switcher']",
            "[data-tooltip*='Chart']",
            ".chart-style-switcher",
            "[title*='Chart']"
        ]
        
        chart_type_btn = None
        for selector in chart_type_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        chart_type_btn = element
                        break
                if chart_type_btn:
                    break
            except:
                continue
        
        if not chart_type_btn:
            logger.warning("⚠️ لم يتم العثور على زر نوع الشارت")
            return False
        
        # النقر على زر نوع الشارت
        driver.execute_script("arguments[0].scrollIntoView(true);", chart_type_btn)
        time.sleep(2)
        driver.execute_script("arguments[0].click();", chart_type_btn)
        time.sleep(5)
        
        # البحث عن خيار Renko
        renko_selectors = [
            "[data-name='renko']",
            "[title*='Renko']",
            "//div[contains(text(), 'Renko')]",
            "//span[contains(text(), 'Renko')]",
            "//button[contains(text(), 'Renko')]"
        ]
        
        for selector in renko_selectors:
            try:
                if selector.startswith("//"):
                    renko_elements = driver.find_elements(By.XPATH, selector)
                else:
                    renko_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for renko_element in renko_elements:
                    if renko_element.is_displayed():
                        driver.execute_script("arguments[0].click();", renko_element)
                        time.sleep(8)
                        logger.info("✅ تم تغيير نوع الشارت إلى Renko")
                        return True
            except:
                continue
        
        logger.warning("⚠️ لم يتم العثور على خيار Renko")
        return False
        
    except Exception as e:
        logger.error(f"❌ خطأ في تغيير نوع الشارت: {e}")
        return False

async def enable_renko_candlesticks(driver):
    """تفعيل Renko Candlesticks (الشمعات)"""
    try:
        logger.info("🕯️ تفعيل Renko Candlesticks...")
        
        # البحث عن إعدادات الشارت أو زر الإعدادات
        settings_selectors = [
            "[data-name='chart-properties']",
            "[data-name='properties']",
            "[title*='Properties']",
            "[title*='Settings']",
            ".chart-controls-bar button",
            "[data-tooltip*='Properties']"
        ]
        
        settings_btn = None
        for selector in settings_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        settings_btn = element
                        break
                if settings_btn:
                    break
            except:
                continue
        
        if settings_btn:
            # فتح إعدادات الشارت
            driver.execute_script("arguments[0].click();", settings_btn)
            time.sleep(5)
            
            # البحث عن خيار Candlesticks أو Body
            candlestick_selectors = [
                "//label[contains(text(), 'Candle')]",
                "//label[contains(text(), 'Body')]",
                "//span[contains(text(), 'Candle')]",
                "//span[contains(text(), 'Body')]",
                "[data-name*='candle']",
                "[data-name*='body']",
                "input[type='checkbox']"
            ]
            
            for selector in candlestick_selectors:
                try:
                    if selector.startswith("//"):
                        elements = driver.find_elements(By.XPATH, selector)
                    else:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed():
                            # إذا كان checkbox، تأكد من تفعيله
                            if element.tag_name == 'input' and element.get_attribute('type') == 'checkbox':
                                if not element.is_selected():
                                    driver.execute_script("arguments[0].click();", element)
                                    time.sleep(2)
                            else:
                                driver.execute_script("arguments[0].click();", element)
                                time.sleep(2)
                            
                            logger.info("✅ تم تفعيل Renko Candlesticks")
                            
                            # إغلاق نافذة الإعدادات
                            try:
                                close_btn = driver.find_element(By.CSS_SELECTOR, "[data-name='close'], .tv-dialog__close")
                                driver.execute_script("arguments[0].click();", close_btn)
                                time.sleep(2)
                            except:
                                pass
                            
                            return True
                except:
                    continue
        
        # محاولة بديلة: البحث مباشرة عن خيارات Renko
        try:
            # النقر بزر الماوس الأيمن على الشارت لفتح القائمة
            chart_canvas = driver.find_element(By.CSS_SELECTOR, "canvas")
            ActionChains(driver).context_click(chart_canvas).perform()
            time.sleep(3)
            
            # البحث عن خيارات الشارت
            style_options = driver.find_elements(By.XPATH, "//div[contains(text(), 'Style') or contains(text(), 'Properties')]")
            if style_options:
                driver.execute_script("arguments[0].click();", style_options[0])
                time.sleep(3)
                
                # البحث عن خيار الشمعات
                candle_options = driver.find_elements(By.XPATH, "//span[contains(text(), 'Candle') or contains(text(), 'Body')]")
                if candle_options:
                    driver.execute_script("arguments[0].click();", candle_options[0])
                    time.sleep(2)
                    logger.info("✅ تم تفعيل Renko Candlesticks (طريقة بديلة)")
                    return True
        except:
            pass
        
        logger.warning("⚠️ لم يتم العثور على خيار Renko Candlesticks")
        return False
        
    except Exception as e:
        logger.error(f"❌ خطأ في تفعيل Renko Candlesticks: {e}")
        return False

async def change_to_monthly_timeframe(driver):
    """تغيير الفريم إلى شهري"""
    try:
        logger.info("📅 تغيير الفريم إلى شهري...")
        
        timeframe_selectors = [
            "[data-name='intervals']",
            "[data-tooltip*='Time']",
            ".interval-item",
            "[title*='Interval']"
        ]
        
        timeframe_btn = None
        for selector in timeframe_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        timeframe_btn = element
                        break
                if timeframe_btn:
                    break
            except:
                continue
        
        if timeframe_btn:
            driver.execute_script("arguments[0].click();", timeframe_btn)
            time.sleep(3)
            
            # البحث عن الفريم الشهري
            monthly_selectors = [
                "//button[contains(text(), '1M')]",
                "//div[contains(text(), '1M')]",
                "//span[contains(text(), '1M')]",
                "[data-value='1M']",
                "[data-period='1M']"
            ]
            
            for selector in monthly_selectors:
                try:
                    if selector.startswith("//"):
                        monthly_elements = driver.find_elements(By.XPATH, selector)
                    else:
                        monthly_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for monthly_element in monthly_elements:
                        if monthly_element.is_displayed():
                            driver.execute_script("arguments[0].click();", monthly_element)
                            time.sleep(5)
                            logger.info("✅ تم تغيير الفريم إلى شهري")
                            return True
                except:
                    continue
        
        logger.warning("⚠️ لم يتم العثور على الفريم الشهري")
        return False
        
    except Exception as e:
        logger.error(f"❌ خطأ في تغيير الفريم: {e}")
        return False

async def clean_chart_interface(driver):
    """تنظيف واجهة الشارت"""
    try:
        elements_to_hide = [
            ".tv-dialog-renderer",
            ".tv-toast-container",
            ".tv-floating-toolbar",
            ".tv-screener-popup",
            ".layout__area--top",
            ".layout__area--bottom",
            ".layout__area--left",
            ".tv-header",
            ".tv-footer"
        ]
        
        for selector in elements_to_hide:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    driver.execute_script("arguments[0].style.display = 'none';", element)
            except:
                pass
    except Exception as e:
        logger.warning(f"⚠️ خطأ في تنظيف الواجهة: {e}")

async def capture_chart_screenshot(driver, symbol):
    """التقاط لقطة شاشة محسنة للشارت"""
    try:
        logger.info(f"📸 التقاط شارت Renko Candlesticks لـ {symbol}...")
        
        # انتظار إضافي
        time.sleep(8)
        
        # البحث عن منطقة الشارت
        chart_selectors = [
            ".layout__area--center",
            ".chart-container",
            "[data-name='legend-source-item']",
            "canvas"
        ]
        
        chart_element = None
        for selector in chart_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.size['height'] > 200:
                        chart_element = element
                        break
                if chart_element:
                    break
            except:
                continue
        
        file_name = f"{symbol}_renko_candlesticks_monthly.png"
        
        if chart_element:
            chart_element.screenshot(file_name)
            logger.info(f"📸 تم التقاط شارت {symbol} (منطقة محددة)")
        else:
            driver.save_screenshot(file_name)
            logger.info(f"📸 تم التقاط شارت {symbol} (شاشة كاملة)")
        
        # التحقق من جودة الصورة
        if os.path.exists(file_name):
            file_size = os.path.getsize(file_name)
            if file_size > 10000:  # أكبر من 10KB
                logger.info(f"✅ تم إنشاء صورة صحيحة ({file_size} bytes)")
                return file_name
            else:
                logger.warning(f"⚠️ الصورة صغيرة جداً ({file_size} bytes)")
                return None
        else:
            logger.error("❌ فشل في إنشاء الصورة")
            return None
            
    except Exception as e:
        logger.error(f"❌ خطأ في التقاط الشارت: {e}")
        return None

async def process_symbol(driver, symbol_info):
    """معالجة عملة واحدة"""
    symbol = symbol_info["symbol"]
    name = symbol_info["name"]
    
    logger.info(f"🕯️ معالجة {name} ({symbol}) - Renko Candlesticks...")
    
    try:
        # بناء رابط TradingView
        url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}"
        
        logger.info(f"🌐 الذهاب إلى: {url}")
        driver.get(url)
        
        # انتظار تحميل الصفحة
        time.sleep(15)
        
        # إعداد شارت Renko Candlesticks
        setup_success = await setup_renko_candlesticks(driver, symbol)
        
        # التقاط الشارت
        screenshot_file = await capture_chart_screenshot(driver, symbol)
        
        if screenshot_file:
            # إرسال الصورة
            photo = FSInputFile(screenshot_file)
            
            # إرسال رسالة نصية
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"🕯️ **{name} ({symbol})**\n📊 Renko Candlesticks Chart\n📅 Monthly Timeframe (1M)\n⏰ {time.strftime('%Y-%m-%d %H:%M UTC')}",
                parse_mode="Markdown"
            )
            
            # إرسال الصورة
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption=f"🕯️ {name} - Renko Candlesticks Monthly"
            )
            
            # حذف الملف
            os.remove(screenshot_file)
            logger.info(f"✅ تم إرسال شارت Renko Candlesticks لـ {symbol} بنجاح")
            return True
        else:
            logger.error(f"❌ فشل في إنشاء شارت {symbol}")
            return False
            
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة {symbol}: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل بوت Renko Candlesticks...")
    
    # إرسال رسالة بداية
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="🚀 **بدء تشغيل بوت Renko Candlesticks**\n🕯️ جاري جلب شارتات Renko بالشمعات...\n📊 نوع الشارت: Renko Candlesticks\n📅 الفريم: شهري (1M)\n⏳ يرجى الانتظار...",
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
            success = await process_symbol(driver, symbol_info)
            
            if success:
                successful_charts.append(symbol_info)
            
            # انتظار بين العملات
            if i < len(SYMBOLS) - 1:
                logger.info("⏳ انتظار بين العملات...")
                time.sleep(25)
        
        # إرسال ملخص النتائج
        try:
            total_symbols = len(SYMBOLS)
            success_count = len(successful_charts)
            
            summary = f"""
🤖 **تقرير بوت Renko Candlesticks**
📅 التاريخ: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **النتائج:**
✅ نجح: {success_count}/{total_symbols}
❌ فشل: {total_symbols - success_count}/{total_symbols}

🕯️ **شارتات Renko Candlesticks المرسلة:**
{chr(10).join([f"• {info['name']}" for info in successful_charts])}

📈 **المواصفات:**
• نوع الشارت: Renko Candlesticks 🕯️
• الفريم الزمني: شهري (1M)
• المصدر: TradingView
• الشكل: شمعات ملونة مع فتائل

🔄 **التشغيل التالي:** خلال 6 ساعات
            """.strip()
            
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=summary,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال الملخص: {e}")
                
    except Exception as e:
        logger.error(f"❌ خطأ عام: {e}")
        
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"❌ **خطأ في بوت Renko Candlesticks**\n```{str(e)}```",
                parse_mode="Markdown"
            )
        except:
            pass
        
    finally:
        driver.quit()
        await bot.session.close()
        logger.info("🏁 انتهى التشغيل")

if __name__ == "__main__":
    asyncio.run(main())
