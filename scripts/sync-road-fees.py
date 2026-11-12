"""Compatibility entry point: synchronize all current reviewed source assets."""
import runpy
runpy.run_path('scripts/sync-data-assets.py',run_name='__main__')
