import requests
import os
from datetime import datetime
import time

def get_crypto_prices():
  """جلب أسعار العملات من Binance API"""
  symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
  prices = {}
  
  for symbol in symbols:
      try:
          # استخدام API endpoint الصحيح
          url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
          response = requests.get(url, timeout=10)
          
          if response.status_code == 200:
              data = response.json()
              price = float(data['price'])
              prices[symbol] = f"${price:,.2f}"
              print(f"✅ {symbol}: {prices[symbol]}")
          else:
              print(f"❌ خطأ في جلب سعر {symbol}: {response.status_code}")
              prices[symbol] = "غير متوفر"
              
      except Exception as e:
          print(f"❌ خطأ في جلب سعر {symbol}: {str(e)}")
          prices[symbol] = "غير متوفر"
          
      # تأخير قصير بين الطلبات
      time.sleep(0.1)
  
  return prices

def send_telegram_message(message):
  """إرسال رسالة إلى تليجرام"""
  bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
  chat_id = os.getenv('TELEGRAM_CHAT_ID')
  
  # التحقق من وجود المتغيرات
  if not bot_token:
      print("❌ TELEGRAM_BOT_TOKEN غير موجود")
      return False
      
  if not chat_id:
      print("❌ TELEGRAM_CHAT_ID غير موجود")
      return False
  
  print(f"🔍 Bot Token: {bot_token[:10]}...")
  print(f"🔍 Chat ID: {chat_id}")
  
  url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
  
  payload = {
      'chat_id': chat_id,
      'text': message,
      'parse_mode': 'HTML'
  }
  
  try:
      response = requests.post(url, data=payload, timeout=30)
      
      print(f"📡 Response Status: {response.status_code}")
      print(f"📡 Response: {response.text}")
      
      if response.status_code == 200:
          result = response.json()
          if result.get('ok'):
              print("✅ تم إرسال الرسالة بنجاح!")
              return True
          else:
              print(f"❌ خطأ من تليجرام: {result}")
              return False
      else:
          print(f"❌ خطأ HTTP: {response.status_code}")
          print(f"❌ Response: {response.text}")
          return False
          
  except Exception as e:
      print(f"❌ خطأ في إرسال الرسالة: {str(e)}")
      return False

def create_report():
  """إنشاء تقرير العملات الشهري"""
  print("🚀 بدء تشغيل بوت العملات...")
  
  # جلب أسعار العملات
  print("📊 جلب أسعار العملات...")
  prices = get_crypto_prices()
  
  # إنشاء التقرير
  current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
  
  report = f"""
🚀 <b>تقرير العملات الرقمية الشهري</b>
📅 التاريخ: {current_date}

💰 <b>أسعار العملات الحالية:</b>

🔸 Bitcoin (BTC): {prices.get('BTCUSDT', 'غير متوفر')}
🔸 Ethereum (ETH): {prices.get('ETHUSDT', 'غير متوفر')}
🔸 Binance Coin (BNB): {prices.get('BNBUSDT', 'غير متوفر')}
🔸 Solana (SOL): {prices.get('SOLUSDT', 'غير متوفر')}
🔸 XRP: {prices.get('XRPUSDT', 'غير متوفر')}

📈 <b>ملاحظة:</b> هذا تقرير آلي يتم إرساله شهرياً

🤖 بوت العملات الرقمية
  """.strip()
  
  print("📝 تم إنشاء التقرير:")
  print(report)
  
  # إرسال التقرير
  print("📤 إرسال التقرير...")
  success = send_telegram_message(report)
  
  if success:
      print("✅ تم إرسال التقرير بنجاح!")
  else:
      print("❌ فشل في إرسال التقرير")
  
  print("🏁 تم الانتهاء من التشغيل")

if __name__ == "__main__":
  create_report()
