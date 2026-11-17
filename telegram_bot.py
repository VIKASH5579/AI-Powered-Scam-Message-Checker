import os
import tempfile
from language_support import normalize_hindi_message
from database import (
    save_analysis,
    save_feedback,
    save_review_submission
)
from scam_detector import extract_text_from_image, redact_sensitive_info
from telegram.request import HTTPXRequest
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from combined_detector import analyze_combined

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Welcome to AI Scam Message Checker!\n\n"
        "Send me any message and I will analyze its scam risk.\n\n"
        "Senior Citizen Mode:\n"
        "Type /senior to get simple explanations "
        "and extra safety warnings."
    )
    
# Senior Citizen Mode Setting
SENIOR_MODE_USERS = set()
    
async def senior_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    SENIOR_MODE_USERS.add(user_id)

    await update.message.reply_text(
        "👴 SENIOR CITIZEN MODE: ON 👵\n\n"
        "Ab scam reports simple Hindi aur English mein milengi.\n\n"
        "Stay Alert. Stay Safe! 🛡️"
    )
    
async def normal_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    SENIOR_MODE_USERS.discard(user_id)

    await update.message.reply_text(
        "NORMAL MODE: ON\n\n"
        "You will now receive standard scam analysis reports."
    )


async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    message = update.message.text.strip()

    if not message:
        await update.message.reply_text(
            "Please send a valid text message."
        )
        return

    if len(message) > 4000:
        await update.message.reply_text(
            "Message too long! Please send a message under 4000 characters."
        )
        return

    try:
        result = analyze_combined(message)
        
        analysis_id = save_analysis("text", message, result)
        
        context.user_data[f"analysis_{analysis_id}"] = message
        
        context.job_queue.run_once(
            lambda job_context: job_context.user_data.pop(
                f"analysis_{analysis_id}", None
            ),
            600,
            data=None,
            chat_id=update.effective_chat.id,
            user_id=update.effective_user.id
        )
        
        reasons = result["reasons"]
        
        user_id = update.effective_user.id

        is_senior = user_id in SENIOR_MODE_USERS

        if is_senior:

            if result["risk_level"] == "HIGH":
                senior_explanation = (
                    "\n\n🚨 KHATRA! / DANGER!\n"
                    "Yeh message scam ho sakta hai.\n"
                    "Is par bharosa mat karein.\n"
                    "OTP, PIN ya password bilkul share na karein.\n"
                    "Kisi unknown link par click na karein.\n"
                    "Zarurat ho to apne family member se madad lein."
                )

            elif result["risk_level"] == "MEDIUM":
                senior_explanation = (
                    "\n\n⚠️ SAVDHAN / BE CAREFUL!\n"
                    "Is message mein shak wali baatein hain.\n"
                    "Koi payment ya personal information share na karein.\n"
                    "Pehle official source se verify karein."
                )

            else:
                senior_explanation = (
                    "\n\n✅ LOW RISK / KAM KHATRA\n"
                    "Filhaal message mein kam risk mila hai.\n"
                    "Phir bhi OTP, PIN ya password share na karein."
                )

        else:
            senior_explanation = ""

        reason_text = "\n".join(
            ["- " + reason for reason in reasons]
        ) if reasons else "No specific rule-based warning found."
        
        senior_warning = ""

        if result["risk_level"] == "HIGH" and not is_senior:
            senior_warning = (
                "\n\nIMPORTANT WARNING:\n"
                "This message may be dangerous.\n"
                "Never share OTP, PIN or password."
            )

        elif result["risk_level"] == "MEDIUM" and not is_senior:
            senior_warning = (
                "\n\nPLEASE BE CAREFUL:\n"
                "Is message mein kuch shak wali baatein hain.\n"
                "Pehle bank ya company se verify karein."
            )

        reply = (
            "SCAM ANALYSIS REPORT\n\n"
            f"Rule Score: {result['rule_score']}/100\n"
            f"AI Scam Score: {result['ml_score']}%\n"
            f"AI Prediction: {'SCAM' if result['ml_prediction'] == 1 else 'GENUINE'}\n"
            f"Final Risk Score: {result['final_score']}/100\n"
            f"Risk Level: {result['risk_level']}\n\n"
            f"{senior_explanation}\n\n"
            f"Reasons:\n{reason_text}\n\n"
            "Warning: This is an experimental checker. "
            "Never share OTP, UPI PIN or passwords."
            f"{senior_warning}"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "👍 Yes",
                    callback_data=f"feedback_yes_{analysis_id}"
                ),
                InlineKeyboardButton(
                    "👎 No",
                    callback_data=f"feedback_no_{analysis_id}"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            reply,
            reply_markup=reply_markup
        )

    except Exception:
        print("Analysis failed. Sensitive details hidden.")

        await update.message.reply_text(
            "Sorry! Message analysis failed. Please try again."
        )
        
