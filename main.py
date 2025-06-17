import requests
import os
from datetime import datetime
import time
import json

def test_binance_api():
    """اختبار API بينانس"""
    print("🔍 اختبار API بينانس...")
    
    # اختبار الاتصال العام
    try:
        test_url = "https://api.binance.com/api/v3/ping"
        response = requests.get(test_url, timeout=10)
        print(f"📡 Ping Status: {response.status_code}")
        print(f"📡 Ping Response: {response.text}")
    except Exception as e:
        print(f"❌ خطأ في ping: {e}")
    
    # اختبار جلب سعر واحد
    try:
        test_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(test_url, timeout=10)
        print(f"📡 BTC Status: {response.status_code}")
        print(f"📡 BTC Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 BTC Data Type: {type(data)}")
            print(f"📊 BTC Data Keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
            
    except Exception as e:
        print(f"❌ خطأ في اختبار BTC: {e}")

def get_crypto_prices():
    """جلب أسعار العملات من Binance API"""
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
    prices = {}
    
    for symbol in symbols:
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            print(f"🔗 URL: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"📡 {symbol} Status: {response.status_code}")
            print(f"📡 {symbol} Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 {symbol} Data: {data}")
                print(f"📊 {symbol} Type: {type(data)}")
                
                if isinstance(data, dict) and 'price' in data:
                    price = float(data['price'])
                    prices[symbol] = f"${price:,.2f}"
                    print(f"✅ {symbol}: {prices[symbol]}")
                else:
                    print(f"❌ {symbol}: البيانات لا تحتوي على 'price'")
                    print(f"❌ {symbol}: Keys available: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
                    prices[symbol] = "غير متوفر"
            else:
                print(f"❌ خطأ HTTP {symbol}: {response.status_code}")
                prices[symbol] = "غير متوفر"
                
        except Exception as e:
            print(f"❌ خطأ في جلب سعر {symbol}: {str(e)}")
            prices[symbol] = "غير متوفر"
            
        time.sleep(0.2)
    
    return prices

def test_telegram_bot():
    """اختبار إعدادات تليجرام"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print("🔍 فحص إعدادات تليجرام...")
    print(f"🔑 Bot Token موجود: {'نعم' if bot_token else 'لا'}")
    print(f"🔑 Chat ID موجود: {'نعم' if chat_id else 'لا'}")
    
    if bot_token:
        print(f"🔑 Bot Token (أول 10 أحرف): {bot_token[:10]}...")
        print(f"🔑 Bot Token (طول): {len(bot_token)}")
    
    if chat_id:
        print(f"🔑 Chat ID: {chat_id}")
        print(f"🔑 Chat ID (طول): {len(str(chat_id))}")
    
    # اختبار getMe
    if bot_token:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            response = requests.get(url, timeout=10)
            print(f"📡 getMe Status: {response.status_code}")
            print(f"📡 getMe Response: {response.text}")
        except Exception as e:
            print(f"❌ خطأ في getMe: {e}")

def send_telegram_message(message):
    """إرسال رسالة إلى تليجرام"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ إعدادات تليجرام مفقودة")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        print(f"📤 إرسال إلى: {url}")
        print(f"📤 البيانات: {payload}")
        
        response = requests.post(url, data=payload, timeout=30)
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📡 Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ تم إرسال الرسالة بنجاح!")
                return True
        
        print("❌ فشل في إرسال الرسالة")
        return False
            
    except Exception as e:
        print(f"❌ خطأ في إرسال الرسالة: {str(e)}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء تشغيل بوت العملات...")
    print("=" * 50)
    
    # اختبار API بينانس
    test_binance_api()
    print("=" * 50)
    
    # اختبار تليجرام
    test_telegram_bot()
    print("=" * 50)
    
    # جلب أسعار العملات
    print("📊 جلب أسعار العملات...")
    prices = get_crypto_prices()
    print("=" * 50)
    
    # إنشاء التقرير
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    report = f"""
🚀 <b>تقرير العملات الرقمية</b>
📅 {current_date}

💰 <b>الأسعار:</b>
🔸 BTC: {prices.get('BTCUSDT', 'غير متوفر')}
🔸 ETH: {prices.get('ETHUSDT', 'غير متوفر')}
🔸 BNB: {prices.get('BNBUSDT', 'غير متوفر')}
🔸 SOL: {prices.get('SOLUSDT', 'غير متوفر')}
🔸 XRP: {prices.get('XRPUSDT', 'غير متوفر')}

🤖 بوت العملات الرقمية
    """.strip()
    
    print("📝 التقرير:")
    print(report)
    print("=" * 50)
    
    # إرسال التقرير
    print("📤 إرسال التقرير...")
    success = send_telegram_message(report)
    
    print("=" * 50)
    print("🏁 تم الانتهاء من التشغيل")

if __name__ == "__main__":
    main()
