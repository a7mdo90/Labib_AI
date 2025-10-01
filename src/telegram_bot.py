import os
import csv
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram.error import NetworkError

from google.cloud import vision
from openai import OpenAI
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# ————— Load environment —————
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# ————— Logging setup —————
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    level=logging.INFO
)

# ————— Clients & Collections —————
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
vision_client = vision.ImageAnnotatorClient()

chroma_client = chromadb.PersistentClient(path="/app/.chroma")
print("✅ ChromaDB path loaded:", os.path.exists("/app/.chroma"))
emb_fn = OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY)
try:
    collection = chroma_client.get_or_create_collection(

        name="student_textbooks",
        embedding_function=emb_fn
    )
except:
    collection = chroma_client.get_or_create_collection(

        name="student_textbooks",
        embedding_function=emb_fn
    )



# ————— States —————
ASK_PHONE, GRADE, SUBJECT, QUESTION, RATING, COMMENT = range(6)

# ————— CSV logs —————
INTERACTIONS_LOG = "student_logs.csv"
FEEDBACK_LOG = "feedback_logs.csv"

def log_interaction(grade, subject, question, answer, phone):
    with open(INTERACTIONS_LOG, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            datetime.now(), phone, grade, subject, question, answer
        ])

def log_feedback(phone, grade, subject, rating, comment):
    with open(FEEDBACK_LOG, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            datetime.now(), phone, grade, subject, rating, comment
        ])

# ————— Grade → Subjects map —————
grade_subjects = {
    "1":  ["عربي","انجليزي","رياضيات","علوم","تربية اسلامية"],
    "2":  ["عربي","انجليزي","رياضيات","علوم","تربية اسلامية"],
    "3":  ["عربي","انجليزي","رياضيات","علوم","تربية اسلامية"],
    "4":  ["عربي","انجليزي","رياضيات","علوم","تربية اسلامية","اجتماعيات"],
    "5":  ["عربي","انجليزي","رياضيات","علوم","تربية اسلامية","اجتماعيات"],
    "6":  ["عربي","انجليزي","رياضيات","علوم","تربية اسلامية","اجتماعيات"],
    "7":  ["عربي","انجليزي","رياضيات","علوم","تربية اسلامية","اجتماعيات"],
    "8":  ["عربي","انجليزي","رياضيات","علوم","تربية اسلامية","اجتماعيات"],
    "9":  ["عربي","انجليزي","رياضيات","علوم","تربية اسلامية","اجتماعيات"],
    "10": ["عربي","انجليزي","رياضيات","تربية اسلامية","اجتماعيات","كيمياء","فيزياء","احياء"],
    "11": ["عربي","انجليزي","رياضيات علمي","رياضيات ادبي","تربية اسلامية","اجتماعيات",
           "كيمياء","فيزياء","احياء","تاريخ","جغرافيا","علم نفس","اللغة الفرنسية","جيولوجيا"],
    "12": ["عربي","انجليزي","رياضيات احصاء ادبي","تربية اسلامية","تاريخ","جغرافيا",
           "فلسفة","اللغة الفرنسية","دستور","رياضيات علمي","كيمياء","فيزياء","احياء"],
}

# ————— System prompt —————
system_prompt = (
    "أنت معلم كويتي محترف وذو خبرة في تدريس جميع المواد من الصف الأول إلى الصف الثاني عشر "
    "وفقًا لمنهج وزارة التربية في الكويت.\n\n"
    "لقد تم تزويدك بنسخة رقمية من محتوى الكتاب المدرسي الرسمي، لذلك يجب أن تعتمد فقط على هذا "
    "المحتوى في إجاباتك.\n\n"
    "مهمتك هي مساعدة الطلاب في فهم وإجابة أسئلة نهاية الدروس بشكل دقيق، وبأسلوب بسيط وواضح. "
    "لا تضف أي معلومة من خارج الكتاب. يمكنك إعادة صياغة الإجابات لتسهيل الفهم، لكن بدون تغيير "
    "المعنى.\n\n"
    "إذا لم تجد الإجابة في السياق المقدم، اجب على السؤال بشكل مختصر جداً بدون أي شرح مطول."
)

# ————— Global error handler —————
async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    err = context.error
    logging.exception("❌ Exception in handler:")
    # if user context is available, notify politely
    if update and getattr(update, "effective_message", None):
        try:
            await update.effective_message.reply_text(
                "⚠️ حدثت مشكلة تقنية، الرجاء المحاولة مرة أخرى بعد قليل."
            )
        except Exception:
            pass

# ————— Handlers —————

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[KeyboardButton("📞 شاركني رقمك", request_contact=True)]]
    try:
        await update.message.reply_text(
            "من فضلك اضغط الزر لمشاركة رقم هاتفك للمتابعة:",
            reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True, resize_keyboard=True)
        )
    except NetworkError:
        logging.warning("NetworkError in start()")
    return ASK_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.contact.phone_number
    grade_kb = [[str(i)] for i in range(1,13)]
    try:
        await update.message.reply_text(
            "السلام عليكم و رحمه الله و بركاته\nانتو الحين في اي صف؟",
            reply_markup=ReplyKeyboardMarkup(grade_kb, one_time_keyboard=True, resize_keyboard=True)
        )
    except NetworkError:
        logging.warning("NetworkError in get_phone()")
    return GRADE

async def get_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["grade"] = update.message.text
    subjects = grade_subjects.get(context.user_data["grade"], ["عربي","انجليزي"])
    subj_kb  = [[s] for s in subjects]
    try:
        await update.message.reply_text(
            "اي مادة تحتاجون مساعدتي فيها؟",
            reply_markup=ReplyKeyboardMarkup(subj_kb, one_time_keyboard=True, resize_keyboard=True)
        )
    except NetworkError:
        logging.warning("NetworkError in get_grade()")
    return SUBJECT