async def check_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.photo:
        return

    await update.message.reply_text(
        "Screenshot received! Analyzing..."
    )

    image_path = None

    try:
        # Download screenshot
        photo = update.message.photo[-1]
        photo_file = await photo.get_file()

        with tempfile.NamedTemporaryFile(
            suffix=".jpg", delete=False
        ) as temp_file:
            image_path = temp_file.name

        await photo_file.download_to_drive(image_path)

        # Extract screenshot text
        extracted_text = extract_text_from_image(image_path)

        if not extracted_text or not extracted_text.strip():
            await update.message.reply_text(
                "No readable text found in this screenshot."
            )
            return

        # Analyze original text.
        # analyze_combined() handles Hindi normalization internally.
        result = analyze_combined(extracted_text)

        save_analysis("screenshot", extracted_text, result)

        # Prepare reasons
        reasons = result["reasons"]

        reason_text = "\n".join(
            ["- " + reason for reason in reasons]
        ) if reasons else "No specific warning found."

        # Final decision
        decision = result["final_decision"]

        reply = (
            "📸 SCREENSHOT SCAM ANALYSIS\n\n"
            f"Extracted Text:\n"
            f"{redact_sensitive_info(extracted_text)[:2500]}\n\n"
            f"Rule Score: {result['rule_score']}/100\n"
            f"AI Scam Score: {result['ml_score']}%\n"
            f"AI Prediction: "
            f"{'SCAM' if result['ml_prediction'] == 1 else 'GENUINE'}\n"
            f"Final Decision: {decision}\n"
            f"Final Risk Score: {result['final_score']}/100\n"
            f"Risk Level: {result['risk_level']}\n"
            f"Category: {result['category']}\n\n"
            f"Reasons:\n{reason_text}\n\n"
            "⚠️ Safety Reminder:\n"
            "Never share OTP, UPI PIN or passwords."
        )

        # Senior Citizen Friendly Mode
        user_id = update.effective_user.id

        if user_id in SENIOR_MODE_USERS:

            if result["risk_level"] == "HIGH":
                senior_explanation = (
                    "\n\n🚨 KHATRA! / DANGER!\n\n"
                    "Yeh message scam ho sakta hai.\n"
                    "यह संदेश धोखाधड़ी हो सकता है।\n\n"
                    "OTP, PIN ya password bilkul share na karein.\n"
                    "किसी को OTP, PIN या पासवर्ड न दें।\n\n"
                    "Koi unknown link par click na karein.\n"
                    "अनजान लिंक पर क्लिक न करें।\n\n"
                    "Zarurat pade toh family member se madad lein."
                )

            elif result["risk_level"] == "MEDIUM":
                senior_explanation = (
                    "\n\n⚠️ SAVDHAN / BE CAREFUL!\n\n"
                    "Is message mein kuch shak wali baatein hain.\n"
                    "इस संदेश में कुछ संदिग्ध बातें हैं।\n\n"
                    "Payment ya personal information share na karein.\n"
                    "पैसे या निजी जानकारी साझा न करें।\n\n"
                    "Official source se verify karein."
                )

            else:
                senior_explanation = (
                    "\n\n✅ LOW RISK / KAM KHATRA\n\n"
                    "Yeh message filhaal kam risk wala lagta hai.\n"
                    "यह संदेश फिलहाल कम जोखिम वाला लगता है।\n\n"
                    "Phir bhi OTP, PIN ya password share na karein.\n"
                    "फिर भी OTP, PIN या पासवर्ड साझा न करें।"
                )

            reply += senior_explanation

        await update.message.reply_text(reply)

    except Exception:
        print("Photo Analysis Error:")

        await update.message.reply_text(
            "Sorry! Screenshot analysis failed."
        )

    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            
