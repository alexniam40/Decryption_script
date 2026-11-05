import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# আপনার গিটহাবে থাকা ডিক्रিপশন স্ক্রিপ্টগুলো ইম্পোর্ট করা
import DARKTUNNEL
import HTTPCUSTOM
import HTTPINJECTOR
import NPVTUNNEL
import SSCCUSTOM

# লগিং সেটআপ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# আপনার টেলিগ্রাম বটের টোকেন এখানে বসান (অথবা এনভায়রনমেন্ট ভেরিয়েবল থেকে নিতে পারেন)
TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    file = await doc.get_file()
    file_bytes = await file.download_as_bytearray()
    file_name = doc.file_name.lower()
    
    result = None
    
    # ফাইルの নাম বা এক্সটেনশন অনুযায়ী সংশ্লিষ্ট স্ক্রিপ্ট কল করা
    try:
        if file_name.endswith(".ehi"):
            result = HTTPINJECTOR.run(bytes(file_bytes))
        elif file_name.endswith(".hc"):
            result = HTTPCUSTOM.run(bytes(file_bytes))
        elif "npvt" in file_name or file_name.endswith(".npvt"):
            result = NPVTUNNEL.run(bytes(file_bytes))
        elif "ssc" in file_name or file_name.endswith(".ssc"):
            result = SSCCUSTOM.run(bytes(file_bytes))
        elif "dark" in file_name:
            result = DARKTUNNEL.run(bytes(file_bytes))
        else:
            # যদি সরাসরি ফাইল রিড করে ট্রাই করতে চান
            for decryptor in [HTTPINJECTOR, HTTPCUSTOM, NPVTUNNEL, SSCCUSTOM, DARKTUNNEL]:
                res = decryptor.run(bytes(file_bytes))
                if res:
                    result = res
                    break
    except Exception as e:
        result = f"ডিক্রিপশন করার সময় ত্রুটি হয়েছে: {str(e)}"

    if result:
        # যদি ফলাফল অনেক বড় হয়, টেলিগ্রামের মেসেজ লিমি트 (4096 অক্ষর) বজায় রেখে পাঠানো
        if len(result) > 4000:
            for i in range(0, len(result), 4000):
                await update.message.reply_text(f"```json\n{result[i:i+4000]}\n```", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"```json\n{result}\n```", parse_mode="Markdown")
    else:
        await update.message.reply_text("দুঃখিত, এই ফাইলটি ডিক্রিপ্ট করা সম্ভব হয়নি অথবা ফাইল ফরম্যাট সমর্থিত নয়।")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    print("Bot is running...")
    app.run_polling()
              
