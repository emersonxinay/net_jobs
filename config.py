import os


class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:emerson123@localhost/red_jobs'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
