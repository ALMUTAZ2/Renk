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
from datetime import datetime, timedelta

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

def format_duration(seconds):
    """تحويل الثواني إلى تنسيق مقروء"""
    if seconds < 60:
        return f"{seconds:.1f} ثانية"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} دقيقة"
    else:
        hours = seconds / 3600
        minutes = (seconds % 3600) / 60
        return f"{hours:.1f} ساعة و {minutes:.0f} دقيقة"

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
    {"symbol": "XRPUSDT", "name": "XRP"},
    {"symbol": "ADAUSDT", "name": "Cardano"},
    {"symbol": "DOGEUSDT", "name": "Dogecoin"},
    {"symbol": "LTCUSDT", "name": "Litecoin"},
    {"symbol": "LINKUSDT", "name": "Chainlink"},
    {"symbol": "UNIUSDT", "name": "Uniswap"},
    {"symbol": "MATICUSDT", "name": "Polygon"},
    {"symbol": "SHIBUSDT", "name": "Shiba Inu"},
    {"symbol": "ATOMUSDT", "name": "Cosmos"},
    {"symbol": "DOTUSDT", "name": "Polkadot"},
    {"symbol": "EOSUSDT", "name": "EOS"},
    {"symbol": "AVAXUSDT", "name": "Avalanche"},
    {"symbol": "AAVEUSDT", "name": "AAVE"},
    {"symbol": "XLMUSDT", "name": "Stellar"},
    {"symbol": "USDTUSDT", "name": "Tether"},
    {"symbol": "USDCUSDT", "name": "USD Coin"},
    {"symbol": "DASHUSDT", "name": "Dash"},
    {"symbol": "ZECUSDT", "name": "Zcash"},
    {"symbol": "XMRUSDT", "name": "Monero"},
    {"symbol": "XTZUSDT", "name": "Tezos"},
    {"symbol": "ALGOUSDT", "name": "Algorand"},
    {"symbol": "PEPEUSDT", "name": "Pepe Coin"},
    
    # العملات ذات الشعبية العالية (تمت إضافتها)
    {"symbol": "TONUSDT", "name": "Toncoin"},
    {"symbol": "INJUSDT", "name": "Injective"},
    {"symbol": "RUNEUSDT", "name": "ThorChain"},
    {"symbol": "SNXUSDT", "name": "Synthetix"},
    {"symbol": "GRTUSDT", "name": "The Graph"},
    {"symbol": "LDOUSDT", "name": "Lido DAO"},
    {"symbol": "OPUSDT", "name": "Optimism"},
    {"symbol": "ARBUSDT", "name": "Arbitrum"},
    {"symbol": "TIAUSDT", "name": "Celestia"},
    {"symbol": "STXUSDT", "name": "Stacks"},
    {"symbol": "NEARUSDT", "name": "Near Protocol"},
    {"symbol": "KASUSDT", "name": "Kaspa"},
    {"symbol": "HBARUSDT", "name": "Hedera"},
    {"symbol": "FILUSDT", "name": "Filecoin"},
    {"symbol": "ENSUSDT", "name": "Ethereum Name Service"}
]

