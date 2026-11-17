from flask import Flask
from flask_cors import CORS

from config.settings import settings
from database import close_db, get_db
from middlewares.error_handler import register_error_handlers
from views.routes import register_routes


def create_app():
    application = Flask(__name__)
    application.config["SECRET_KEY"] = settings.SECRET_KEY
    application.config["DEBUG"] = settings.DEBUG
    origins = settings.CORS_ORIGINS
    if origins != "*":
        origins = [item.strip() for item in origins.split(",") if item.strip()]
    CORS(application, resources={r"/*": {"origins": origins}})
    register_error_handlers(application)
    register_routes(application)
    application.teardown_appcontext(close_db)
    return application


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        get_db()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{settings.PORT}")
    print("=" * 50)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
