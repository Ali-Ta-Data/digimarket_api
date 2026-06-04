from app import create_app, db
from app.models import Product, User


def create_user(email, password, nom, role):
    user = User(email=email, nom=nom, role=role)
    user.set_password(password)
    db.session.add(user)
    return user


def seed():
    app = create_app()
    with app.app_context():
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
