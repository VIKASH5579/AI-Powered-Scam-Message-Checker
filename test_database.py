from database import (
    create_database,
    save_analysis,
    save_feedback,
    view_history
)
create_database()

test_result = {
    "rule_score": 85,
    "ml_score": 92.5,
    "final_score": 90,
    "risk_level": "HIGH",
    "ml_prediction": 1
}

analysis_id = save_analysis(
    "text",
    "Share your OTP to claim reward",
    test_result
)

print("Analysis ID:", analysis_id)

save_feedback(analysis_id, "SCAM")

print("Database test completed!")

view_history()