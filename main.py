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
    chrome_options.add_argument("--headless=new")  # استخدام headless الجديد
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # إزالة إشارات الأتمتة
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # إزالة خاصية webdriver
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
        # انتظار عدة عناصر للتأكد من التحميل
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas")))
        time.sleep(5)
        
        # انتظار اختفاء شاشة التحميل
        try:
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".tv-spinner")))
        except:
            pass
        
        time.sleep(3)
        logger.info("✅ تم تحميل الشارت")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ انتهت مهلة انتظار تحميل الشارت: {e}")
        return False

async def setup_renko_chart(driver, symbol):
    """إعداد شارت Renko مع الفريم الشهري - محسن"""
    try:
        logger.info(f"🔧 إعداد Renko Chart لـ {symbol}...")
        
        wait = WebDriverWait(driver, 20)
        
        # انتظار تحميل الصفحة الأساسي
        await wait_for_chart_load(driver)
        
        # 1. إغلاق أي نوافذ منبثقة
        try:
            close_buttons = [
                "[data-name='close']",
                ".tv-dialog__close",
                ".js-dialog__close",
                "[aria-label='Close']"
            ]
            
            for selector in close_buttons:
                try:
                    close_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    if close_btn.is_displayed():
                        driver.execute_script("arguments[0].click();", close_btn)
                        time.sleep(1)
                except:
                    continue
        except:
            pass
        
        # 2. تغيير نوع الشارت إلى Renko
        try:
            logger.info("📊 تغيير نوع الشارت إلى Renko...")
            
            # البحث عن زر نوع الشارت
            chart_type_selectors = [
                "[data-name='chart-style-switcher']",
                "[data-tooltip*='Chart']",
                ".chart-style-switcher"
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
            
            if chart_type_btn:
                # النقر على زر نوع الشارت
                driver.execute_script("arguments[0].scrollIntoView(true);", chart_type_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", chart_type_btn)
                time.sleep(3)
                
                # البحث عن خيار Renko
                renko_found = False
                renko_selectors = [
                    "[data-name='renko']",
                    "[title*='Renko']",
                    "//div[contains(text(), 'Renko')]",
                    "//span[contains(text(), 'Renko')]"
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
                                time.sleep(5)
                                logger.info("✅ تم تغيير نوع الشارت إلى Renko")
                                renko_found = True
                                break
                        
                        if renko_found:
                            break
                    except:
                        continue
                
                if not renko_found:
                    logger.warning("⚠️ لم يتم العثور على خيار Renko")
            else:
                logger.warning("⚠️ لم يتم العثور على زر نوع الشارت")
        
        except Exception as e:
            logger.warning(f"⚠️ خطأ في تغيير نوع الشارت: {e}")
        
        # 3. تغيير الفريم الزمني إلى شهري
        try:
            logger.info("📅 تغيير الفريم إلى شهري...")
            
            # البحث عن زر الفريم الزمني
            timeframe_selectors = [
                "[data-name='intervals']",
                "[data-tooltip*='Time']",
                ".interval-item"
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
                time.sleep(2)
                
                # البحث عن الفريم الشهري
                monthly_selectors = [
                    "//button[contains(text(), '1M')]",
                    "//div[contains(text(), '1M')]",
                    "[data-value='1M']"
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
                                time.sleep(3)
                                logger.info("✅ تم تغيير الفريم إلى شهري")
                                break
                    except:
                        continue
        
        except Exception as e:
            logger.warning(f"⚠️ خطأ في تغيير الفريم: {e}")
        
        # 4. إزالة العناصر المشتتة
        try:
            elements_to_hide = [
                ".tv-dialog-renderer",
                ".tv-toast-container",
                ".tv-floating-toolbar",
                ".tv-screener-popup",
                "[data-name='legend']",
                ".layout__area--top",
                ".layout__area--bottom",
                ".layout__area--left"
            ]
            
            for selector in elements_to_hide:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        driver.execute_script("arguments[0].style.display = 'none';", element)
                except:
                    pass
        except:
            pass
        
        # انتظار إضافي لتحميل الشارت الجديد
        await wait_for_chart_load(driver, 15)
        
        logger.info("✅ تم إعداد الشارت بنجاح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد الشارت: {e}")
        return False

async def capture_chart_screenshot(driver, symbol):
    """التقاط لقطة شاشة محسنة للشارت"""
    try:
        logger.info(f"📸 التقاط شارت {symbol}...")
        
        # انتظار إضافي
        time.sleep(5)
        
        # محاولة العثور على منطقة الشارت
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
                    if element.is_displayed() and element.size['height'] > 100:
                        chart_element = element
                        break
                if chart_element:
                    break
            except:
                continue
        
        file_name = f"{symbol}_renko_monthly.png"
        
        if chart_element:
            # التقاط الشارت فقط
            chart_element.screenshot(file_name)
            logger.info(f"📸 تم التقاط شارت {symbol} (منطقة محددة)")
        else:
            # التقاط الشاشة كاملة
            driver.save_screenshot(file_name)
            logger.info(f"📸 تم التقاط شارت {symbol} (شاشة كاملة)")
        
        # التحقق من جودة الصورة
        if os.path.exists(file_name):
            file_size = os.path.getsize(file_name)
            if file_size > 5000:  # أكبر من 5KB
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
    
    logger.info(f"📈 معالجة {name} ({symbol})...")
    
    try:
        # بناء رابط TradingView
        url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}"
        
        logger.info(f"🌐 الذهاب إلى: {url}")
        driver.get(url)
        
        # انتظار تحميل الصفحة
        time.sleep(10)
        
        # إعداد شارت Renko
        setup_success = await setup_renko_chart(driver, symbol)
        
        # التقاط الشارت
        screenshot_file = await capture_chart_screenshot(driver, symbol)
        
        if screenshot_file:
            # إرسال الصورة
            photo = FSInputFile(screenshot_file)
            
            # إرسال رسالة نصية
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"📊 **{name} ({symbol})**\n📈 Renko Chart - Monthly Timeframe\n📅 {time.strftime('%Y-%m-%d %H:%M UTC')}",
                parse_mode="Markdown"
            )
            
            # إرسال الصورة
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption=f"📈 {name} - Renko Monthly Chart"
            )
            
            # حذف الملف
            os.remove(screenshot_file)
            logger.info(f"✅ تم إرسال شارت {symbol} بنجاح")
            return True
        else:
            logger.error(f"❌ فشل في إنشاء شارت {symbol}")
            return False
            
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة {symbol}: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل بوت شارتات Renko المحسن...")
    
    # إرسال رسالة بداية
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="🚀 **بدء تشغيل بوت Renko المحسن**\n⏳ جاري جلب شارتات Renko الشهرية...\n📊 نوع الشارت: Renko Candlesticks\n📅 الفريم: شهري (1M)",
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
                time.sleep(20)
        
        # إرسال ملخص النتائج
        try:
            total_symbols = len(SYMBOLS)
            success_count = len(successful_charts)
            
            summary = f"""
🤖 **تقرير بوت Renko المحسن**
📅 التاريخ: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **النتائج:**
✅ نجح: {success_count}/{total_symbols}
❌ فشل: {total_symbols - success_count}/{total_symbols}

✅ **شارتات Renko المرسلة:**
{chr(10).join([f"• {info['name']}" for info in successful_charts])}

📈 **المواصفات:**
• نوع الشارت: Renko Candlesticks
• الفريم الزمني: شهري (1M)
• المصدر: TradingView
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
                text=f"❌ **خطأ في بوت Renko**\n```{str(e)}```",
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
