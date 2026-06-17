"""Routes de gestion du catalogue produits.

Les visiteurs peuvent consulter et rechercher les produits. Les opérations
d'écriture sont protégées par JWT et réservées aux administrateurs.
"""

from flask import Blueprint, g, jsonify, request
from flask_jwt_extended import jwt_required

from app import db
from app.decorators import admin_required, json_required, product_required, validate_payload
from app.models import Product


products_bp = Blueprint("products", __name__, url_prefix="/api/produits")

"""Navigation: Retourne le catalogue, avec filtres optionnels nom et categorie."""
@products_bp.get("")
def list_products():
    query = Product.query
    search = request.args.get("nom")
    categorie = request.args.get("categorie")
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            Product.nom.ilike(pattern) | Product.description.ilike(pattern)
        )
    if categorie:
        query = query.filter(Product.categorie.ilike(categorie))
    return jsonify([product.to_dict() for product in query.order_by(Product.nom).all()])


"""Retourne la fiche détaillée d'un produit chargé à partir de l'id"""
@products_bp.get("/<int:product_id>")
@product_required
def get_product(product_id):
    return jsonify(g.product.to_dict())

"""Crée un produit dans le catalogue, opération réservée aux admins."""
@products_bp.post("")
@jwt_required()
@admin_required
@json_required(["nom", "categorie", "prix"])
@validate_payload(lambda data: validate_product_payload(data, creation=True))
def create_product():
    data = g.json_data
    product = Product(
        nom=data["nom"].strip(),
        description=data.get("description"),
        categorie=data["categorie"].strip(),
        prix=float(data["prix"]),
        quantite_stock=int(data.get("quantite_stock", 0)),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


"""Modifier un produit existant réservé aux admin"""
@products_bp.put("/<int:product_id>")
@jwt_required()
@admin_required
@product_required
@json_required()
@validate_payload(lambda data: validate_product_payload(data, creation=False))
def update_product(product_id):
    product = g.product
    data = g.json_data

    for field in ["nom", "description", "categorie"]:
        if field in data:
            setattr(product, field, data[field])
    if "prix" in data:
        product.prix = float(data["prix"])
    if "quantite_stock" in data:
        product.quantite_stock = int(data["quantite_stock"])

    db.session.commit()
    return jsonify(product.to_dict())


"""Supprimer un produit du catalogue réservé aux admins."""
@products_bp.delete("/<int:product_id>")
@jwt_required()
@admin_required
@product_required
def delete_product(product_id):
    db.session.delete(g.product)
    db.session.commit()
    return "", 204


def validate_product_payload(data, creation):
    """Valide les valeurs métier d'un produit.

    Args:
        data: payload JSON envoyé par le client.
        creation: True si le produit est créé, False s'il est modifié.
    """
    if "prix" in data and float(data["prix"]) < 0:
        return "Le prix doit etre positif"
    stock_value = data.get("quantite_stock", 0 if creation else None)
    if stock_value is not None and int(stock_value) < 0:
        return "Le stock doit etre positif"
    return None
