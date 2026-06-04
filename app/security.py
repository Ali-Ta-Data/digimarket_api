from flask_jwt_extended import get_jwt, get_jwt_identity

from app import db
from app.models import User


def current_user():
    user_id = get_jwt_identity()
    return db.session.get(User, int(user_id))


def can_access_order(order):
    claims = get_jwt()
    return claims.get("role") == "admin" or order.utilisateur_id == int(get_jwt_identity())
