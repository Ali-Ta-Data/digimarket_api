"""Point d'entrée de développement.

Ce fichier permet de lancer l'API avec: python run.py
En production, on préférera exposer app:create_app() à un serveur WSGI.
"""

from app import create_app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
