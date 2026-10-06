# Rapport — Mini-projet Docker

## 1. Image de base

L'image de base retenue pour le service web est :

```dockerfile
FROM python:3.13-slim
```

Le choix de `python:3.13-slim` permet d'utiliser une image officielle Python disposant directement de l'environnement nécessaire à l'exécution de l'application Flask.

La variante `slim` est plus légère que l'image Python complète, car elle contient moins de composants système inutiles pour notre application. Cela permet de réduire la taille finale de l'image Docker tout en conservant une bonne compatibilité avec les dépendances Python du projet.

Une image basée sur Alpine aurait pu être encore plus légère. Cependant, Alpine utilise un environnement système différent et peut nécessiter des configurations supplémentaires ou provoquer des problèmes de compatibilité avec certaines bibliothèques Python.

`python:3.13-slim` représente donc un bon compromis entre :

- la taille de l'image ;
- la simplicité de configuration ;
- la compatibilité avec les dépendances Python ;
- la facilité de maintenance.

---

## 2. Cache Docker

Le Dockerfile du service web est organisé de manière à exploiter efficacement le mécanisme de cache de Docker.

Il utilise l'ordre suivant :

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
```

Le fichier `requirements.txt` est copié avant le fichier `app.py`.

Cette organisation est importante car Docker construit une image sous forme de couches. Lorsqu'une instruction n'a pas changé, Docker peut réutiliser la couche correspondante au lieu de la reconstruire.

Ainsi, si le code de `app.py` est modifié mais que `requirements.txt` reste identique, Docker peut conserver dans son cache la couche contenant l'installation des dépendances Python.

Cela évite d'exécuter de nouveau :

```bash
pip install --no-cache-dir -r requirements.txt
```

à chaque modification du code de l'application.

### Premier build

Lors du premier build, Docker devait construire les différentes couches de l'image et installer les dépendances Python.

Le temps observé était d'environ :

```text
12,49 secondes
```

### Deuxième build

Un deuxième build a ensuite été exécuté sans modification des fichiers.

Docker a alors pu réutiliser les couches déjà présentes dans son cache.

Le temps observé était d'environ :

```text
1,15 seconde
```

Le deuxième build est donc beaucoup plus rapide que le premier.

Ce test montre que le mécanisme de cache Docker permet d'accélérer fortement les constructions successives d'une image en évitant de reconstruire les couches qui n'ont pas été modifiées.

---

## 3. Taille de l'image

La taille de l'image Docker finale du service web a été vérifiée après sa construction.

L'image :

```text
finance-task-manager-web
```

a une taille d'environ :

```text
215 MB
```

Cette taille reste raisonnable pour une application Python contenant Flask ainsi que les bibliothèques nécessaires à la connexion à PostgreSQL.

L'utilisation de l'image de base :

```text
python:3.13-slim
```

permet déjà de limiter la taille de l'image par rapport à une image Python complète.

L'image `slim` contient uniquement un ensemble réduit de composants système, ce qui évite d'embarquer inutilement de nombreux outils qui ne sont pas nécessaires à l'exécution de l'application.

Aucune comparaison avant/après supplémentaire n'a été réalisée dans ce projet, car la version `slim` a été utilisée directement comme image de base.

---

## 4. Persistance des données

La persistance des données PostgreSQL est assurée grâce à un volume Docker nommé :

```text
postgres_data
```

Le volume est associé au service PostgreSQL dans le fichier `compose.yaml`.

L'objectif est de conserver les données de la base même lorsque le conteneur PostgreSQL est supprimé puis recréé.

### Premier test : suppression des conteneurs sans suppression du volume

Pour vérifier la persistance, une table de test appelée :

```text
test_persistence
```

a été créée dans PostgreSQL.

Une donnée de test a ensuite été insérée :

```text
Donnee persistante Docker
```

Les conteneurs ont ensuite été arrêtés et supprimés avec Docker Compose, sans supprimer le volume.

Après avoir recréé les services, une requête `SELECT` sur la table `test_persistence` a permis de retrouver la donnée précédemment enregistrée.

La donnée était donc toujours présente après la recréation des conteneurs.

Cela montre que les données PostgreSQL ne sont pas stockées uniquement dans le système de fichiers du conteneur. Elles sont conservées dans le volume Docker `postgres_data`.

Un arrêt classique avec :

```bash
docker compose down
```

supprime les conteneurs et le réseau associé au projet, mais conserve le volume nommé.

Lorsque les conteneurs sont recréés avec :

```bash
docker compose up -d
```

PostgreSQL retrouve alors les données présentes dans le volume.

### Deuxième test : suppression du volume

Un second test a été réalisé avec la commande :

```bash
docker compose down -v
```

L'option `-v` demande à Docker Compose de supprimer également les volumes associés au projet.

Les services ont ensuite été recréés.

Après le redémarrage, une nouvelle requête sur la table :

```text
test_persistence
```

a retourné une erreur indiquant que la relation n'existait plus :

```text
ERROR: relation "test_persistence" does not exist
```

La table et la donnée de test avaient donc disparu.

Ce deuxième test confirme que les données PostgreSQL étaient bien stockées dans le volume Docker.

En résumé :

- `docker compose down` : les conteneurs sont supprimés mais le volume est conservé, donc les données persistent ;
- `docker compose down -v` : les conteneurs et le volume sont supprimés, donc les données disparaissent.

Le volume Docker permet ainsi de rendre le stockage PostgreSQL indépendant du cycle de vie des conteneurs.

---

## 5. Difficulté rencontrée

Une difficulté rencontrée pendant la réalisation du projet concernait la connexion à PostgreSQL.

Lors d'un premier test, une commande de connexion à PostgreSQL utilisait l'utilisateur :

```text
postgres
```

La commande retournait alors l'erreur suivante :

```text
FATAL: role "postgres" does not exist
```

Pour comprendre l'origine du problème, les variables d'environnement définies dans le fichier `.env` ont été vérifiées.

La configuration du projet utilisait :

```env
POSTGRES_DB=finance_db
POSTGRES_USER=finance_user
DB_HOST=db
```

L'utilisateur PostgreSQL configuré n'était donc pas `postgres`, mais :

```text
finance_user
```

et la base de données utilisée était :

```text
finance_db
```

La commande de connexion a alors été corrigée afin d'utiliser les paramètres correspondant réellement à la configuration du projet.

Après cette correction, la connexion à PostgreSQL a fonctionné correctement.

Cette difficulté a permis de comprendre l'importance de la cohérence entre :

- les variables d'environnement définies dans `.env` ;
- la configuration du fichier `compose.yaml` ;
- les paramètres utilisés par l'application Flask ;
- les commandes exécutées directement dans les conteneurs Docker.

Dans une architecture Docker Compose, les différents services doivent utiliser les mêmes informations de connexion pour pouvoir communiquer correctement.

---

## Conclusion

Ce mini-projet a permis de mettre en pratique les principaux concepts de Docker et Docker Compose à travers la conteneurisation d'une application Flask utilisant PostgreSQL.

L'application repose sur plusieurs services distincts : le service web Flask, la base de données PostgreSQL et l'interface Adminer.

L'utilisation de Docker Compose permet de démarrer et de gérer l'ensemble de ces services de manière centralisée.

Les différents tests réalisés ont notamment permis de vérifier :

- le choix d'une image Python légère avec `python:3.13-slim` ;
- l'intérêt du cache Docker pour accélérer les builds successifs ;
- la taille de l'image finale ;
- la persistance des données PostgreSQL grâce à un volume Docker ;
- la différence entre la suppression des conteneurs et la suppression des conteneurs avec leurs volumes ;
- la communication entre l'application Flask et PostgreSQL à travers les variables d'environnement.

L'application obtenue est fonctionnelle, conteneurisée et reproductible à partir des fichiers présents dans le dépôt Git.