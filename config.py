"""
Configuration file for Personal Finance Manager
================================================
Contains database credentials, API keys, and app settings.
Update these values with your actual credentials before deployment.
"""

import os


class Config:
    """Application configuration."""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'finance-manager-secret-key-2024')

    # MySQL Database Configuration
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'finance_manager')

    # Gemini API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

    # Session
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
