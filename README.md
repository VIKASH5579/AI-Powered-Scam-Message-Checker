AI-Powered Scam Message Checker

An intelligent, privacy-conscious cyber-safety assistant that helps users identify potentially fraudulent messages through a simple Telegram bot.

Problem Statement

People receive fraudulent messages related to fake KYC updates, UPI refunds, lottery winnings, fake job offers, banking alerts, and phishing links. Many users, especially senior citizens, struggle to identify these scams and may unknowingly share sensitive information or lose money.

Solution

The AI-Powered Scam Message Checker analyzes suspicious text messages and screenshots using Machine Learning, keyword detection, regex-based rules, suspicious URL analysis, and OCR.

It generates a risk score and provides understandable safety recommendations.

Features

- AI-powered scam detection using TF-IDF and Logistic Regression.
- Rule-based scam verification.
- Risk scoring from 0–100.
- Low, Medium, and High risk classification.
- Hindi, English, and Hinglish support.
- Suspicious URL detection.
- Indian phone number extraction.
- Screenshot analysis using Tesseract OCR.
- Sensitive information redaction.
- Telegram bot interface.
- Optional user feedback and consent-based manual review.
- Monthly anonymized scam trend reports.
- Senior Citizen Friendly Mode.

Technology Stack

- Python
- python-telegram-bot
- scikit-learn
- TF-IDF
- Logistic Regression
- Regular Expressions
- SQLite
- Pandas
- Tesseract OCR
- Pillow

How It Works

1. User forwards a suspicious message or uploads a screenshot.
2. The system extracts text, URLs, phone numbers, and keywords.
3. Machine Learning and rule-based detection analyze the content.
4. The system calculates a risk score.
5. The Telegram bot displays the result and safety recommendations.
6. Users can optionally provide feedback.
7. Monthly reports summarize scam trends.

Installation

Clone the repository:

git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_PROJECT_FOLDER

Install dependencies:

pip install -r requirements.txt

Install Tesseract OCR and configure its path in the project.

Configuration

Create a ".env" file and add your Telegram bot token:

BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN

Never upload your actual bot token or private credentials to GitHub.

Run the Project

python telegram_bot.py

Privacy and Security

- Original messages are not stored in analysis history.
- Sensitive information is redacted before consent-based review submission.
- User feedback is stored separately.
- Temporary message data is automatically cleared after the configured period.
- Monthly reports use aggregated analysis data.

Limitations

This is an experimental scam detection system. It cannot guarantee that every message is correctly classified. Always independently verify suspicious requests with the official bank, organization, or service provider.

Never share OTPs, passwords, or UPI PINs.

Project Goal

To create an accessible, intelligent, and privacy-conscious cyber-safety assistant that helps everyday users recognize potential online scams and make safer digital decisions.

License

For educational and research purposes.

## 🚀 Live Demo

The AI Scam Message Checker successfully analyzed a suspicious bank KYC message.

### Sample Analysis Result

- Rule Score: 75/100
- AI Scam Score: 93.37%
- AI Prediction: SCAM
- Final Risk Score: 82/100
- Risk Level: HIGH

### Detected Warning Signs

- Suspicious KYC update warning
- Threat of account blocking or suspension
- Urgent or pressure-based language
- Suspicious URL pattern detected

### Safety Recommendation

Never share OTP, UPI PIN, passwords, or sensitive banking information.

*Note: This is an experimental scam detection system.*

### Genuine Message Test

Sample: Bank NEFT transaction confirmation.

- Rule Score: 0/100
- AI Scam Score: 38.91%
- AI Prediction: GENUINE
- Final Risk Score: 16/100
- Risk Level: LOW

Result: Correctly identified as a low-risk genuine-style message.
