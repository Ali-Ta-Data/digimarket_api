"""Routes de gestion des commandes.

Les clients consultent leurs propres commandes et peuvent en créer. Les admins
peuvent consulter toutes les commandes et modifier leur statut.
"""

from flask import Blueprint, g, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app import db
from app.decorators import admin_required, json_required, order_required, validate_payload
from app.models import Order, OrderItem, Product


orders_bp = Blueprint("orders", __name__, url_prefix="/api/commandes")

ALLOWED_STATUSES = {"en attente", "validee", "expediee", "annulee"}


@orders_bp.get("")
@jwt_required()
def list_orders():
    """Liste les commandes visibles par l'utilisateur courant.

    Un admin voit toutes les commandes; un client ne voit que les siennes.
    """
    claims = get_jwt()
    query = Order.query
    if claims.get("role") != "admin":
        query = query.filter_by(utilisateur_id=int(get_jwt_identity()))
    orders = query.order_by(Order.date_commande.desc()).all()
    return jsonify([order.to_dict() for order in orders])


@orders_bp.get("/<int:order_id>")
@jwt_required()
@order_required(check_owner=True)
def get_order(order_id):
    """Retourne une commande avec ses lignes après contrôle d'accès."""
    return jsonify(g.order.to_dict(include_lignes=True))


@orders_bp.post("")
@jwt_required()
@json_required(["adresse_livraison", "lignes"])
@validate_payload(lambda data: validate_order_payload(data))
def create_order():
    """Crée une commande et décrémente le stock des produits commandés."""
    data = g.json_data
    order = Order(
        utilisateur_id=int(get_jwt_identity()),
        adresse_livraison=data["adresse_livraison"],
    )

    for ligne in data["lignes"]:
        product_id = ligne.get("produit_id")
        quantite = int(ligne.get("quantite", 0))
        product = db.session.get(Product, product_id)
        if not product:
            return jsonify({"message": f"Produit {product_id} introuvable"}), 404
        if (product.quantite_stock or 0) < quantite:
            return jsonify({"message": f"Stock insuffisant pour {product.nom}"}), 409

        # Le stock est décrémenté dans la même transaction que la création de commande.
        product.quantite_stock -= quantite
        order.lignes.append(
            OrderItem(produit=product, quantite=quantite, prix_unitaire=product.prix)
        )

    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict(include_lignes=True)), 201


@orders_bp.patch("/<int:order_id>")
@jwt_required()
@admin_required
@order_required(check_owner=False)
@json_required(["statut"])
def update_order_status(order_id):
    """Modifie le statut d'une commande, uniquement pour les admins."""
    order = g.order
    data = g.json_data
    statut = data.get("statut")
    if statut not in ALLOWED_STATUSES:
        return jsonify({"message": "Statut invalide", "statuts": sorted(ALLOWED_STATUSES)}), 400
    order.statut = statut
    db.session.commit()
    return jsonify(order.to_dict(include_lignes=True))


@orders_bp.get("/<int:order_id>/lignes")
@jwt_required()
@order_required(check_owner=True)
def get_order_lines(order_id):
    """Retourne uniquement les lignes d'une commande accessible."""
    return jsonify([ligne.to_dict() for ligne in g.order.lignes])


def validate_order_payload(data):
    """Vérifie qu'une commande contient des lignes valides."""
    lignes = data.get("lignes")
    if not isinstance(lignes, list) or not lignes:
        return "La commande doit contenir au moins une ligne"
    for ligne in lignes:
        if not ligne.get("produit_id"):
            return "Chaque ligne doit contenir un produit_id"
        if int(ligne.get("quantite", 0)) <= 0:
            return "La quantite doit etre superieure a 0"
    return None
