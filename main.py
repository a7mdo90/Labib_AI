#!/usr/bin/env python3
"""
Labib Telegram Bot - Main Entry Point
=====================================

This is the main entry point that imports and runs the bot from the organized structure.

Author: Labib AI Team
Date: September 18, 2025
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main bot
if __name__ == "__main__":
    from labib_bot import main
    main()
