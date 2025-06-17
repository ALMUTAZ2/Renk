import time
import os
from datetime import datetime
import requests

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# العملات المطلوبة
symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]

def get_crypto_price(symbol):
  """جلب سعر العملة من Binance API"""
  try:
      url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
      response = requests.get(url)
      data = response.json()
      return float(data['price'])
  except Exception as e:
      print(f"❌ خطأ في جلب سعر {symbol}: {e}")
      return None

def send_telegram_message(text):
  """إرسال رسالة عبر Telegram باستخدام requests"""
  try:
      url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
      payload = {
          'chat_id': TELEGRAM_CHAT_ID,
          'text': text,
          'parse_mode': 'Markdown'
      }
      response = requests.post(url, data=payload)
      if response.status_code == 200:
          print("✅ تم إرسال التقرير بنجاح")
          return True
      else:
          print(f"❌ خطأ في إرسال الرسالة: {response.text}")
          return False
  except Exception as e:
      print(f"❌ خطأ في إرسال الرسالة: {e}")
      return False

def main():
  """الوظيفة الرئيسية"""
  print("🚀 بدء تشغيل بوت العملات...")
  
  report = "📊 **تقرير العملات الشهري - Renko Monthly**\n\n"
  
  for symbol in symbols:
      price = get_crypto_price(symbol)
      if price:
          # تنسيق السعر حسب العملة
          if symbol == "BTCUSDT":
              formatted_price = f"${price:,.2f}"
          elif symbol == "ETHUSDT":
              formatted_price = f"${price:,.2f}"
          else:
              formatted_price = f"${price:.4f}"
          
          report += f"🔸 **{symbol.replace('USDT', '')}**: {formatted_price}\n"
      else:
          report += f"❌ **{symbol.replace('USDT', '')}**: غير متاح\n"
      
      time.sleep(0.5)  # تجنب الإفراط في الطلبات
  
  report += f"\n⏰ **وقت التحديث**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
  
  # إرسال التقرير
  send_telegram_message(report)
  print("✅ تم الانتهاء من التقرير")

if __name__ == "__main__":
  main()
