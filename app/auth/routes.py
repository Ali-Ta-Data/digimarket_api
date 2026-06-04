"""Routes d'authentification.

Ce blueprint gère l'inscription, la connexion et la génération du token JWT.
Les routes s'appuient sur json_required pour valider les champs attendus.
"""

from flask import Blueprint, g, jsonify
from flask_jwt_extended import create_access_token

from app import db
from app.decorators import json_required
from app.models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
@json_required(["email", "password", "nom"])
def register():
    """Crée un utilisateur client et retourne ses informations publiques.

    Par sécurité, seul le premier utilisateur peut demander le rôle admin via
    l'API d'inscription. Les inscriptions suivantes sont forcées en client.
    """
    data = g.json_data
    if len(data["password"]) < 8:
        return jsonify({"message": "Le mot de passe doit contenir au moins 8 caracteres"}), 400

    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Cette adresse email existe deja"}), 409

    requested_role = data.get("role", "client")
    # Cette règle permet de créer un premier admin sans laisser l'inscription ouverte aux admins.
    role = "admin" if requested_role == "admin" and User.query.count() == 0 else "client"

    user = User(email=email, nom=data["nom"].strip(), role=role)
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Utilisateur cree", "user": user.to_dict()}), 201


@auth_bp.post("/login")
@json_required(["email", "password"])
def login():
    """Authentifie un utilisateur et retourne un access token JWT."""
    data = g.json_data
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Identifiants invalides"}), 401

    # Les claims ajoutés au JWT servent aux décorateurs d'autorisation.
    token = create_access_token(
        identity=str(user.id), additional_claims={"role": user.role, "email": user.email}
    )
    return jsonify({"access_token": token, "user": user.to_dict()})
