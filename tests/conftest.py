"""Configuration pytest pour les tests fonctionnels.

Les tests utilisent une base SQLite en mémoire afin de rester isolés et rapides.
Chaque test reçoit une application fraîche avec un admin, un client et un produit.
"""

import pytest

from app import create_app, db
from app.models import Product, User


TEST_DESCRIPTIONS = {}


def pytest_collection_modifyitems(config, items):
    """Mémorise la description de chaque test au moment où pytest les collecte."""
    for item in items:
        docstring = getattr(item.function, "__doc__", None)
        TEST_DESCRIPTIONS[item.nodeid] = docstring.strip() if docstring else item.nodeid


def pytest_runtest_logreport(report):
    """Affiche une description lisible quand un test est réussi.

    Pytest affiche par défaut un point par test avec l'option -q. Ce hook ajoute
    une ligne explicite basée sur la docstring du test, ce qui rend le résultat
    plus compréhensible pour une personne qui découvre la suite de tests.
    """
    if report.when != "call" or not report.passed:
        return

    description = TEST_DESCRIPTIONS.get(report.nodeid, report.nodeid)
    print(f"PASS - {description}")


class TestConfig:
    """Configuration dédiée aux tests."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret-key-with-at-least-32-bytes"


@pytest.fixture()
def app():
    """Crée une application Flask de test et initialise les données minimales."""
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        admin = User(email="admin@test.fr", nom="Admin", role="admin")
        admin.set_password("Admin123!")
        client = User(email="client@test.fr", nom="Client", role="client")
        client.set_password("Client123!")

        client2 = User(email="client2@test.fr", nom="Client2", role="client2")
        client2.set_password("ClientABC!")
        
        product = Product(
            nom="Souris ergonomique",
            description="Souris sans fil",
            categorie="Peripheriques",
            prix=49.90,
            quantite_stock=5,
        )
        db.session.add_all([admin, client,client2, product])
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Retourne le client HTTP Flask utilisé pour appeler les routes."""
    return app.test_client()


def login(client, email, password):
    """Connecte un utilisateur de test et retourne son token JWT."""
    response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    return response.get_json()["access_token"]


@pytest.fixture()
def admin_token(client):
    """Token JWT d'un administrateur de test."""
    return login(client, "admin@test.fr", "Admin123!")


@pytest.fixture()
def client_token(client):
    """Token JWT d'un client de test."""
    return login(client, "client@test.fr", "Client123!")

@pytest.fixture()
def client_token2(client):
    """Token JWT d'un client de test."""
    return login(client, "client2@test.fr", "ClientABC!")