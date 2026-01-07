"""Asset manager for handling asset paths in both dev and PyInstaller bundle environments."""
import os
import sys


def get_asset_path(asset_name):
    """
    Get the correct path for an asset, handling both development and PyInstaller bundle modes.
    
    Args:
        asset_name: Name or relative path of the asset (e.g., "Circle-Ninja.png" or just the filename)
    
    Returns:
        Full path to the asset file
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        asset_dir = os.path.join(sys._MEIPASS, 'assets')
    else:
        # Running in development
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets')
    
    return os.path.join(asset_dir, asset_name)
