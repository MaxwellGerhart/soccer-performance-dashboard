#!/usr/bin/env python3
"""
Cleanup script to remove old World Cup/StatsBomb files from NCAA soccer dashboard
"""

import os
import shutil
from pathlib import Path

def cleanup_old_files():
    """Remove old World Cup/StatsBomb files while preserving NCAA files"""
    
    # Files to remove (root directory)
    files_to_remove = [
        'app.py',                    # Original World Cup Flask app
        'player_traits.py',          # StatsBomb trait calculations
        'generate_radar_charts.py',  # Old radar chart generator
    ]
    
    # Templates to remove
    templates_to_remove = [
        'templates/base.html',
        'templates/index.html',
        'templates/players.html',
        'templates/teams.html',
        'templates/traits.html', 
        'templates/events.html',
        'templates/player_profile.html',
    ]
    
    # Scripts directory to remove entirely
    scripts_dir = 'scripts'
    
    # Old database files to remove
    old_data_files = [
        'data/soccer.db',
        'data/processed/statsbomb_all_events.csv',
    ]
    
    # StatsBomb data directory
    statsbomb_dir = 'data/statsbomb'
    
    # Temp scripts that can be removed (keeping ncaaMatchPredictor.ipynb)
    temp_scripts_to_remove = [
        'temp_scripts/analyze_data.py',
        'temp_scripts/better_defensive_metrics.py',
        'temp_scripts/check_data.py',
        'temp_scripts/check_events.py', 
        'temp_scripts/check_lineups.py',
        'temp_scripts/check_matches.py',
        'temp_scripts/save_traits.py',
        'temp_scripts/test_radar.py',
        'temp_scripts/generate_radar_charts.py',
    ]
    
    removed_files = []
    errors = []
    
    print("🧹 Cleaning up old World Cup/StatsBomb files...")
    print("=" * 60)
    
    # Remove individual files
    for file_path in files_to_remove + templates_to_remove + old_data_files + temp_scripts_to_remove:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                removed_files.append(file_path)
                print(f"✅ Removed: {file_path}")
            else:
                print(f"⚠️  Not found: {file_path}")
        except Exception as e:
            errors.append(f"❌ Error removing {file_path}: {e}")
            print(f"❌ Error removing {file_path}: {e}")
    
    # Remove entire directories
    directories_to_remove = [scripts_dir, statsbomb_dir]
    
    for dir_path in directories_to_remove:
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                removed_files.append(f"{dir_path}/ (entire directory)")
                print(f"✅ Removed directory: {dir_path}/")
            else:
                print(f"⚠️  Directory not found: {dir_path}/")
        except Exception as e:
            errors.append(f"❌ Error removing directory {dir_path}: {e}")
            print(f"❌ Error removing directory {dir_path}: {e}")
    
    # Remove __pycache__ files for removed modules
    try:
        pycache_files = [
            '__pycache__/player_traits.cpython-313.pyc',
        ]
        for cache_file in pycache_files:
            if os.path.exists(cache_file):
                os.remove(cache_file)
                removed_files.append(cache_file)
                print(f"✅ Removed cache: {cache_file}")
    except Exception as e:
        errors.append(f"❌ Error removing cache files: {e}")
        print(f"❌ Error removing cache files: {e}")
    
    print("=" * 60)
    print(f"🎉 Cleanup complete!")
    print(f"📁 Removed {len(removed_files)} files/directories")
    
    if errors:
        print(f"⚠️  {len(errors)} errors occurred:")
        for error in errors:
            print(f"   {error}")
    
    print("\n✅ NCAA Soccer Dashboard files preserved:")
    preserved_files = [
        "ncaa_app.py",
        "player_ratings.py", 
        "templates/ncaa_*.html",
        "data/ncaa_soccer.db",
        "data/d1_player_stats.csv",
        "data/ncaa_mens_scores_2024.csv",
        "static/radars/",
        "Logos_png/",
        "requirements.txt",
        "README.md"
    ]
    for file in preserved_files:
        print(f"   ✅ {file}")
    
    return len(removed_files), len(errors)

if __name__ == "__main__":
    removed_count, error_count = cleanup_old_files()
    print(f"\n🏁 Final result: {removed_count} items removed, {error_count} errors")
