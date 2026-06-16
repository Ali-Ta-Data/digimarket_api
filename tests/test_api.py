"""Tests fonctionnels des principaux parcours API.

Ces tests couvrent l'authentification, les droits admin/client, la création
de commande et la mise à jour du stock. Ils servent de filet de sécurité pour
les fonctionnalités demandées dans le cahier des charges.
"""

from app import db
from app.models import Product


def auth_header(token):
    """Construit l'en-tête Authorization attendu par les routes protégées."""
    return {"Authorization": f"Bearer {token}"}


def test_register_creates_client(client):
    """Une inscription standard crée toujours un utilisateur client."""
    response = client.post(
        "/api/auth/register",
        json={"email": "new@test.fr", "password": "Password123!", "nom": "Nouveau"},
    )

    assert response.status_code == 201
    assert response.get_json()["user"]["role"] == "client"


def test_admin_can_create_product(client, admin_token):
    """Un administrateur peut ajouter un produit au catalogue."""
    response = client.post(
        "/api/produits",
        json={
            "nom": "Station de travail",
            "description": "PC puissant",
            "categorie": "Ordinateurs",
            "prix": 1899.0,
            "quantite_stock": 3,
        },
        headers=auth_header(admin_token),
    )

    assert response.status_code == 201
    assert response.get_json()["nom"] == "Station de travail"


def test_client_cannot_create_product(client, client_token):
    """Un client authentifié ne peut pas créer de produit."""
    response = client.post(
        "/api/produits",
        json={"nom": "Produit interdit", "categorie": "Test", "prix": 1},
        headers=auth_header(client_token),
    )

    assert response.status_code == 403


def test_create_order_decrements_stock(app, client, client_token):
    """Créer une commande décrémente le stock et calcule le total."""
    
    with app.app_context():
        product = db.session.get(Product, 1)
    response = client.post(
        "/api/commandes",
        json={
            "adresse_livraison": "10 rue de Paris, 75001 Paris",
            "lignes": [{"produit_id": 1, "quantite": 2}],
        },
        headers=auth_header(client_token),
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["total"] == 99.8

    with app.app_context():
        product = db.session.get(Product, 1)
        assert product.quantite_stock == 3


def test_client_only_sees_own_orders(client, client_token,client_token2, admin_token):
    """Un client voit ses commandes tandis qu'un admin voit toutes les commandes."""
    client.post(
        "/api/commandes",
        json={
            "adresse_livraison": "10 rue de Paris, 75001 Paris",
            "lignes": [{"produit_id": 1, "quantite": 1}],
        },
        headers=auth_header(client_token),
    )

    response = client.post(
        "/api/commandes",
        json={
            "adresse_livraison": "10 rue de Strasbourg, 67000 Strasbourg",
            "lignes": [{"produit_id": 1, "quantite": 1}],
        },
        headers=auth_header(client_token2),
    )

    client_orders = client.get("/api/commandes", headers=auth_header(client_token))
    client_orders2 = client.get("/api/commandes", headers=auth_header(client_token2))
    admin_orders = client.get("/api/commandes", headers=auth_header(admin_token))

    assert client_orders.status_code == 200
    """Le 1er client voit sa commande"""
    assert len(client_orders.get_json()) == 1
    """Le 2eme client voit sa commande"""
    assert len(client_orders2.get_json()) == 1
    """L'administrateur voit les 2 commandes"""
    assert len(admin_orders.get_json()) == 2


def test_admin_updates_order_status(client, client_token, admin_token):
    """Un administrateur peut faire évoluer le statut d'une commande."""
    created = client.post(
        "/api/commandes",
        json={
            "adresse_livraison": "10 rue de Paris, 75001 Paris",
            "lignes": [{"produit_id": 1, "quantite": 1}],
        },
        headers=auth_header(client_token),
    ).get_json()

    response = client.patch(
        f"/api/commandes/{created['id']}",
        json={"statut": "expediee"},
        headers=auth_header(admin_token),
    )

    assert response.status_code == 200
    assert response.get_json()["statut"] == "expediee"