async def get_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["subject"] = update.message.text
    try:
        await update.message.reply_text("اكتب سؤالك او ارسل صورة من الكتاب 📖")
    except NetworkError:
        logging.warning("NetworkError in get_subject()")
    return QUESTION

async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    grade    = context.user_data["grade"]
    subject  = context.user_data["subject"]
    phone    = context.user_data["phone"]

    # typing...
    try:
        await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    except NetworkError:
        logging.warning("NetworkError sending ChatAction")

    # query ChromaDB
    tag = f"{grade}-{subject}"
    try:
        res         = collection.query(
                        query_texts=[question],
                        n_results=5,
                        where={"tag": {"$eq": tag}}
                      )
        chunks      = res["documents"][0]
        context_str = "\n".join(chunks).strip()
    except Exception:
        logging.warning("Failed ChromaDB query", exc_info=True)
        context_str = ""

    # build & call GPT
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": f"السؤال:\n{question}\n\nالسياق:\n{context_str}"}
    ]
    try:
        resp   = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo", messages=messages
                 )
        answer = resp.choices[0].message.content.strip()
    except Exception:
        logging.exception("OpenAI call failed")
        answer = "❗️ عذرًا، تعذّر الحصول على الإجابة حاليًا."

    # send answer in one shot
    try:
        await update.message.reply_text(f"🧠 الجواب:\n{answer}")
    except NetworkError:
        logging.warning("NetworkError replying with answer")

    # log interaction
    log_interaction(grade, subject, question, answer, phone)

    # offer next steps
    next_kb = [["/change"], ["/end"]]
    try:
        await update.message.reply_text(
            "📚 يمكنك: سؤال آخر، /change لتغيير الصف/المادة، أو /end لإنهاء الجلسة.",
            reply_markup=ReplyKeyboardMarkup(next_kb, one_time_keyboard=True, resize_keyboard=True)
        )
    except NetworkError:
        logging.warning("NetworkError sending next_kb")

    return QUESTION

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo      = await update.message.photo[-1].get_file()
        photo_path = "temp.jpg"
        await photo.download_to_drive(photo_path)
        with open(photo_path, "rb") as f:
            img  = vision.Image(content=f.read())
            text = vision_client.document_text_detection(image=img)\
                                 .full_text_annotation.text.strip()
    except Exception:
        logging.exception("Vision OCR failed")
        text = ""

    # feed it into get_question
    update.message.text = text or " "  # avoid empty
    return await get_question(update, context)

async def change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # clear and re-ask grade
    context.user_data.pop("grade",   None)
    context.user_data.pop("subject", None)
    grade_kb = [[str(i)] for i in range(1,13)]
    try:
        await update.message.reply_text(
            "اختر صفك الجديد:",
            reply_markup=ReplyKeyboardMarkup(grade_kb, one_time_keyboard=True, resize_keyboard=True)
        )
    except NetworkError:
        logging.warning("NetworkError in change()")
    return GRADE

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "شكراً لاستخدام البوت! كيف تقيّم تجربتك؟",
            reply_markup=ReplyKeyboardMarkup([["👍","👎"]], one_time_keyboard=True, resize_keyboard=True)
        )
    except NetworkError:
        logging.warning("NetworkError in end()")
    return RATING

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rating = update.message.text
    context.user_data["rating"] = rating

    if rating == "👍":
        log_feedback(
            phone   = context.user_data["phone"],
            grade   = context.user_data.get("grade",""),
            subject = context.user_data.get("subject",""),
            rating  = "up", comment=""
        )
        try:
            await update.message.reply_text("🙏 شكراً لتقييمك الإيجابي. في أمان الله!")
        except NetworkError:
            logging.warning("NetworkError sending thumbs-up thanks")
        return ConversationHandler.END
    else:  # 👎
        try:
            await update.message.reply_text("نأسف لعدم رضاك. كيف يمكننا التحسين؟")
        except NetworkError:
            logging.warning("NetworkError asking for comment")
        return COMMENT

async def handle_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    comment = update.message.text
    log_feedback(
        phone   = context.user_data["phone"],
        grade   = context.user_data.get("grade",""),
        subject = context.user_data.get("subject",""),
        rating  = "down", comment=comment
    )
    try:
        await update.message.reply_text("🙏 شكراً لملاحظاتك. سنسعى لتحسين الأداء. في أمان الله!")
    except NetworkError:
        logging.warning("NetworkError sending final thanks")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("تم إلغاء المحادثة.")
    except NetworkError:
        pass
    return ConversationHandler.END

# ————— Main —————
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_PHONE: [ MessageHandler(filters.CONTACT, get_phone) ],
            GRADE:     [ MessageHandler(filters.TEXT & ~filters.COMMAND, get_grade) ],
            SUBJECT:   [ MessageHandler(filters.TEXT & ~filters.COMMAND, get_subject) ],
            QUESTION:  [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_question),
                MessageHandler(filters.PHOTO, handle_photo),
            ],
            RATING:    [ MessageHandler(filters.Regex("^(👍|👎)$"), handle_rating) ],
            COMMENT:   [ MessageHandler(filters.TEXT & ~filters.COMMAND, handle_comment) ],
        },
        fallbacks=[
            CommandHandler("change", change),
            CommandHandler("end",    end),
            CommandHandler("cancel", cancel),
        ],
        allow_reentry=True
    )

    app.add_handler(conv)
    # register global error handler
    app.add_error_handler(global_error_handler)

    print("🤖 Telegram bot is running (with resilience!)")
    app.run_polling()

if __name__ == "__main__":
    main()
