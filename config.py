class Config:
    SECRET_KEY = "civicconnect-secret-key"

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Akanksha%40123@127.0.0.1:3306/civicconnect"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    UPLOAD_FOLDER = "static/uploads"