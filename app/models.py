from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from app import db


def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="client")
    date_creation = db.Column(db.DateTime, nullable=False, default=utc_now)

    commandes = db.relationship("Order", back_populates="utilisateur")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "nom": self.nom,
            "role": self.role,
            "date_creation": self.date_creation.isoformat(),
        }


class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    categorie = db.Column(db.String(50), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    quantite_stock = db.Column(db.Integer, default=0)
    date_creation = db.Column(db.DateTime, nullable=False, default=utc_now)

    lignes = db.relationship("OrderItem", back_populates="produit")

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "description": self.description,
            "categorie": self.categorie,
            "prix": self.prix,
            "quantite_stock": self.quantite_stock,
            "disponible": (self.quantite_stock or 0) > 0,
            "date_creation": self.date_creation.isoformat(),
        }


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date_commande = db.Column(db.DateTime, default=utc_now)
    adresse_livraison = db.Column(db.String(200), nullable=False)
    statut = db.Column(db.String(20), default="en attente")

    utilisateur = db.relationship("User", back_populates="commandes")
    lignes = db.relationship(
        "OrderItem", back_populates="commande", cascade="all, delete-orphan"
    )

    def to_dict(self, include_lignes=False):
        data = {
            "id": self.id,
            "utilisateur_id": self.utilisateur_id,
            "date_commande": self.date_commande.isoformat(),
            "adresse_livraison": self.adresse_livraison,
            "statut": self.statut,
            "total": round(sum(l.total for l in self.lignes), 2),
        }
        if include_lignes:
            data["lignes"] = [ligne.to_dict() for ligne in self.lignes]
        return data


class OrderItem(db.Model):
    __tablename__ = "order_item"

    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)

    commande = db.relationship("Order", back_populates="lignes")
    produit = db.relationship("Product", back_populates="lignes")

    @property
    def total(self):
        return self.quantite * self.prix_unitaire

    def to_dict(self):
        return {
            "id": self.id,
            "commande_id": self.commande_id,
            "produit_id": self.produit_id,
            "produit": self.produit.nom if self.produit else None,
            "quantite": self.quantite,
            "prix_unitaire": self.prix_unitaire,
            "total": round(self.total, 2),
        }
