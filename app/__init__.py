from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    jwt.init_app(app)

    from app.auth.routes import auth_bp
    from app.orders.routes import orders_bp
    from app.products.routes import products_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"message": "Ressource introuvable"}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"message": "Requete invalide"}), 400

    return app
