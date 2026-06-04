"""Aides liées à l'utilisateur authentifié.

Ce module conserve quelques fonctions simples autour du JWT courant. Les
décorateurs plus complets sont définis dans app.decorators.
"""

from flask_jwt_extended import get_jwt, get_jwt_identity

from app import db
from app.models import User


def current_user():
    """Retourne l'objet User correspondant à l'identité du JWT courant."""
    user_id = get_jwt_identity()
    return db.session.get(User, int(user_id))


def can_access_order(order):
    """Vérifie si l'utilisateur courant est admin ou propriétaire de la commande."""
    claims = get_jwt()
    return claims.get("role") == "admin" or order.utilisateur_id == int(get_jwt_identity())
