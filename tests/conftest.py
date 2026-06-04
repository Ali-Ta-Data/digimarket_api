import pytest

from app import create_app, db
from app.models import Product, User


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret-key-with-at-least-32-bytes"


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        admin = User(email="admin@test.fr", nom="Admin", role="admin")
        admin.set_password("Admin123!")
        client = User(email="client@test.fr", nom="Client", role="client")
        client.set_password("Client123!")
        product = Product(
            nom="Souris ergonomique",
            description="Souris sans fil",
            categorie="Peripheriques",
            prix=49.90,
            quantite_stock=5,
        )
        db.session.add_all([admin, client, product])
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, email, password):
    response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    return response.get_json()["access_token"]


@pytest.fixture()
def admin_token(client):
    return login(client, "admin@test.fr", "Admin123!")


@pytest.fixture()
def client_token(client):
    return login(client, "client@test.fr", "Client123!")
