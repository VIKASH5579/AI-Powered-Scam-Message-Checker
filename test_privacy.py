from scam_detector import redact_sensitive_info

tests = [
    "OTP: 123456",
    "Mobile: 9876543210",
    "Mobile: +91 98765 43210",
    "Email: vikash@gmail.com",
    "UPI: vikash123@paytm",
    "OTP: 123456 Mobile: 98765-43210 Email: test@gmail.com UPI: user@oksbi"
]

for message in tests:
    print(redact_sensitive_info(message))