async def capture_tradingview_chart(symbol_info, driver):
    """التقاط شارت من TradingView"""
    symbol = symbol_info["symbol"]
    name = symbol_info["name"]
    
    # بدء قياس الوقت للعملة الواحدة
    chart_start_time = time.time()
    
    logger.info(f"📈 معالجة {name} ({symbol})...")
    
    try:
        # بناء رابط TradingView مع الثيم الداكن
        url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}&interval=1M&style=4&theme=dark"

        
        logger.info(f"🌐 الذهاب إلى: {url}")
        driver.get(url)
        
        # انتظار تحميل الصفحة
        logger.info("⏳ انتظار تحميل الشارت...")
        time.sleep(20)  # انتظار أطول للتأكد من التحميل
        
        # أخذ لقطة شاشة
        file_name = f"{symbol}_chart.png"
        
        try:
            # محاولة العثور على منطقة الشارت
            wait = WebDriverWait(driver, 15)
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
            
            # حساب الوقت المستغرق لهذه العملة
            chart_duration = time.time() - chart_start_time
            
            # إرسال رسالة نصية أولاً
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"📊 **شارت {name} ({symbol})**\n🔗 TradingView\n📅 {time.strftime('%Y-%m-%d %H:%M UTC')}\n⏱️ وقت المعالجة: {format_duration(chart_duration)}",
                parse_mode="Markdown"
            )
            
            # إرسال الصورة
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption=f"📈 {name} Chart"
            )
            
            # حذف الملف
            os.remove(file_name)
            logger.info(f"✅ تم إرسال شارت {symbol} بنجاح في {format_duration(chart_duration)}")
            return True, chart_duration
            
        else:
            chart_duration = time.time() - chart_start_time
            logger.error(f"❌ فشل في إنشاء ملف صحيح لـ {symbol}")
            return False, chart_duration
            
    except Exception as e:
        chart_duration = time.time() - chart_start_time
        logger.error(f"❌ خطأ في معالجة {symbol}: {e}")
        return False, chart_duration

async def send_summary_message(successful_charts, total_duration, chart_durations):
    """إرسال رسالة ملخص شهرية"""
    try:
        total_symbols = len(SYMBOLS)
        success_count = len(successful_charts)
        
        current_date = datetime.now()
        month_names = {
            1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
            5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
            9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
        }
        current_month = month_names[current_date.month]
        current_year = current_date.year
        
        next_month_num = current_date.month + 1 if current_date.month < 12 else 1
        next_year = current_year if current_date.month < 12 else current_year + 1
        next_month = month_names[next_month_num]
        
        # حساب متوسط الوقت لكل عملة
        avg_time_per_chart = sum(chart_durations) / len(chart_durations) if chart_durations else 0
        
        summary = f"""
🌙 **التقرير الشهري - بوت الشارتات**
📅 الشهر: {current_month} {current_year}
🕒 التاريخ والوقت: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **نتائج هذا الشهر:**
✅ نجح: {success_count}/{total_symbols}
❌ فشل: {total_symbols - success_count}/{total_symbols}

⏱️ **إحصائيات الوقت:**
🕐 إجمالي الوقت المستغرق: {format_duration(total_duration)}
📈 متوسط الوقت لكل شارت: {format_duration(avg_time_per_chart)}
⚡ أسرع شارت: {format_duration(min(chart_durations)) if chart_durations else "غير متاح"}
🐌 أبطأ شارت: {format_duration(max(chart_durations)) if chart_durations else "غير متاح"}

✅ **الشارتات المُرسلة:**
{chr(10).join([f"• {info['name']} ({info['symbol']})" for info in successful_charts])}

📈 **معلومات إضافية:**
• المصدر: TradingView
• البورصة: Binance
• الإطار الزمني: 1 شهر

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
        
        # تقدير الوقت المتوقع (حوالي 45 ثانية لكل عملة)
        estimated_time = len(SYMBOLS) * 45  # ثانية
        estimated_duration = format_duration(estimated_time)
        
        greeting = f"""
🚀 **مرحباً بك في التقرير الشهري!**

📅 **{current_month} {current_year}**
🕒 بدء التشغيل: {time.strftime('%Y-%m-%d %H:%M UTC')}

📊 **ما سيتم عمله:**
• تصوير شارتات العملات الرقمية على فريم شهري رينكو وإرساله على التليجرام بشكل شهري
• عدد العملات: {len(SYMBOLS)} عملة
• الوقت المتوقع للإنتهاء: {estimated_duration}

⏳ **جاري المعالجة...**
يرجى الانتظار بينما نجلب أحدث الشارتات لك
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=greeting,
            parse_mode="Markdown"
        )
        
        logger.info("👋 تم إرسال رسالة الترحيب الشهرية")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال رسالة الترحيب: {e}")

