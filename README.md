# digimarket_api

API REST Flask pour la boutique e-commerce DigiMarket, préparée pour un environnement Linux.

Cette version reprend le projet initial et factorise les contrôles récurrents avec des décorateurs:

- `@admin_required` pour les routes réservées aux administrateurs.
- `@json_required(...)` pour centraliser la lecture et la vérification du JSON.
- `@validate_payload(...)` pour appliquer les validateurs métier.
- `@product_required` et `@order_required(...)` pour charger les ressources et contrôler les accès.

## Installation Linux

```bash
cd digimarket_api
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

## Initialisation de la base

```bash
source .venv/bin/activate
python -m app.seed
```

Le script crée `digimarket.db` avec des données de test.

Comptes de test:

- Admin: `admin@digimarket.fr` / `Admin123!`
- Client: `client@digimarket.fr` / `Client123!`

## Lancement

```bash
source .venv/bin/activate
python run.py
```

L'API démarre sur `http://127.0.0.1:5000`.

## Tests préparés

Les tests sont fournis dans le dossier `tests/`, mais ils n'ont pas été exécutés pour cette version comme demandé.

Pour les lancer plus tard:

```bash
source .venv/bin/activate
python -m pytest
```

Ou avec le script Linux:

```bash
bash scripts/test.sh
```

## Endpoints

### Authentification

- `POST /api/auth/register`
- `POST /api/auth/login`

### Produits

- `GET /api/produits`
- `GET /api/produits/<id>`
- `POST /api/produits` admin uniquement
- `PUT /api/produits/<id>` admin uniquement
- `DELETE /api/produits/<id>` admin uniquement

### Commandes

- `GET /api/commandes`
- `GET /api/commandes/<id>`
- `POST /api/commandes`
- `PATCH /api/commandes/<id>` admin uniquement
- `GET /api/commandes/<id>/lignes`

## Exemple curl

```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@digimarket.fr","password":"Admin123!"}'
```
