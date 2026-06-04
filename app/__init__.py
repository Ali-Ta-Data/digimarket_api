"""Initialisation de l'application Flask DigiMarket.

Le module expose la factory create_app(), utilisée à la fois par run.py,
les tests et le script de seed. Cette approche évite les effets de bord au
moment de l'import et facilite la configuration selon l'environnement.
"""

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_object=Config):
    """Construit et configure une instance Flask complète.

    Args:
        config_object: classe ou objet de configuration Flask.

    Returns:
        Une application Flask avec base de données, JWT et blueprints prêts.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Les extensions sont créées au niveau module puis liées à l'application ici.
    db.init_app(app)
    jwt.init_app(app)

    # Les imports de blueprints restent dans la factory pour éviter les imports circulaires.
    from app.auth.routes import auth_bp
    from app.orders.routes import orders_bp
    from app.products.routes import products_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)

    @app.get("/api/health")
    def health():
        """Endpoint simple pour vérifier que l'API répond."""
        return {"status": "ok"}

    @app.errorhandler(404)
    def not_found(error):
        """Réponse JSON uniforme quand une ressource n'existe pas."""
        return jsonify({"message": "Ressource introuvable"}), 404

    @app.errorhandler(400)
    def bad_request(error):
        """Réponse JSON uniforme pour les requêtes invalides."""
        return jsonify({"message": "Requete invalide"}), 400

    return app
