from database import (
    create_database,
    ensure_review_schema,
    ensure_analysis_category_schema
)

create_database()

ensure_review_schema()

ensure_analysis_category_schema()