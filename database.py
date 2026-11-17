import sqlite3

DATABASE_NAME = "scam_checker.db"

def create_database():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    # Analysis history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source TEXT,
            message_length INTEGER,
            rule_score INTEGER,
            ml_score REAL,
            final_score INTEGER,
            risk_level TEXT,
            prediction TEXT
        )
    """)

    # User feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id)
                REFERENCES analysis_history(id)
        )
    """)
    
    # User-approved messages for manual review
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS review_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            consented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id)
                REFERENCES analysis_history(id)
        )
    """)

    connection.commit()
    connection.close()

    print("Database created successfully!")
    
def save_analysis(source, message, result):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    prediction = result["final_decision"]

    scam_category = result.get(
        "category",
        "Other / Unclassified"
    )

    cursor.execute("""
        INSERT INTO analysis_history (
            source,
            message_length,
            rule_score,
            ml_score,
            final_score,
            risk_level,
            prediction,
            scam_category
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        source,
        len(message),
        result["rule_score"],
        result["ml_score"],
        result["final_score"],
        result["risk_level"],
        prediction,
        scam_category
    ))

    connection.commit()

    analysis_id = cursor.lastrowid

    connection.close()

    return analysis_id

def save_feedback(analysis_id, feedback):

    if feedback not in ("correct", "incorrect"):
        print("Invalid feedback!")
        return

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO user_feedback (analysis_id, feedback)
        VALUES (?, ?)
    """, (analysis_id, feedback))

    connection.commit()
    connection.close()

    print("Feedback saved successfully!")
    
def view_feedback():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            user_feedback.id,
            user_feedback.analysis_id,
            user_feedback.feedback,
            analysis_history.prediction,
            analysis_history.risk_level,
            analysis_history.final_score,
            user_feedback.created_at

        FROM user_feedback

        JOIN analysis_history
        ON user_feedback.analysis_id = analysis_history.id

        ORDER BY user_feedback.id DESC
    """)

    records = cursor.fetchall()

    connection.close()

    print("\nUSER FEEDBACK REVIEW")
    print("--------------------")

    if not records:
        print("No feedback found.")
        return

    for record in records:
        print(record)
    
def view_history():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, source, message_length,
               final_score, risk_level, prediction
        FROM analysis_history
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    print("\nANALYSIS HISTORY")
    print("----------------")

    for record in records:
        print(record)

    connection.close()


if __name__ == "__main__":
    create_database()
    
def generate_monthly_report():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            strftime('%Y-%m', created_at) AS month,
            COUNT(*) AS total_messages,

            SUM(CASE WHEN prediction = 'SCAM' THEN 1 ELSE 0 END),
            SUM(CASE WHEN prediction = 'NEEDS CAUTION' THEN 1 ELSE 0 END),
            SUM(CASE WHEN prediction = 'GENUINE' THEN 1 ELSE 0 END),

            SUM(CASE WHEN risk_level = 'HIGH' THEN 1 ELSE 0 END),
            SUM(CASE WHEN risk_level = 'MEDIUM' THEN 1 ELSE 0 END),
            SUM(CASE WHEN risk_level = 'LOW' THEN 1 ELSE 0 END)

        FROM analysis_history
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY month DESC
    """)

    reports = cursor.fetchall()

    cursor.execute("""
        SELECT
            strftime('%Y-%m', created_at),
            scam_category,
            COUNT(*)

        FROM analysis_history

        WHERE prediction IN ('SCAM', 'NEEDS CAUTION')
        AND scam_category IS NOT NULL
        AND scam_category != 'GENUINE / No Scam Category'

        GROUP BY strftime('%Y-%m', created_at), scam_category
        ORDER BY strftime('%Y-%m', created_at) DESC
    """)

    category_reports = cursor.fetchall()

    connection.close()

    print("\\nMONTHLY SCAM TREND REPORT")
    print("=========================")

    if not reports:
        print("No analysis records found.")
        return

    for report in reports:

        month, total, scams, caution, genuine, high, medium, low = report

        print(f"\\nMonth: {month}")
        print(f"Total Messages: {total}")
        print(f"Scam Messages: {scams}")
        print(f"Needs Caution: {caution}")
        print(f"Genuine Messages: {genuine}")
        print(f"HIGH Risk: {high}")
        print(f"MEDIUM Risk: {medium}")
        print(f"LOW Risk: {low}")

        if total > 0:
            scam_percentage = (scams / total) * 100
            flagged_percentage = ((scams + caution) / total) * 100

            print(f"Scam Percentage: {scam_percentage:.2f}%")
            print(f"Flagged Percentage: {flagged_percentage:.2f}%")

        print("\\nSCAM / CAUTION CATEGORY BREAKDOWN:")

        month_categories = [
            item for item in category_reports
            if item[0] == month
        ]

        if not month_categories:
            print("No scam category data available.")
        else:
            for category_record in month_categories:
                print(f"{category_record[1]}: {category_record[2]}")
            
def view_incorrect_feedback():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            user_feedback.id,
            user_feedback.analysis_id,
            analysis_history.prediction,
            analysis_history.final_score,
            analysis_history.risk_level,
            user_feedback.created_at

        FROM user_feedback

        JOIN analysis_history
        ON user_feedback.analysis_id = analysis_history.id

        WHERE user_feedback.feedback = 'incorrect'

        ORDER BY user_feedback.id DESC
    """)

    records = cursor.fetchall()
    connection.close()

    print("\nINCORRECT FEEDBACK RECORDS")
    print("--------------------------")

    if not records:
        print("No incorrect feedback found.")
        return

    for record in records:
        print(record)
        
