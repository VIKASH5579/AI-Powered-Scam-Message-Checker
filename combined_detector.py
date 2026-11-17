import re
import joblib

from scam_detector import analyze_message
from language_support import normalize_hindi_message


# Load trained ML model
model = joblib.load("models/scam_model.pkl")


# ---------------------------------------
# STEP 1: CONTEXT SIGNAL DETECTION
# ---------------------------------------

def detect_context_signals(message):

    text = message.lower()

    # Safety and awareness messages
    safety_patterns = [

        r"\bnever share\b",
        r"\bdo not share\b",
        r"\bdon't share\b",

        r"\bnever give\b",
        r"\bdo not give\b",
        r"\bdon't give\b",

        r"\bnever tell anyone\b",
        r"\bnever tell\b",
        r"\bdo not tell\b",
        r"\bdon't tell\b",

        r"\bkeep your (?:otp|pin|password)\b",
        r"\bprotect your (?:otp|pin|password)\b",

        r"\bnever share your screen\b",
        r"\bdo not share your screen\b",
        r"\bdon't share your screen\b",

        r"\bnever install unknown apps\b"
    ]

    safety_warning = any(
        re.search(pattern, text)
        for pattern in safety_patterns
    )

    # Requests for confidential information

    credential_patterns = [

        r"\b(?:send|share|tell|give|provide|reveal)\s+"
        r"(?:me\s+)?(?:your\s+)?"
        r"(?:otp|one time password|upi pin|pin|password|verification code)\b",

        r"\b(?:otp|upi pin|pin|password)"
        r"(?:\s+and\s+(?:otp|pin|password))*\s+"
        r"(?:send|share|tell|provide)\b"
    ]

    # Remove safety-warning phrases before checking
    # for actual credential requests.
    credential_text = text

    for pattern in safety_patterns:
        credential_text = re.sub(
            pattern,
            " ",
            credential_text
        )

    credential_request = any(
        re.search(pattern, credential_text)
        for pattern in credential_patterns
    )

    # Lottery and reward claims
    reward_claim = (
        any(word in text for word in [
            "cashback", "reward", "prize", "lottery"
        ])
        and any(word in text for word in [
            "claim", "receive", "won"
        ])
    )

    lottery_claim = (
        any(word in text for word in [
            "lottery", "lucky draw"
        ])
        and any(word in text for word in [
            "won", "winner", "claim", "click"
        ])
    )

    # Electricity disconnection threat
    electricity_threat = (
        any(word in text for word in [
            "electricity",
            "power connection",
            "bijli connection",
            "electric connection"
        ])
        and any(word in text for word in [
            "disconnected",
            "disconnect",
            "cut off",
            "will be cut",
            "will be disconnected",
            "kat jayega",
            "band ho jayega"
        ])
        and any(word in text for word in [
            "pay now",
            "pay immediately",
            "urgent payment",
            "pay bill",
            "make payment",
            "click",
            "payment",
            "bharo",
            "pay"
        ])
    )

    # Parcel and customs fee pressure
    parcel_fee_scam_signal = (
        any(word in text for word in [
            "parcel", "package", "shipment", "delivery"
        ])
        and any(word in text for word in [
            "on hold", "held", "blocked",
            "customs", "custom fee",
            "delivery fee", "release fee"
        ])
        and any(word in text for word in [
            "pay", "payment", "fee", "click",
            "link", "verify"
        ])
    )

    # Remote access / screen-sharing request
    remote_access_request = (
        any(word in text for word in [
            "install this app",
            "download this app",
            "install app",
            "remote access",
            "screen sharing",
            "share your screen",
            "share screen",
            "allow screen access",
            "anydesk",
            "teamviewer"
        ])
        and any(word in text for word in [
            "payment",
            "receive money",
            "refund",
            "bank",
            "support",
            "verification",
            "receive payment",
            "get money"
        ])
    )

    # Job registration fee
    job_fee_request = (
        any(word in text for word in [
            "job offer",
            "job registration",
            "work from home",
            "recruitment"
        ])
        and any(word in text for word in [
            "registration fee",
            "pay fee",
            "processing fee",
            "security deposit"
        ])
    )

    # Genuine transaction / service confirmations
    benign_patterns = [

        r"\bmobile recharge was successful\b",
        r"\brecharge successful\b",
        r"\bsuccessfully recharged\b",

        r"\bsalary has been credited\b",
        r"\bsalary credited\b",

        r"\bpayment was successfully completed\b",
        r"\bpayment successfully completed\b",

        r"\belectricity bill payment was successful\b",
        r"\bbill successfully paid\b",

        r"\border has been dispatched\b",
        r"\border dispatched\b",

        r"\btransaction successful\b",
        r"\bpayment successful\b"
    ]

    benign_notice = any(
        re.search(pattern, text)
        for pattern in benign_patterns
    )

    return {
        "safety_warning": safety_warning,
        "credential_request": credential_request,
        "reward_claim": reward_claim,
        "lottery_claim": lottery_claim,
        "electricity_threat": electricity_threat,
        "parcel_fee_scam_signal": parcel_fee_scam_signal,
        "remote_access_request": remote_access_request,
        "job_fee_request": job_fee_request,
        "benign_notice": benign_notice
    }


