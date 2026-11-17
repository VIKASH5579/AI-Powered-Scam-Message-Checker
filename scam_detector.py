import re
from urllib.parse import urlparse
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# STEP 1: Suspicious keywords

suspicious_keywords = [
    "lottery",
    "winner",
    "claim your prize",
    "urgent",
    "verify your account",
    "kyc",
    "otp",
    "upi pin",
    "bank account blocked",
    "click here",
    "free money",
    "password"
]


# STEP 2: Keyword detection

def detect_scam(message):

    message = message.lower()

    detected_keywords = []

    for keyword in suspicious_keywords:

        if keyword in message:
            detected_keywords.append(keyword)

    return detected_keywords


# STEP 3: Extract URLs

def extract_urls(message):

    url_pattern = (
        r'(?i)\b(?:https?://|www\.)[^\s<>()]+'
        r'|(?<![@\w.-])(?:[a-z0-9-]+\.)+[a-z]{2,}'
        r'(?:/[^\s<>()]*)?'
    )

    urls = re.findall(url_pattern, message)

    urls = [url.rstrip(".,!?;:") for url in urls]

    return urls


def check_suspicious_urls(urls):

    suspicious_domains = [
        "bit.ly",
        "tinyurl.com",
        "t.co",
        "cutt.ly",
        "rb.gy"
    ]

    suspicious_urls = []

    for url in urls:

        has_scheme = url.lower().startswith(("http://", "https://"))

        if url.startswith("www.") or not has_scheme:
            parsed_url = urlparse("http://" + url)
        else:
            parsed_url = urlparse(url)

        domain = (parsed_url.hostname or "").lower()

        if (
            parsed_url.scheme == "http"
            or not has_scheme
            or any(
                domain == d or domain.endswith("." + d)
                for d in suspicious_domains
            )
        ):
            suspicious_urls.append(url)

    return suspicious_urls

# STEP 4: Extract phone numbers

def extract_phone_numbers(message):

    phone_pattern = (
        r'(?<!\d)(?:\+91[\s-]?)?'
        r'[6-9]\d{4}[\s-]?\d{5}(?!\d)'
    )

    return re.findall(phone_pattern, message)


# STEP 6: Calculate risk score

def calculate_risk(message, keywords, suspicious_urls):

    message = message.lower()

    score = 0
    reasons = []

    # Lottery and prize detection
    if any(word in message for word in [
        "lottery", "winner", "claim your prize",
        "won lottery", "have won"
    ]):
        score += 25
        reasons.append("Lottery or prize-related message")

    # KYC fraud detection
    if "kyc" in message and any(
        word in message for word in [
            "blocked", "suspended", "update",
            "verify", "link"
        ]
    ):
        score += 20
        reasons.append("Suspicious KYC update warning")

    # Bank account threat
    if any(word in message for word in [
        "account", "bank account"
    ]) and any(word in message for word in [
        "blocked", "suspended", "closed"
    ]):
        score += 25
        reasons.append("Threat of account blocking or suspension")

    # Urgent language
    if any(word in message for word in [
        "urgent", "immediately", "hurry",
        "limited time", "now"
    ]):
        score += 10
        reasons.append("Urgent or pressure-based language")

    # Sensitive information
    if any(word in message for word in [
        "otp", "upi pin", "password"
    ]):
        score += 30
        reasons.append("Sensitive banking information mentioned")

    # Explicit credential requests
    credential_requests = [
        "share your otp",
        "send your otp",
        "provide your otp",
        "share your upi pin",
        "send your upi pin",
        "tell me your password",
        "tell me your otp",
        "give me your otp",
        "send me your otp",
        "provide me your otp",
        "tell me your pin"
    ]

    if any(phrase in message for phrase in credential_requests):
        score += 20
        reasons.append("Explicit request for confidential information")

    # Promotional language
    promotional_words = [
        "perks", "offer", "reward", "cashback",
        "bonus", "discount", "free gift",
        "claim now", "special offer"
    ]

    has_promotion = any(
        word in message for word in promotional_words
    )

    if has_promotion:
        score += 15
        reasons.append("Promotional or reward-related wording")

    # Suspicious money bait
    if any(word in message for word in [
        "win money", "earn money", "get cash",
        "free money", "rs888", "₹888"
    ]):
        score += 15
        reasons.append("Suspicious money or reward offer")

    # Promotion combined with claim
    if has_promotion and any(word in message for word in [
        "claim now", "claim your", "claim",
        "receive reward", "won rs",
        "cashback mila", "cashback received",
        "free reward"
    ]):
        score += 20
        reasons.append("Reward promotion with claim language")

    # Suspicious URL
    if suspicious_urls:
        score += 20
        reasons.append("Suspicious URL pattern detected")

    # Promotion with suspicious URL
    if has_promotion and suspicious_urls:
        score += 15
        reasons.append("Promotion combined with suspicious link")

    score = min(score, 100)

    if score <= 30:
        risk_level = "LOW"
    elif score <= 60:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return score, risk_level, reasons


