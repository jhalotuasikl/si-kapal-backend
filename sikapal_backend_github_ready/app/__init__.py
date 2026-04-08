from flask import Flask
from .config import Config
from .extensions import db, jwt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    from .routes import register_routes
    register_routes(app)

    # Auto migrate ringan: tambahkan kolom yang mungkin belum ada
    with app.app_context():
        try:
            from .utils.auto_migrate import ensure_schema
            ensure_schema(db)
        except Exception:
            pass

    return app
