# Finance Task Manager

Application web de gestion de tâches financières développée avec Flask et PostgreSQL et conteneurisée avec Docker Compose.

## Prérequis

- Docker Engine 24.0 ou supérieur
- Docker Compose v2.20 ou supérieur
- Sous Windows : Docker Desktop récent intégrant Docker Compose v2

Vérification des versions :

docker --version
docker compose version

## Démarrage

1. Copier le fichier d'exemple des variables d'environnement :

cp .env.example .env

Sous Windows PowerShell :

Copy-Item .env.example .env

2. Construire et démarrer les conteneurs :

docker compose up --build -d

3. Vérifier leur état :

docker compose ps

## Accès à l'application

Application Flask :
http://localhost:5000

Health check :
http://localhost:5000/health

Adminer :
http://localhost:8080

## Variables d'environnement

Les variables sont définies dans le fichier `.env`.

- `POSTGRES_DB` : nom de la base PostgreSQL
- `POSTGRES_USER` : utilisateur PostgreSQL
- `POSTGRES_PASSWORD` : mot de passe PostgreSQL
- `DB_HOST` : nom du service PostgreSQL utilisé par l'application

Le fichier `.env` n'est pas versionné. Le fichier `.env.example` fournit les valeurs d'exemple nécessaires.

## Commandes utiles

Afficher les conteneurs :

docker compose ps

Afficher les logs :

docker compose logs -f

Ouvrir un shell dans le conteneur web :

docker compose exec web sh

Arrêter l'application :

docker compose down

Arrêter l'application et supprimer les volumes :

docker compose down -v