# ---------------------------------------
# STEP 2: SCAM CATEGORY DETECTION
# ---------------------------------------

def detect_scam_category(message, suspicious_urls):

    text = message.lower()

    categories = {

        "OTP / Account Scam": [
            "otp", "upi pin", "password",
            "verification code"
        ],

        "Bank / KYC Scam": [
            "bank", "kyc", "account blocked",
            "account suspended"
        ],

        "UPI / Payment Scam": [
            "upi", "payment", "refund",
            "transaction", "qr code", "cashback"
        ],

        "Lottery / Prize Scam": [
            "lottery", "prize", "winner",
            "won", "lucky draw", "reward"
        ],

        "Job Scam": [
            "job offer", "work from home",
            "recruitment", "vacancy",
            "registration fee"
        ],

        "Phishing Link Scam": [
            "click here", "verify link",
            "login link", "update your details"
        ],

        "Electricity Payment Scam": [
            "electricity", "power connection",
            "bijli connection"
        ],

        "Parcel / Customs Fee Scam": [
            "parcel", "package", "customs",
            "delivery fee", "shipment"
        ],

        "Remote Access Scam": [
            "screen sharing", "share your screen",
            "remote access", "anydesk",
            "teamviewer"
        ]
    }

    scores = {
        category: sum(
            1 for keyword in keywords
            if keyword in text
        )
        for category, keywords in categories.items()
    }

    if suspicious_urls:
        scores["Phishing Link Scam"] += 2

    highest_score = max(scores.values())

    if highest_score == 0:
        return "Other / Unclassified"

    return max(scores, key=scores.get)


# ---------------------------------------
# STEP 3: COMBINED AI ANALYSIS
# ---------------------------------------

