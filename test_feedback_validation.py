from database import save_feedback

print("Testing valid feedback:")

save_feedback(14, "correct")
save_feedback(14, "incorrect")

print("\nTesting invalid feedback:")

save_feedback(14, "SCAM")