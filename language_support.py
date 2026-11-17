import re


def normalize_hindi_message(message):

    text = str(message).strip()

    # ------------------------------------------------
    # STEP 1: COMPLETE PHRASE NORMALIZATION
    # Longer phrases are processed before individual words.
    # ------------------------------------------------

    phrase_replacements = {

        # Hindi safety warnings
        "अपना OTP किसी के साथ साझा न करें":
            "never share your OTP with anyone",

        "अपना ओटीपी किसी के साथ साझा न करें":
            "never share your OTP with anyone",

        "अपना पासवर्ड किसी को मत बताना":
            "never tell anyone your password",

        "अपना पिन किसी को मत बताना":
            "never tell anyone your PIN",

        "किसी के साथ OTP साझा न करें":
            "never share your OTP with anyone",

        "किसी को अपना OTP न बताएं":
            "never tell anyone your OTP",

        "किसी को अपना पासवर्ड न बताएं":
            "never tell anyone your password",

        # Roman Hindi safety warnings
        "Apna password kisi ko mat batana":
            "never tell anyone your password",

        "Apna OTP kisi ko mat batana":
            "never tell anyone your OTP",

        "Apna PIN kisi ko mat batana":
            "never tell anyone your PIN",

        "OTP kisi ke saath share mat karo":
            "never share your OTP with anyone",

        "OTP kisi ke saath share na karein":
            "never share your OTP with anyone",

        "password kisi ko mat batana":
            "never tell anyone your password",

        "password kisi ko nahi batana":
            "never tell anyone your password",

        # Hindi scam phrases
        "मुझे अपना OTP बताओ":
            "tell me your OTP",

        "मुझे अपना ओटीपी बताओ":
            "tell me your OTP",

        "आपका बैंक खाता बंद हो जाएगा":
            "your bank account will be blocked",

        "बिजली कनेक्शन कट जाएगा":
            "electricity connection will be disconnected",

        "बिजली का कनेक्शन कट जाएगा":
            "electricity connection will be disconnected",

        "अभी बिल भरो":
            "pay bill now",

        "इनाम पाने के लिए क्लिक करें":
            "click to claim prize",

        "आपने लॉटरी जीती है":
            "you have won lottery",

        "आपका मोबाइल रिचार्ज सफल रहा":
            "your mobile recharge was successful",

        "आपका मोबाइल रिचार्ज सफलतापूर्वक हो गया":
            "your mobile recharge was successful",

        "आपका बिजली बिल सफलतापूर्वक जमा हो गया है":
            "your electricity bill payment was successful",

        "आपका वेतन आपके बैंक खाते में जमा हो गया है":
            "your salary has been credited to your bank account",

        # Roman Hinglish scam phrases
        "Mujhe apna OTP batao":
            "tell me your OTP",

        "Aapko cashback mila hai claim karo":
            "you received cashback claim",

        "Aap lottery jeet gaye hain":
            "you have won lottery",

        "Aapka bank account band ho jayega":
            "your bank account will be blocked",

        "KYC update karne ke liye link kholo":
            "open link for KYC update",

        "Bijli connection kat jayega":
            "electricity connection will be disconnected",

        "Bijli ka connection kat jayega":
            "electricity connection will be disconnected",

        "bill bharo":
            "pay bill",

        "Screen share karo payment receive karne ke liye":
            "share your screen to receive payment",

        "screen share karo":
            "share your screen",

        "payment receive karne ke liye":
            "to receive payment",

        "Aapka mobile recharge successful ho gaya hai":
            "your mobile recharge was successful",

        "Aapka mobile recharge safal raha":
            "your mobile recharge was successful",

        "Aapka payment successfully complete ho gaya hai":
            "your payment was successfully completed",

        "Aapka salary bank account mein credit ho gaya hai":
            "your salary has been credited to your bank account",

        "Aapka order dispatch ho gaya hai":
            "your order has been dispatched",

        "Aap lottery jeet gaye hain, abhi claim karein":
            "you have won lottery, claim now",

        "band ho jayega":
            "will be blocked",

        "kat jayega":
            "will be disconnected",

        "jeet gaye hain":
            "have won",

        "jeet gaye":
            "won",

        "mila hai":
            "received",

        "claim karo":
            "claim",

        "claim karein":
            "claim",

        "verify karo":
            "verify",

        "link kholo":
            "open link",

        "kisi ko mat batana":
            "never tell anyone",

        "kisi ke saath share mat karo":
            "never share with anyone"
    }

    for source, replacement in sorted(
        phrase_replacements.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):

        pattern = (
            r"(?<!\w)"
            + re.escape(source)
            + r"(?!\w)"
        )

        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE
        )

    # ------------------------------------------------
    # STEP 2: INDIVIDUAL HINDI WORD NORMALIZATION
    # Avoid translating common verbs without context.
    # ------------------------------------------------

    hindi_replacements = {

        "बैंक खाता": "bank account",
        "बैंक": "bank",
        "खाता": "account",

        "बंद हो जाएगा": "will be blocked",
        "बंद": "blocked",

        "इनाम": "prize",
        "पुरस्कार": "reward",
        "लॉटरी": "lottery",

        "जीत गए": "won",
        "जीती": "won",
        "जीते": "won",
        "जीता": "won",

        "ओटीपी": "OTP",
        "पासवर्ड": "password",
        "पिन": "PIN",

        "भेजें": "send",
        "भेजो": "send",
        "बताओ": "tell",
        "बताएं": "tell",

        "तुरंत": "urgent",
        "अभी": "now",

        "क्लिक करें": "click",
        "क्लिक": "click",
        "खोलें": "open",

        "पाने": "claim",
        "के लिए": "for",

        "आपने": "you",
        "आपका": "your",
        "आपके": "your",
        "आपकी": "your",
        "अपना": "your",

        "हैं": "are",
        "है": "is"
    }

    for source, replacement in sorted(
        hindi_replacements.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):

        pattern = (
            r"(?<!\w)"
            + re.escape(source)
            + r"(?!\w)"
        )

        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE
        )

    # ------------------------------------------------
    # STEP 3: COMMON ROMAN HINGLISH WORDS
    # ------------------------------------------------

    hinglish_replacements = {

        "Aapka": "your",
        "Aapke": "your",
        "Aapki": "your",
        "Aapko": "you",
        "Aapne": "you",
        "Apna": "your",
        "Apne": "your",
        "Mujhe": "me",
        "Aap": "you",

        "bhejo": "send",
        "bheje": "send",
        "batao": "tell",
        "kholo": "open",

        "bharo": "pay",
        "abhi": "now",
        "turant": "urgent",

        "nahi hua": "not updated",
        "nahi hai": "is not"
    }

    for source, replacement in sorted(
        hinglish_replacements.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):

        pattern = (
            r"(?<!\w)"
            + re.escape(source)
            + r"(?!\w)"
        )

        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE
        )

    return re.sub(r"\s+", " ", text).strip()