async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    try:
        data = query.data
        parts = data.split("_")

        feedback_type = parts[1]
        analysis_id = int(parts[2])

        if feedback_type == "yes":

            feedback = "correct"
            response = "Thank you! Your feedback has been saved. 👍"

            save_feedback(analysis_id, feedback)
            
            context.user_data.pop(f"analysis_{analysis_id}", None)

            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(response)

        else:

            feedback = "incorrect"
            save_feedback(analysis_id, feedback)

            keyboard = [
                [
                    InlineKeyboardButton(
                        "✅ Yes, share for review",
                        callback_data=f"review_yes_{analysis_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "❌ No, keep private",
                        callback_data=f"review_no_{analysis_id}"
                    )
                ]
            ]

            await query.edit_message_reply_markup(reply_markup=None)

            await query.message.reply_text(
                "Sorry about the incorrect result.\n\n"
                "Would you like to share your original message "
                "for manual review and possible model improvement?\n\n"
                "Your permission is required before saving it.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    except Exception:
        print("Feedback Error:")

        await query.message.reply_text(
            "Sorry! Could not save your feedback."
        )
        
async def handle_review_permission(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    try:
        data = query.data
        parts = data.split("_")

        permission = parts[1]
        analysis_id = int(parts[2])

        if permission == "yes":

            message = context.user_data.get(
                f"analysis_{analysis_id}"
            )

            if not message:
                response = (
                    "Sorry! Original message is no longer available. "
                    "Please send it again if you want to share it."
                )

            else:
                safe_message = redact_sensitive_info(message)

                save_review_submission(
                     analysis_id,
                    safe_message
                )
                
                context.user_data.pop(f"analysis_{analysis_id}", None)

                response = (
                    "Thank you! Your permission has been received. ✅\n\n"
                    "Your redacted message has been saved for manual review.\n"
                    "It will not be used for model training until verified."
                )
    
        else:
            context.user_data.pop(
                f"analysis_{analysis_id}",
                None
            )

            response = (
                "Your message will remain private. "
                "Thank you for your feedback. 🔒"
            )

        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(response)

    except Exception:
        print("Review Permission Error:")

        await query.message.reply_text(
            "Sorry! Could not process your choice."
        )


def main():
    if not TOKEN:
        print("ERROR: Telegram token missing in .env file")
        return

    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30,
        read_timeout=30,
        write_timeout=30,
        pool_timeout=30
    )

    app = (
        Application.builder()
        .token(TOKEN)
        .request(request)
        .get_updates_request(request)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        CommandHandler("senior", senior_mode)
    )
    app.add_handler(
        CommandHandler("normal", normal_mode)
    )
    app.add_handler(
        CallbackQueryHandler(
            handle_feedback,
            pattern=r"^feedback_(yes|no)_\d+$"
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            handle_review_permission,
            pattern=r"^review_(yes|no)_\d+$"
        )
    )
    app.add_handler(
        MessageHandler(filters.PHOTO, check_photo)
    )
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, check_message)
    )

    print("Telegram Scam Checker Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()