AI Scam Message Checker – System Architecture

flowchart TD
    A[User Input] --> B{Input Type}
    B -->|Text Message| C[Text Processing]
    B -->|Screenshot| D[Tesseract OCR]
    D --> C

    C --> E[Hindi Language Normalization]

    E --> F[Rule Based Detector]
    E --> G[Machine Learning Model]

    F --> H[Combined Risk Scoring]
    G --> H

    H --> I[Final Risk Score 0-100]
    I --> J[Risk Classification]

    J --> K[LOW Risk]
    J --> L[MEDIUM Risk]
    J --> M[HIGH Risk]

    J --> N[Telegram Bot Result]
    N --> O[SQLite Database]
    O --> P[Analysis History and Feedback]

System Components

1. User Input: Accepts text messages and screenshots.
2. OCR: Extracts text from screenshots using Tesseract.
3. Language Normalization: Converts supported Hindi words into English equivalents.
4. Rule-Based Detector: Checks suspicious keywords and URLs.
5. Machine Learning Model: Uses TF-IDF and Logistic Regression.
6. Combined Risk Scoring: Combines rule-based and ML scores.
7. Risk Classification: Classifies messages into LOW, MEDIUM, or HIGH.
8. SQLite Database: Stores analysis history and feedback.