"""Script d'initialisation de la base de données de démonstration.

À lancer avec: python -m app.seed
Il recrée les tables puis ajoute un admin, un client et quelques produits.
"""

from app import create_app, db
from app.models import Product, User


def create_user(email, password, nom, role):
    """Crée un utilisateur avec mot de passe hashé et l'ajoute à la session."""
    user = User(email=email, nom=nom, role=role)
    user.set_password(password)
    db.session.add(user)
    return user


def seed():
    """Réinitialise la base SQLite et insère les données de test."""
    app = create_app()
    with app.app_context():
        # drop_all est acceptable ici car ce script sert uniquement au seed local.
        db.drop_all()
        db.create_all()

        create_user("admin@digimarket.fr", "Admin123!", "Administrateur DigiMarket", "admin")
        create_user("client@digimarket.fr", "Client123!", "Client Demo", "client")

        products = [
            Product(
                nom="Ordinateur portable Pro 14",
                description="Portable performant pour bureautique avancee et creation.",
                categorie="Ordinateurs",
                prix=1299.90,
                quantite_stock=8,
            ),
            Product(
                nom="Ecran 27 pouces QHD",
                description="Ecran haute resolution avec dalle IPS.",
                categorie="Ecrans",
                prix=329.90,
                quantite_stock=15,
            ),
            Product(
                nom="Clavier mecanique RGB",
                description="Clavier filaire avec switches tactiles.",
                categorie="Peripheriques",
                prix=89.90,
                quantite_stock=30,
            ),
        ]
        db.session.add_all(products)
        db.session.commit()


if __name__ == "__main__":
    seed()
    print("Base digimarket.db initialisee avec donnees de test.")
