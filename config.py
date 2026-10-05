import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "civicconnect-local-secret-key"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:Akanksha%40123@127.0.0.1:3306/civicconnect"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "static",
        "uploads"
    )