def analyze_combined(message):

    # Normalize Hindi and Hinglish
    normalized_message = normalize_hindi_message(message)

    # Rule-based analysis
    rule_result = analyze_message(normalized_message)

    rule_score = rule_result["risk_score"]

    # ML prediction
    probabilities = model.predict_proba(
        [normalized_message]
    )[0]

    scam_index = list(model.classes_).index(1)

    ml_score = round(
        probabilities[scam_index] * 100, 2
    )

    ml_prediction = 1 if ml_score >= 60 else 0

    # Context analysis
    context = detect_context_signals(
        normalized_message
    )

    # Combine rule and ML scores
    final_score = round(
        (rule_score * 0.60) +
        (ml_score * 0.40)
    )

    reasons = list(rule_result["reasons"])

    suspicious_urls = rule_result["suspicious_urls"]

    # -----------------------------------
    # STEP 4: CONTEXT-BASED ADJUSTMENTS
    # -----------------------------------

    # Check whether the message contains actual
    # suspicious activity before applying safe overrides.

    dangerous_context = any([
        context["credential_request"],
        context["lottery_claim"],
        context["reward_claim"],
        context["electricity_threat"],
        context["parcel_fee_scam_signal"],
        context["remote_access_request"],
        context["job_fee_request"]
    ])

    # Safety warning should not hide an actual
    # credential request or another scam signal.
    if (
        context["safety_warning"]
        and not dangerous_context
        and not suspicious_urls
    ):

        final_score = min(final_score, 20)

        reasons.append(
            "Safety awareness message detected"
        )

    # Genuine service confirmation
    elif (
        context["benign_notice"]
        and not dangerous_context
        and not suspicious_urls
    ):

        final_score = min(final_score, 20)

        reasons.append(
            "Genuine service or transaction confirmation detected"
        )

    else:

        # Direct credential request
        if context["credential_request"]:

            final_score = max(final_score, 75)

            reasons.append(
                "Direct request for confidential banking information"
            )

        # Lottery claim
        if context["lottery_claim"]:

            final_score = max(final_score, 65)

            reasons.append(
                "Lottery win with claim or click request"
            )

        # Reward claim
        elif context["reward_claim"]:

            final_score = max(final_score, 40)

            reasons.append(
                "Reward or cashback claim requires verification"
            )

        # Electricity disconnection pressure
        if context["electricity_threat"]:

            final_score = max(final_score, 40)

            reasons.append(
                "Electricity disconnection threat with payment pressure"
            )

        # Parcel / customs fee pressure
        if context["parcel_fee_scam_signal"]:

            final_score = max(final_score, 40)

            reasons.append(
                "Parcel or customs fee payment request requires verification"
            )

        # Remote access request
        if context["remote_access_request"]:

            final_score = max(final_score, 45)

            reasons.append(
                "Remote access or screen-sharing request linked to payment"
            )

        # Job registration fee
        if context["job_fee_request"]:

            final_score = max(final_score, 40)

            reasons.append(
                "Job offer requiring advance registration or processing fee"
            )

        # Suspicious URL with strong rule score
        if suspicious_urls and rule_score >= 40:

            final_score = max(final_score, 65)

        # Very high ML score
        if ml_score >= 90:

            final_score = max(final_score, 65)

    # Keep score between 0 and 100
    final_score = min(
        max(final_score, 0),
        100
    )

    # -----------------------------------
    # STEP 5: FINAL DECISION
    # -----------------------------------

    if final_score >= 65:

        final_decision = "SCAM"

    elif final_score >= 35:

        final_decision = "NEEDS CAUTION"

    else:

        final_decision = "GENUINE"

    # Risk level
    if final_score <= 30:

        risk_level = "LOW"

    elif final_score <= 60:

        risk_level = "MEDIUM"

    else:

        risk_level = "HIGH"

    # Scam category
    if final_decision != "GENUINE":

        scam_category = detect_scam_category(
            normalized_message,
            suspicious_urls
        )

    else:

        scam_category = "GENUINE / No Scam Category"

    # -----------------------------------
    # STEP 6: RETURN COMPLETE RESULT
    # -----------------------------------

    return {
        "normalized_message": normalized_message,
        "rule_score": rule_score,
        "ml_score": ml_score,
        "ml_prediction": ml_prediction,
        "final_score": final_score,
        "final_decision": final_decision,
        "risk_level": risk_level,
        "scam_category": scam_category,
        "keywords": rule_result["keywords"],
        "urls": rule_result["urls"],
        "suspicious_urls": suspicious_urls,
        "phone_numbers": rule_result["phone_numbers"],
        "reasons": reasons
    }


# ---------------------------------------
# STEP 7: MANUAL TESTING
# ---------------------------------------

if __name__ == "__main__":

    test_messages = [

        "आपका बैंक खाता बंद हो जाएगा, तुरंत OTP भेजें",

        "बिजली कनेक्शन कट जाएगा, अभी बिल भरो",

        "Bijli connection kat jayega, bill bharo",

        "Screen share karo payment receive karne ke liye",

        "अपना OTP किसी के साथ साझा न करें",

        "Apna password kisi ko mat batana",

        "आपका मोबाइल रिचार्ज सफल रहा",

        "Your electricity connection will be disconnected. Pay now",

        "Your parcel is on hold. Pay customs fee using this link",

        "Install this app and share your screen to receive payment",

        "Never share your OTP or PIN with anyone",

        "Tell me your OTP to verify your bank account",

        "Your salary has been credited to your bank account"
    ]

    for message in test_messages:

        result = analyze_combined(message)

        print("\nOriginal Message:", message)

        print(
            "Normalized Message:",
            result["normalized_message"]
        )

        print(
            "Rule Score:",
            result["rule_score"]
        )

        print(
            "AI Scam Score:",
            result["ml_score"]
        )

        print(
            "Final Decision:",
            result["final_decision"]
        )

        print(
            "Risk Score:",
            result["final_score"]
        )

        print(
            "Risk Level:",
            result["risk_level"]
        )

        print(
            "Scam Category:",
            result["scam_category"]
        )

        print(
            "Reasons:",
            result["reasons"]
        )

        print("-----------------------------------")