# Rapport — Mini-projet Docker

## 1. Image de base

## 2. Cache Docker
Le premier build de l'image Docker a pris environ 12,49 secondes.

Lors du deuxième build, sans modification des fichiers, Docker a réutilisé les couches déjà présentes dans le cache. Le temps de construction est alors descendu à environ 1,15 seconde.

Cela montre que le mécanisme de cache de Docker permet d'accélérer fortement les builds successifs en évitant de reconstruire les couches qui n'ont pas été modifiées.

## 3. Taille de l'image
L'image Docker finale `finance-task-manager-web` a une taille de 215 MB.

Cette taille reste raisonnable pour une application Python contenant ses dépendances. L'utilisation d'une image Python slim dans le Dockerfile permet de limiter la taille de l'image en évitant d'embarquer des composants système inutiles.

## 4. Persistance des données
La persistance des données PostgreSQL est assurée grâce à un volume Docker nommé `postgres_data`.

Pour vérifier son fonctionnement, une table `test_persistence` a été créée dans PostgreSQL et une donnée de test y a été insérée :

`Donnee persistante Docker`

Les conteneurs ont ensuite été supprimés puis recréés avec Docker Compose.

Après leur recréation, une requête SELECT sur la table `test_persistence` a permis de retrouver la donnée précédemment enregistrée.

Cela confirme que les données PostgreSQL sont conservées indépendamment du cycle de vie des conteneurs grâce au volume Docker.
## 5. Difficulté rencontrée
Lors de la réalisation du projet, une difficulté rencontrée concernait la connexion à PostgreSQL.

Lors du premier test, la commande utilisait l'utilisateur `postgres`, ce qui provoquait l'erreur :

`FATAL: role "postgres" does not exist`

En vérifiant le fichier `.env`, nous avons constaté que l'utilisateur PostgreSQL configuré pour le projet était `finance_user` et que la base de données était `finance_db`.

La commande a donc été corrigée en utilisant les bons paramètres. La connexion à PostgreSQL a ensuite fonctionné correctement.

Cette difficulté a permis de comprendre l'importance de la cohérence entre les variables d'environnement définies dans `.env` et les commandes exécutées dans les conteneurs Docker.