# STEP 9: Unified Detection Function

def analyze_message(message):

    # Perform all detection operations
    keywords = detect_scam(message)

    urls = extract_urls(message)

    phones = extract_phone_numbers(message)

    suspicious_urls = check_suspicious_urls(urls)

    score, risk_level, reasons = calculate_risk(
        message,
        keywords,
        suspicious_urls
    )

    # Create complete analysis report
    result = {
        "message": message,
        "keywords": keywords,
        "urls": urls,
        "phone_numbers": phones,
        "suspicious_urls": suspicious_urls,
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons
    }

    return result


# STEP 10: Run the application

def main():

    user_message = input("\nEnter your message: ")

    result = analyze_message(user_message)

    print("\n========== SCAM ANALYSIS REPORT ==========")

    print("Risk Score:", result["risk_score"], "/ 100")
    print("Risk Level:", result["risk_level"])

    print("\nDetected Keywords:")
    print(result["keywords"])

    print("\nExtracted URLs:")
    print(result["urls"])

    print("\nExtracted Phone Numbers:")
    print(result["phone_numbers"])

    print("\nSuspicious URLs:")
    print(result["suspicious_urls"])

    print("\nReasons:")

    for reason in result["reasons"]:
        print("-", reason)

    print("\n==========================================")


if __name__ == "__main__":
    main()
    
def extract_text_from_image(image_path):

    try:
        image = Image.open(image_path)

        extracted_text = pytesseract.image_to_string(
            image,
            lang="eng"
        )

        return extracted_text.strip()

    except Exception as error:
        print("OCR Error:", error)
        return ""
    
def redact_sensitive_info(message):

    # 1. Indian mobile numbers (+91, spaces and hyphens supported)
    message = re.sub(
        r'(?<!\d)(\+91[\s-]?)?([6-9]\d{4})[\s-]?(\d{5})(?!\d)',
        lambda m: (m.group(1) or '') + m.group(2)[:2]
        + '******' + m.group(3)[-2:],
        message
    )

    # 2. Six-digit OTP
    message = re.sub(
        r'\b\d{6}\b',
        '******',
        message
    )

    # 3. Email addresses (including OCR spaces)
    message = re.sub(
        r'\b([A-Za-z0-9])[A-Za-z0-9._%+-]*\s*@\s*'
        r'([A-Za-z0-9-]+)\s*\.\s*([A-Za-z]{2,})\b',
        r'\1***@\2.\3',
        message
    )

    # 4. UPI IDs
    message = re.sub(
        r'\b([A-Za-z0-9])[A-Za-z0-9._-]*@'
        r'(?:upi|ybl|paytm|oksbi|okaxis|okhdfcbank|ibl|axl|okicici)\b',
        r'\1***@upi',
        message,
        flags=re.IGNORECASE
    )

    return message