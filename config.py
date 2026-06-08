import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:admin123@localhost:5432/taskdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT config
    JWT_SECRET_KEY         = "super-secret-key-change-in-production"
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)