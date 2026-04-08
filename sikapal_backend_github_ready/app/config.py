from datetime import timedelta

class Config:
    SECRET_KEY = "si-kapal-secret"

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://sikapal_user:SikapalApp123!@localhost/si_kapal"
        "?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = "jwt-si-kapal"

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)