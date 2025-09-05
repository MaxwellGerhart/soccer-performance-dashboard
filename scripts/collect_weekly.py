"""
CLI entry to run weekly data collection. Intended for Render Cron Jobs.
"""
import os
import sys
from datetime import datetime

# Ensure project root is on path when run from Render cron working dir
CUR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(CUR, '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from weekly_data_manager import SeasonDataManager


def main():
    season = sys.argv[1] if len(sys.argv) > 1 else os.getenv('SEASON', '2025')

    mgr = SeasonDataManager()

    # Optionally allow forcing the season active via env
    if os.getenv('FORCE_ACTIVATE_SEASON', 'false').lower() in ('1', 'true', 'yes'):
        try:
            mgr.activate_season(season)
        except Exception as e:
            print(f"Warning: could not activate season {season}: {e}")

    ok = mgr.run_weekly_collection(season)
    if not ok:
        print("Weekly collection reported failure or inactive season")
        sys.exit(1)

    print(f"Done weekly collection for {season} at {datetime.utcnow().isoformat()}Z")


if __name__ == '__main__':
    main()
