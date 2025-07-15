import pandas as pd
from sqlalchemy import create_engine, text

# Load CSV with low_memory fix
df = pd.read_csv("data/processed/statsbomb_all_events.csv", low_memory=False)

# Save to SQLite
engine = create_engine("sqlite:///data/soccer.db")
df.to_sql("events", engine, if_exists="replace", index=False)
print("Saved to database: data/soccer.db (table: events)")

# Verify record count
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM events"))
    count = result.scalar()
    print("Total rows in 'events' table:", count)