def save_review_submission(analysis_id, message):
    
    from scam_detector import redact_sensitive_info
    message = redact_sensitive_info(message)

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO review_submissions (
            analysis_id,
            message,
            status
        )
        VALUES (?, ?, 'PENDING')
    """, (analysis_id, message))

    connection.commit()
    connection.close()

    print("Review submission saved successfully!")
    
def view_review_submissions():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            analysis_id,
            message,
            status,
            verified_label,
            consented_at
        FROM review_submissions
        ORDER BY id DESC
    """)

    records = cursor.fetchall()
    connection.close()

    print("\nREVIEW SUBMISSIONS")
    print("------------------")

    if not records:
        print("No review submissions found.")
        return

    for record in records:
        print(record)
        
def ensure_review_schema():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(review_submissions)")

    columns = [row[1] for row in cursor.fetchall()]

    if "verified_label" not in columns:

        cursor.execute("""
            ALTER TABLE review_submissions
            ADD COLUMN verified_label TEXT
        """)

    connection.commit()
    connection.close()

    print("Review schema updated successfully!")
    
def mark_review_verified(submission_id, verified_label):

    if verified_label not in ("SCAM", "GENUINE"):
        print("Invalid label! Use SCAM or GENUINE.")
        return

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE review_submissions
        SET status = 'VERIFIED',
            verified_label = ?
        WHERE id = ?
        AND status = 'PENDING'
    """, (verified_label, submission_id))

    connection.commit()

    if cursor.rowcount == 1:
        print("Review verified successfully!")
    else:
        print("Submission not found or already verified.")

    connection.close()
    
def view_verified_submissions():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            analysis_id,
            message,
            verified_label,
            consented_at
        FROM review_submissions
        WHERE status = 'VERIFIED'
        ORDER BY id DESC
    """)

    records = cursor.fetchall()
    connection.close()

    print("\nVERIFIED SUBMISSIONS")
    print("--------------------")

    if not records:
        print("No verified submissions found.")
        return

    for record in records:
        print(record)
        
def export_verified_dataset():

    import pandas as pd

    connection = sqlite3.connect(DATABASE_NAME)

    query = """
        SELECT
            message,
            verified_label AS label
        FROM review_submissions
        WHERE status = 'VERIFIED'
        AND verified_label IN ('SCAM', 'GENUINE')
    """

    df = pd.read_sql_query(query, connection)

    connection.close()

    if df.empty:
        print("No verified data available!")
        return

    df["label"] = df["label"].map({
        "GENUINE": 0,
        "SCAM": 1
    })
    
    df["message"] = df["message"].str.strip()

    df = df.drop_duplicates(
        subset=["message", "label"]
    )

    df.to_csv(
        "dataset/verified_messages.csv",
        index=False
    )

    print("Verified dataset exported successfully!")
    print("\nVERIFIED DATASET SUMMARY")
    print("------------------------")
    print("GENUINE messages:", (df["label"] == 0).sum())
    print("SCAM messages:", (df["label"] == 1).sum())
    print("Total messages:", len(df))
    
def check_verified_dataset():

    import pandas as pd

    df = pd.read_csv("dataset/verified_messages.csv")

    genuine_count = (df["label"] == 0).sum()
    scam_count = (df["label"] == 1).sum()

    print("\nTRAINING READINESS CHECK")
    print("-----------------------")

    print("GENUINE:", genuine_count)
    print("SCAM:", scam_count)

    if genuine_count < 100 or scam_count < 100:

        print("\nNot enough verified messages for training.")
        print("Collect at least 100 messages of each class.")

    else:

        print("\nDataset is ready for further evaluation.")
        
def view_pending_review_submissions():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            analysis_id,
            message,
            status,
            consented_at
        FROM review_submissions
        WHERE status = 'PENDING'
        ORDER BY id DESC
    """)

    records = cursor.fetchall()
    connection.close()

    print("\nPENDING REVIEW SUBMISSIONS")
    print("--------------------------")

    if not records:
        print("No pending submissions found.")
        return

    for record in records:
        print(record)
        
def ensure_analysis_category_schema():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(analysis_history)")

    columns = [row[1] for row in cursor.fetchall()]

    if "scam_category" not in columns:

        cursor.execute("""
            ALTER TABLE analysis_history
            ADD COLUMN scam_category TEXT
        """)

    connection.commit()
    connection.close()

    print("Analysis category schema updated!")