#!/usr/bin/env python3
"""
Labib Bot Deployment Script - Main Entry Point
==============================================

This is the main deployment entry point that imports and runs the deployment from the organized structure.

Author: Labib AI Team
Date: September 18, 2025
"""

import sys
import os
from pathlib import Path

# Add deployment directory to Python path
deployment_path = Path(__file__).parent / "deployment"
sys.path.insert(0, str(deployment_path))

# Import and run the deployment
if __name__ == "__main__":
    from deploy import main
    main()
