from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
import sqlite3
from datetime import datetime
import os

# ========== تنظیمات ==========
TOKEN = os.getenv("8607548620:AAHAmaUMPfANjqUazxK4lnsU_loQlSGt92c")  # بعداً در سرور تنظیم می‌کنیم
ADMIN_ID = 96614184  # <-- آی‌دی عددی خودت رو اینجا بذار

# حالت‌های فرم
(
    NAME, PHONE, COMPANY, BOOTH_SIZE, BOOTH_TYPE,
    BUDGET, EXHIBITION_DATE, DESCRIPTION, CONFIRM
) = range(9)

# ========== دیتابیس ==========
def init_db():
    conn = sqlite3.connect("booth_forms.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        full_name TEXT,
        phone TEXT,
        company TEXT,
        booth_size TEXT,
        booth_type TEXT,
        budget TEXT,
        exhibition_date TEXT,
        description TEXT,
        submitted_at TEXT
    )''')
    conn.commit()
    conn.close()

def save_submission(user_id, username, data):
    conn = sqlite3.connect("booth_forms.db")
    c = conn.cursor()
    c.execute('''INSERT INTO submissions 
        (user_id, username, full_name, phone, company, booth_size, 
         booth_type, budget, exhibition_date, description, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (user_id, username, data['name'], data['phone'], data['company'],
         data['booth_size'], data['booth_type'], data['budget'],
         data['exhibition_date'], data['description'],
         datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# ========== توابع فرم ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋\n"
        "به ربات ثبت درخواست غرفه سازی خوش اومدی.\n\n"
        "برای پر کردن فرم روی /form کلیک کن."
    )

async def form_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "📝 فرم درخواست غرفه سازی\n\n"
        "لطفاً **نام و نام خانوادگی** خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("شماره تماس خود را وارد کنید (مثال: ۰۹۱۲۳۴۵۶۷۸۹):")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("نام شرکت یا برند را وارد کنید:")
    return COMPANY

async def get_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['company'] = update.message.text
    await update.message.reply_text("ابعاد تقریبی غرفه را بنویسید (مثال: ۳×۳ یا ۶×۴ متر):")
    return BOOTH_SIZE

async def get_booth_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['booth_size'] = update.message.text
    keyboard = [["مدولار", "سفارشی"], ["ترکیبی"]]
    await update.message.reply_text(
        "نوع غرفه مورد نظر را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return BOOTH_TYPE

async def get_booth_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['booth_type'] = update.message.text
    await update.message.reply_text(
        "بودجه تقریبی خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove()
    )
    return BUDGET

async def get_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['budget'] = update.message.text
    await update.message.reply_text("تاریخ تقریبی نمایشگاه یا زمان نیاز را بنویسید:")
    return EXHIBITION_DATE

async def get_exhibition_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['exhibition_date'] = update.message.text
    await update.message.reply_text(
        "توضیحات اضافی (طرح خاص، رنگ، نیازمندی ویژه و ...):\n"
        "اگر توضیح ندارید بنویسید «ندارم»"
    )
    return DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text

    data = context.user_data
    summary = (
        f"📋 خلاصه درخواست شما:\n\n"
        f"👤 نام: {data['name']}\n"
        f"📱 تلفن: {data['phone']}\n"
        f"🏢 شرکت: {data['company']}\n"
        f"📏 ابعاد: {data['booth_size']}\n"
        f"🏗 نوع: {data['booth_type']}\n"
        f"💰 بودجه: {data['budget']}\n"
        f"📅 تاریخ: {data['exhibition_date']}\n"
        f"📝 توضیحات: {data['description']}\n\n"
        f"آیا اطلاعات بالا صحیح است؟"
    )
    keyboard = [["✅ تأیید و ارسال", "❌ انصراف"]]
    await update.message.reply_text(
        summary,
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CONFIRM

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "✅ تأیید و ارسال":
        user = update.effective_user
        save_submission(user.id, user.username or "", context.user_data)

        await update.message.reply_text(
            "✅ درخواست شما با موفقیت ثبت شد.\n"
            "به زودی با شما تماس می‌گیریم.",
            reply_markup=ReplyKeyboardRemove()
        )

        # پیام کامل برای تو (بعداً فوروارد کن برای طراح)
        data = context.user_data
        admin_msg = (
            f"🆕 درخواست جدید غرفه سازی\n\n"
            f"👤 کاربر: {user.full_name}\n"
            f"یوزرنیم: @{user.username or 'ندارد'}\n"
            f"آی‌دی: `{user.id}`\n\n"
            f"نام: {data['name']}\n"
            f"تلفن: {data['phone']}\n"
            f"شرکت: {data['company']}\n"
            f"ابعاد: {data['booth_size']}\n"
            f"نوع: {data['booth_type']}\n"
            f"بودجه: {data['budget']}\n"
            f"تاریخ: {data['exhibition_date']}\n"
            f"توضیحات: {data['description']}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="Markdown")

    else:
        await update.message.reply_text(
            "❌ درخواست لغو شد.\nبرای شروع مجدد /form را بزنید.",
            reply_markup=ReplyKeyboardRemove()
        )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "فرم لغو شد. برای شروع مجدد /form را بزنید.",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

# ========== دستورات ادمین (فقط برای خودت) ==========
async def list_submissions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect("booth_forms.db")
    c = conn.cursor()
    c.execute("SELECT id, full_name, phone, company, submitted_at FROM submissions ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("هنوز هیچ درخواستی ثبت نشده.")
        return

    text = "📋 لیست درخواست‌ها:\n\n"
    for row in rows:
        text += f"#{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}\n"
    text += "\nبرای دیدن جزئیات: /view شماره"

    await update.message.reply_text(text)

async def view_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("مثال: /view 3")
        return

    try:
        sub_id = int(context.args[0])
    except:
        await update.message.reply_text("شماره باید عدد باشد.")
        return

    conn = sqlite3.connect("booth_forms.db")
    c = conn.cursor()
    c.execute("SELECT * FROM submissions WHERE id = ?", (sub_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        await update.message.reply_text("درخواستی با این شماره پیدا نشد.")
        return

    text = (
        f"📄 جزئیات درخواست #{row[0]}\n\n"
        f"آی‌دی کاربر: `{row[1]}`\n"
        f"یوزرنیم: @{row[2] or 'ندارد'}\n"
        f"نام: {row[3]}\n"
        f"تلفن: {row[4]}\n"
        f"شرکت: {row[5]}\n"
        f"ابعاد: {row[6]}\n"
        f"نوع: {row[7]}\n"
        f"بودجه: {row[8]}\n"
        f"تاریخ: {row[9]}\n"
        f"توضیحات: {row[10]}\n"
        f"زمان ثبت: {row[11]}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ========== اجرای ربات ==========
def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("form", form_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)],
            BOOTH_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_booth_size)],
            BOOTH_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_booth_type)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_budget)],
            EXHIBITION_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_exhibition_date)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("list", list_submissions))
    app.add_handler(CommandHandler("view", view_submission))

    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()
