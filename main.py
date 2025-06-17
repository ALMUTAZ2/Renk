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
    """إعداد Chrome Driver مع Selenium Manager"""
    logger.info("🔧 إعداد Chrome Driver...")
    
    chrome_options = Options()
    
    # إعدادات Chrome
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    try:
        # استخدام Selenium Manager
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
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

async def setup_renko_chart(driver, symbol):
    """إعداد شارت Renko مع الفريم الشهري"""
    try:
        logger.info(f"🔧 إعداد Renko Chart لـ {symbol}...")
        
        # انتظار تحميل الصفحة
        wait = WebDriverWait(driver, 20)
        
        # انتظار حتى يتم تحميل الشارت
        time.sleep(10)
        
        # 1. تغيير الفريم الزمني إلى شهري (1M)
        try:
            logger.info("📅 تغيير الفريم إلى شهري...")
            
            # البحث عن زر الفريم الزمني
            timeframe_selectors = [
                "[data-name='intervals']",
                ".tv-dropdown-behavior__button",
                ".interval-item",
                "[data-value='1M']"
            ]
            
            for selector in timeframe_selectors:
                try:
                    timeframe_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    driver.execute_script("arguments[0].click();", timeframe_btn)
                    time.sleep(2)
                    break
                except:
                    continue
            
            # محاولة النقر على 1M مباشرة
            try:
                monthly_btn = driver.find_element(By.XPATH, "//button[contains(text(), '1M')]")
                driver.execute_script("arguments[0].click();", monthly_btn)
                time.sleep(3)
                logger.info("✅ تم تغيير الفريم إلى شهري")
            except:
                logger.warning("⚠️ لم يتم العثور على زر الفريم الشهري")
        
        except Exception as e:
            logger.warning(f"⚠️ خطأ في تغيير الفريم: {e}")
        
        # 2. تغيير نوع الشارت إلى Renko
        try:
            logger.info("📊 تغيير نوع الشارت إلى Renko...")
            
            # البحث عن زر نوع الشارت
            chart_type_selectors = [
                "[data-name='chart-style-switcher']",
                ".chart-style-switcher",
                "[data-tooltip='Chart Type']",
                ".tv-dropdown-behavior__button[data-name='chart-style-switcher']"
            ]
            
            chart_type_btn = None
            for selector in chart_type_selectors:
                try:
                    chart_type_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if chart_type_btn:
                driver.execute_script("arguments[0].click();", chart_type_btn)
                time.sleep(2)
                
                # البحث عن خيار Renko
                renko_selectors = [
                    "[data-name='renko']",
                    "[title='Renko']",
                    "//div[contains(text(), 'Renko')]",
                    ".item-2IihgTnv[data-name='renko']"
                ]
                
                for selector in renko_selectors:
                    try:
                        if selector.startswith("//"):
                            renko_option = driver.find_element(By.XPATH, selector)
                        else:
                            renko_option = driver.find_element(By.CSS_SELECTOR, selector)
                        
                        driver.execute_script("arguments[0].click();", renko_option)
                        time.sleep(3)
                        logger.info("✅ تم تغيير نوع الشارت إلى Renko")
                        break
                    except:
                        continue
                else:
                    logger.warning("⚠️ لم يتم العثور على خيار Renko")
            else:
                logger.warning("⚠️ لم يتم العثور على زر نوع الشارت")
        
        except Exception as e:
            logger.warning(f"⚠️ خطأ في تغيير نوع الشارت: {e}")
        
        # 3. إزالة العناصر غير المرغوب فيها
        try:
            logger.info("🧹 إزالة العناصر غير المرغوب فيها...")
            
            # إزالة الإعلانات والعناصر المشتتة
            elements_to_hide = [
                ".tv-dialog-renderer",
                ".tv-toast-container",
                ".tv-floating-toolbar",
                "[data-name='legend']",
                ".tv-screener-popup",
                ".js-rootresizer__contents > div:first-child",
                ".layout__area--top",
                ".layout__area--bottom"
            ]
            
            for selector in elements_to_hide:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        driver.execute_script("arguments[0].style.display = 'none';", element)
                except:
                    pass
        
        except Exception as e:
            logger.warning(f"⚠️ خطأ في إزالة العناصر: {e}")
        
        # انتظار إضافي لتحميل الشارت
        time.sleep(8)
        logger.info("✅ تم إعداد الشارت بنجاح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في إعداد الشارت: {e}")
        return False

async def capture_tradingview_chart(symbol_info, driver):
    """التقاط شارت Renko من TradingView"""
    symbol = symbol_info["symbol"]
    name = symbol_info["name"]
    
    logger.info(f"📈 معالجة {name} ({symbol})...")
    
    try:
        # بناء رابط TradingView
        url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}"
        
        logger.info(f"🌐 الذهاب إلى: {url}")
        driver.get(url)
        
        # إعداد شارت Renko
        setup_success = await setup_renko_chart(driver, symbol)
        
        if not setup_success:
            logger.warning(f"⚠️ فشل في إعداد Renko Chart لـ {symbol}")
        
        # أخذ لقطة شاشة
        file_name = f"{symbol}_renko_monthly.png"
        
        try:
            # محاولة العثور على منطقة الشارت
            wait = WebDriverWait(driver, 10)
            
            # محاولة عدة selectors لمنطقة الشارت
            chart_selectors = [
                ".layout__area--center",
                ".chart-container",
                ".tv-lightweight-charts",
                "[data-name='legend-source-item']"
            ]
            
            chart_area = None
            for selector in chart_selectors:
                try:
                    chart_area = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if chart_area:
                # أخذ لقطة شاشة للشارت فقط
                chart_area.screenshot(file_name)
                logger.info(f"📸 تم التقاط شارت {symbol}")
            else:
                # أخذ لقطة شاشة كاملة كبديل
                driver.save_screenshot(file_name)
                logger.info(f"📸 تم التقاط لقطة شاشة كاملة لـ {symbol}")
            
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
🤖 **تقرير بوت شارتات Renko**
📅 التاريخ: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **النتائج:**
✅ نجح: {success_count}/{total_symbols}
❌ فشل: {total_symbols - success_count}/{total_symbols}

✅ **شارتات Renko الشهرية المرسلة:**
{chr(10).join([f"• {info['name']}" for info in successful_charts])}

📈 **نوع الشارت:** Renko Charts
📅 **الفريم الزمني:** شهري (1M)
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
    logger.info("🚀 بدء تشغيل بوت شارتات Renko...")
    
    # إرسال رسالة بداية
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="🚀 **بدء تشغيل بوت شارتات Renko**\n⏳ جاري جلب شارتات Renko الشهرية من TradingView...",
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
            
            # انتظار بين العملات
            if i < len(SYMBOLS) - 1:
                logger.info("⏳ انتظار بين العملات...")
                time.sleep(15)  # زيادة وقت الانتظار
        
        # إرسال ملخص النتائج
        await send_summary_message(successful_charts)
                
    except Exception as e:
        logger.error(f"❌ خطأ عام: {e}")
        
        # إرسال رسالة خطأ
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"❌ **خطأ في بوت Renko**\n```{str(e)}```",
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
