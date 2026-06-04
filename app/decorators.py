"""Décorateurs réutilisables pour les routes Flask.

Ces décorateurs factorisent les contrôles transverses: autorisation admin,
lecture du JSON, validation métier et chargement des ressources. Les routes
restent ainsi courtes et centrées sur leur action principale.
"""

from functools import wraps

from flask import g, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from app import db
from app.models import Order, Product


def admin_required(fn):
    """Autorise uniquement les utilisateurs dont le JWT contient role=admin."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if get_jwt().get("role") != "admin":
            return jsonify({"message": "Acces reserve aux administrateurs"}), 403
        return fn(*args, **kwargs)

    return wrapper


def json_required(required_fields=None):
    """Lit le corps JSON et vérifie la présence des champs obligatoires.

    Les données validées sont stockées dans flask.g.json_data pour éviter de
    relire request.get_json() dans chaque route.
    """
    required_fields = required_fields or []

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True) or {}
            missing = [field for field in required_fields if data.get(field) in (None, "")]
            if missing:
                return jsonify({"message": "Champs requis manquants", "champs": missing}), 400
            g.json_data = data
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def validate_payload(validator):
    """Applique une fonction de validation métier au JSON courant.

    Le validator doit retourner None si tout va bien, ou un message d'erreur.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            error = validator(g.json_data)
            if error:
                return jsonify({"message": error}), 400
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def product_required(fn):
    """Charge le produit demandé et le place dans flask.g.product."""
    @wraps(fn)
    def wrapper(product_id, *args, **kwargs):
        g.product = db.get_or_404(Product, product_id)
        return fn(product_id, *args, **kwargs)

    return wrapper


def order_required(check_owner=True):
    """Charge une commande et contrôle son accès si check_owner vaut True."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(order_id, *args, **kwargs):
            order = db.get_or_404(Order, order_id)
            if check_owner and not user_can_access_order(order):
                return jsonify({"message": "Acces interdit"}), 403
            g.order = order
            return fn(order_id, *args, **kwargs)

        return wrapper

    return decorator


def user_can_access_order(order):
    """Détermine si l'utilisateur courant peut consulter la commande."""
    claims = get_jwt()
    return claims.get("role") == "admin" or order.utilisateur_id == int(get_jwt_identity())
