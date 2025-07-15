import json
import pandas as pd
from pathlib import Path

def get_match_ids(competition_id, season_id):
    match_file = Path("data/statsbomb/data/matches") / f"{competition_id}/{season_id}.json"
    with open(match_file, "r", encoding="utf-8") as f:
        matches = json.load(f)

    match_ids = [match['match_id'] for match in matches]
    return match_ids


def load_all_events(match_ids):
    all_events = []

    for match_id in match_ids:
        event_path = Path(f"data/statsbomb/data/events/{match_id}.json")
        if event_path.exists():
            with open(event_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                df = pd.json_normalize(data, sep='_')
                all_events.append(df)

    if all_events:
        return pd.concat(all_events, ignore_index=True)
    else:
        return pd.DataFrame()  # fallback in case no files found


if __name__ == "__main__":
    comp_id = 9  
    season_id = 281

    match_ids = get_match_ids(comp_id, season_id)
    print(f"Found {len(match_ids)} matches")

    df_all = load_all_events(match_ids)
    print(df_all.head())
    print(f"\nTotal events loaded: {len(df_all)}")

    df_all.to_csv("data/processed/statsbomb_all_events.csv", index=False)
    print("All events saved to data/processed/statsbomb_all_events.csv")