async def send_progress_update(current_index, total_symbols, elapsed_time, successful_count, failed_count):
    """إرسال تحديث التقدم كل 10 عملات"""
    try:
        progress_percentage = (current_index / total_symbols) * 100
        avg_time_per_symbol = elapsed_time / current_index if current_index > 0 else 0
        remaining_symbols = total_symbols - current_index
        estimated_remaining_time = remaining_symbols * avg_time_per_symbol
        
        progress_message = f"""
📊 **تحديث التقدم**

🔄 **الحالة الحالية:**
• تم إنجاز: {current_index}/{total_symbols} ({progress_percentage:.1f}%)
• نجح: {successful_count} | فشل: {failed_count}

⏱️ **إحصائيات الوقت:**
• الوقت المنقضي: {format_duration(elapsed_time)}
• متوسط الوقت لكل عملة: {format_duration(avg_time_per_symbol)}
• الوقت المتبقي المتوقع: {format_duration(estimated_remaining_time)}

🚀 **التقدم:** {"█" * int(progress_percentage // 5)}{"░" * (20 - int(progress_percentage // 5))} {progress_percentage:.1f}%
        """.strip()
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=progress_message,
            parse_mode="Markdown"
        )
        
        logger.info(f"📊 تم إرسال تحديث التقدم: {current_index}/{total_symbols}")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال تحديث التقدم: {e}")

async def main():
    """الدالة الرئيسية"""
    # بدء قياس الوقت الإجمالي
    total_start_time = time.time()
    
    logger.info("🚀 بدء تشغيل بوت الشارتات الشهري...")
    
    await send_monthly_greeting()
    
    driver = setup_chrome_driver()
    successful_charts = []
    failed_charts = []
    chart_durations = []  # لحفظ أوقات كل شارت
    
    try:
        for i, symbol_info in enumerate(SYMBOLS):
            logger.info(f"🔄 معالجة العملة {i+1}/{len(SYMBOLS)}: {symbol_info['name']}")
            
            success, duration = await capture_tradingview_chart(symbol_info, driver)
            chart_durations.append(duration)
            
            if success:
                successful_charts.append(symbol_info)
            else:
                failed_charts.append(symbol_info)
            
            # إرسال تحديث التقدم كل 10 عملات
            if (i + 1) % 10 == 0 or (i + 1) == len(SYMBOLS):
                elapsed_time = time.time() - total_start_time
                await send_progress_update(
                    i + 1, 
                    len(SYMBOLS), 
                    elapsed_time, 
                    len(successful_charts), 
                    len(failed_charts)
                )
            
            if i < len(SYMBOLS) - 1:
                logger.info("⏳ انتظار بين العملات...")
                time.sleep(10)
        
        # حساب الوقت الإجمالي
        total_duration = time.time() - total_start_time
        
        await send_summary_message(successful_charts, total_duration, chart_durations)
        
        if failed_charts:
            failed_list = "\n".join([f"• {info['name']} ({info['symbol']})" for info in failed_charts])
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"⚠️ **العملات التي فشل في معالجتها:**\n{failed_list}\n\n🔧 سيتم إعادة المحاولة في التقرير القادم",
                parse_mode="Markdown"
            )
                
    except Exception as e:
        total_duration = time.time() - total_start_time
        logger.error(f"❌ خطأ عام: {e}")
        
        try:
            error_message = f"""
❌ **خطأ في البوت الشهري**

🕒 الوقت: {time.strftime('%Y-%m-%d %H:%M UTC')}
⏱️ الوقت المنقضي قبل الخطأ: {format_duration(total_duration)}
📋 تفاصيل الخطأ:

{str(e)}

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
        
        # حساب وعرض الوقت الإجمالي النهائي
        final_total_duration = time.time() - total_start_time
        logger.info(f"🏁 انتهى التشغيل الشهري - الوقت الإجمالي: {format_duration(final_total_duration)}")

if __name__ == "__main__":
    asyncio.run(main())
