#!/usr/bin/env python
"""
Script to run Celery beat scheduler for SIGNAL platform.

Usage:
    python scripts/run_celery_beat.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.tasks.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start()