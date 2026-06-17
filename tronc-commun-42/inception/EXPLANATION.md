# Inception — Explication complète pour la soutenance

> Ce fichier est dans `.gitignore` — il ne sera pas versionné.
> Il explique **tout** ce qui a été fait, pourquoi, et comment ça fonctionne.
> Lis-le comme si tu n'avais jamais touché à Docker.

---

## Table des matières

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
2. [Les concepts fondamentaux](#2-les-concepts-fondamentaux)
   - Docker vs VM
   - Image vs Conteneur
   - Dockerfile
   - docker-compose
   - Réseau Docker
   - Volumes Docker
   - Secrets Docker
3. [Architecture de notre infrastructure](#3-architecture-de-notre-infrastructure)
4. [Le Makefile](#4-le-makefile)
5. [Le fichier srcs/.env](#5-le-fichier-srcsenv)
6. [Les secrets](#6-les-secrets)
7. [Le docker-compose.yml — ligne par ligne](#7-le-docker-composeyml--ligne-par-ligne)
8. [MariaDB — expliqué de A à Z](#8-mariadb--expliqué-de-a-à-z)
9. [WordPress + php-fpm — expliqué de A à Z](#9-wordpress--php-fpm--expliqué-de-a-à-z)
10. [Nginx — expliqué de A à Z](#10-nginx--expliqué-de-a-à-z)
11. [Le flux complet : de `make` à `curl`](#11-le-flux-complet--de-make-à-curl)
12. [Questions fréquentes en soutenance](#12-questions-fréquentes-en-soutenance)

---

## 1. Vue d'ensemble du projet

Le projet Inception consiste à monter une **petite infrastructure web** composée de trois services :

```
Internet / navigateur
        │
        ▼ port 443 (HTTPS)
   ┌─────────┐
   │  nginx  │  ← seul point d'entrée, gère le TLS
   └────┬────┘
        │ FastCGI (port 9000 interne)
        ▼
   ┌─────────────┐
   │  wordpress  │  ← WordPress + php-fpm (génère le HTML)
   └──────┬──────┘
          │ TCP 3306 (interne)
          ▼
   ┌──────────┐
   │  mariadb │  ← base de données MySQL
   └──────────┘
```

Chaque service tourne dans son **propre conteneur Docker**, construit à partir d'un **Dockerfile écrit à la main**, basé sur `debian:bookworm`.

---

## 2. Les concepts fondamentaux

### Docker vs Machine Virtuelle (VM)

Une **VM** (VirtualBox, VMware) émule un ordinateur complet : elle a son propre noyau (kernel) d'OS, ses propres pilotes matériels, son propre disque virtuel. Démarrer une VM prend 30 secondes à 2 minutes, et elle consomme beaucoup de RAM et de disque.

Un **conteneur Docker** ne virtualise PAS le matériel. Il partage le noyau du système hôte, mais isole les processus dans leur propre environnement (fichiers, réseau, utilisateurs). Un conteneur démarre en millisecondes et n'embarque que ce dont il a besoin (les binaires et libs de l'application).

```
┌─────────────────────────────────────────┐
│              Machine Hôte               │
│   Noyau Linux partagé par tout le monde │
│  ┌───────────┐  ┌───────────┐  ┌──────┐│
│  │ conteneur │  │ conteneur │  │ ...  ││
│  │  mariadb  │  │  nginx    │  │      ││
│  └───────────┘  └───────────┘  └──────┘│
└─────────────────────────────────────────┘
```

### Image vs Conteneur

- Une **image** Docker est un template en lecture seule : c'est comme une recette de cuisine figée. Elle contient le système de fichiers de base (l'OS Debian), les paquets installés, les fichiers de config, etc.
- Un **conteneur** est une instance d'une image en cours d'exécution. C'est la recette qui a été "cuisinée" et tourne. Tu peux lancer 10 conteneurs à partir de la même image.

```
Image "mariadb"  →  Conteneur "mariadb" (en cours d'exécution)
                 →  Conteneur "mariadb2" (une autre instance)
                 →  ...
```

Dans notre projet, on construit 3 images (une par service) et on lance 1 conteneur par image.

### Dockerfile

Un `Dockerfile` est le fichier de recette pour construire une image. Il contient des instructions exécutées ligne par ligne. Chaque instruction crée une **couche (layer)** de l'image.

Les instructions clés :

| Instruction | Rôle |
|-------------|------|
| `FROM image:tag` | Image de départ (notre base = `debian:bookworm`) |
| `RUN commande` | Exécute une commande pendant le build (install de paquets, etc.) |
| `COPY src dest` | Copie un fichier depuis ton PC dans l'image |
| `EXPOSE port` | Documente le port que l'app utilise (n'ouvre PAS le port sur l'hôte) |
| `ENTRYPOINT ["cmd"]` | Commande lancée au démarrage du conteneur (forme exec = PID 1) |
| `CMD ["cmd"]` | Commande par défaut (même rôle, légèrement différent) |

**Pourquoi `debian:bookworm` ?** Le sujet interdit de partir d'une image déjà toute faite (pas de `FROM wordpress`, pas de `FROM mysql`). On part de la base Debian et on installe tout à la main. `bookworm` est le nom de code de Debian 12 (l'avant-dernière stable). On n'utilise jamais `latest` car ce tag change sans prévenir.

### docker-compose

`docker-compose` (ou `docker compose` v2) est un outil qui permet de définir et gérer plusieurs conteneurs en même temps dans un seul fichier YAML (`docker-compose.yml`). Sans lui, il faudrait lancer chaque `docker run ...` à la main avec des dizaines d'options.

Avec compose, un simple `docker compose up -d --build` :
1. Construit les 3 images
2. Crée le réseau
3. Crée les volumes
4. Lance les 3 conteneurs dans le bon ordre

### Réseau Docker

Par défaut, les conteneurs sont isolés du réseau. Pour qu'ils se parlent, on crée un **réseau virtuel interne**.

Dans notre projet, le réseau s'appelle `inception` et utilise le driver `bridge` (pont réseau). Sur ce réseau, chaque conteneur est accessible par son **nom de service** : le conteneur `wordpress` peut joindre `mariadb` simplement en faisant `mysql -h mariadb`.

Ce qui est **interdit** par le sujet :
- `network: host` → le conteneur utilise directement le réseau de l'hôte, pas d'isolation
- `--link` / `links:` → ancienne méthode dépréciée de Docker

### Volumes Docker

Un **volume** permet de persister des données entre les redémarrages de conteneurs. Sans volume, quand un conteneur s'arrête, toutes ses données disparaissent.

Il existe deux types :
- **Bind mount classique** (`./data:/var/lib/mysql`) : mappe directement un dossier de l'hôte. Simple mais interdit par le sujet.
- **Volume nommé** (`mariadb:/var/lib/mysql`) : géré par Docker, plus portable.

**Le sujet impose les deux à la fois** : utiliser des volumes nommés (gérés par Docker), mais dont les données sont physiquement stockées dans `/home/omischle/data`. On fait ça avec `driver: local` et `driver_opts` :

```yaml
volumes:
  mariadb:
    driver: local
    driver_opts:
      type: none    # pas de système de fichiers spécial
      o: bind       # c'est un bind mount
      device: /home/omischle/data/db  # vers ce dossier hôte
```

Résultat : Docker voit un "vrai" volume nommé (listable avec `docker volume ls`), mais les données sont bien dans `/home/omischle/data/db`.

### Secrets Docker

Un **secret Docker** est un mécanisme pour passer des mots de passe aux conteneurs sans qu'ils apparaissent :
- dans les Dockerfiles
- dans les variables d'environnement (visibles avec `docker inspect`)
- dans le `docker-compose.yml`

Les secrets sont des fichiers texte (un mot de passe par fichier) stockés dans `secrets/` sur l'hôte. Docker les monte en lecture seule dans le conteneur à `/run/secrets/<nom>`. L'entrypoint les lit avec `cat /run/secrets/mon_secret`.

---

## 3. Architecture de notre infrastructure

### Arborescence complète

```
Desktop/                          ← racine du projet
├── Makefile                      ← commandes de build/lancement
├── README.md                     ← doc publique (versionnable)
├── USER_DOC.md                   ← doc utilisateur
├── DEV_DOC.md                    ← doc développeur
├── EXPLANATION.md                ← ce fichier (gitignored)
├── .gitignore                    ← ignore secrets/ et EXPLANATION.md
├── secrets/                      ← mots de passe (gitignored)
│   ├── db_root_password.txt      ← mot de passe root MariaDB
│   ├── db_password.txt           ← mot de passe user WordPress (wpuser)
│   └── credentials.txt           ← ligne 1 = mdp admin WP, ligne 2 = mdp author WP
└── srcs/
    ├── .env                      ← variables non-sensibles
    ├── docker-compose.yml        ← définition des 3 services
    └── requirements/
        ├── mariadb/
        │   ├── Dockerfile        ← recette de l'image MariaDB
        │   ├── conf/my.cnf       ← config MariaDB
        │   └── tools/entrypoint.sh  ← script de démarrage
        ├── nginx/
        │   ├── Dockerfile        ← recette de l'image Nginx
        │   └── conf/nginx.conf   ← config Nginx (HTTPS, TLS, proxy)
        └── wordpress/
            ├── Dockerfile        ← recette de l'image WordPress
            ├── conf/www.conf     ← config php-fpm
            └── tools/entrypoint.sh  ← script de démarrage + install WP
```

### Ordre de démarrage

1. **mariadb** démarre en premier (les autres en dépendent)
2. **wordpress** attend que MariaDB soit prêt (TCP check sur le port 3306), puis installe WordPress
3. **nginx** démarre et peut immédiatement servir des requêtes (la vol est partagée avec wordpress)

---

## 4. Le Makefile

Le Makefile est à la racine du projet. Il est lancé avec `make` depuis le dossier `Desktop/`.

```makefile
COMPOSE_FILE = srcs/docker-compose.yml
DATA_DIR     = /home/omischle/data
```
Ces deux variables sont définies une seule fois et réutilisées partout.

```makefile
all: up
```
`make` sans argument appelle `make up`.

```makefile
up:
    mkdir -p $(DATA_DIR)/db $(DATA_DIR)/wp
    docker compose -f $(COMPOSE_FILE) up -d --build
```
- `mkdir -p` : crée les dossiers de données si ils n'existent pas (nécessaire pour les volumes bind-mount)
- `up -d` : démarre en arrière-plan (detached)
- `--build` : reconstruit les images si les Dockerfiles ont changé

```makefile
build:
    mkdir -p $(DATA_DIR)/db $(DATA_DIR)/wp
    docker compose -f $(COMPOSE_FILE) build
```
Construit les images sans les démarrer.

```makefile
down:
    docker compose -f $(COMPOSE_FILE) down
```
Arrête et supprime les conteneurs + le réseau. Les volumes et données sont **conservés**.

```makefile
stop:
    docker compose -f $(COMPOSE_FILE) stop
```
Arrête les conteneurs sans les supprimer (on peut les relancer avec `start`).

```makefile
start:
    docker compose -f $(COMPOSE_FILE) start
```
Relance des conteneurs préalablement arrêtés avec `stop`.

```makefile
re: clean up
```
`make re` appelle d'abord `clean` (supprime conteneurs + volumes), puis `up` (reconstruit et redémarre). Les données hôte sont conservées, les volumes Docker sont recrées.

```makefile
clean:
    docker compose -f $(COMPOSE_FILE) down -v --remove-orphans
```
- `-v` : supprime aussi les volumes nommés (mais pas les données hôte dans `/home/omischle/data`)
- `--remove-orphans` : supprime les conteneurs qui ne sont plus dans le compose file

```makefile
fclean:
    docker compose -f $(COMPOSE_FILE) down -v --remove-orphans
    docker system prune -af
    sudo rm -rf $(DATA_DIR)
```
- `docker system prune -af` : supprime TOUT ce qui n'est plus utilisé (images, cache de build, réseaux)
- `sudo rm -rf $(DATA_DIR)` : supprime les données physiques sur l'hôte (`/home/omischle/data`)
- Après `fclean`, le prochain `make` repart de zéro (télécharge tout, réinstalle WordPress, etc.)

```makefile
logs:
    docker compose -f $(COMPOSE_FILE) logs -f
```
Affiche les logs de tous les conteneurs en temps réel (`-f` = follow).

```makefile
ps:
    docker compose -f $(COMPOSE_FILE) ps
```
Affiche l'état des conteneurs (Up/Down, ports, etc.).

```makefile
.PHONY: all up build down stop start re clean fclean logs ps
```
`.PHONY` dit à make que ces cibles ne sont pas des fichiers. Sans ça, si un fichier nommé `up` existait, make croirait que la cible est à jour et ne ferait rien.

---

## 5. Le fichier srcs/.env

```env
DOMAIN_NAME=omischle.42.fr

MYSQL_DATABASE=wordpress
MYSQL_USER=wpuser
WORDPRESS_DB_HOST=mariadb:3306

WP_TITLE=Inception
WP_ADMIN_USER=supervisor
WP_ADMIN_EMAIL=supervisor@omischle.42.fr
WP_USER=author42
WP_USER_EMAIL=author42@omischle.42.fr
```

Ce fichier contient des **variables d'environnement non-sensibles**. Elles seront injectées dans les conteneurs via `env_file: .env` dans docker-compose.yml. Les conteneurs peuvent y accéder comme des variables shell normales (`$DOMAIN_NAME`, `$MYSQL_USER`, etc.).

**Ce qu'il ne contient PAS** : aucun mot de passe. Ceux-ci sont dans `secrets/`.

Le fichier peut être versionné (commité dans git) sans risque.

---

## 6. Les secrets

### Pourquoi les secrets ?

Si tu mets un mot de passe dans une variable d'environnement, il est visible via `docker inspect <conteneur>`. Si tu le mets dans le Dockerfile, il est gravé dans l'image (lisible avec `docker history`). Les secrets Docker évitent ces problèmes.

### Les 3 fichiers de secrets

```
secrets/db_root_password.txt   → RootPass42!
secrets/db_password.txt        → WpDbPass42!
secrets/credentials.txt        → SuperAdmin42!\nAuthorPass42!
```

- **db_root_password** : le mot de passe du compte `root` de MariaDB (accès total à tous les DBs)
- **db_password** : le mot de passe du compte `wpuser` de MariaDB (accès uniquement à la DB `wordpress`)
- **credentials** : 
  - ligne 1 = mot de passe de l'administrateur WordPress (`supervisor`)
  - ligne 2 = mot de passe du 2e utilisateur WordPress (`author42`)

### Comment Docker les monte

Dans `docker-compose.yml` :
```yaml
secrets:
  db_root_password:
    file: ../secrets/db_root_password.txt
```

Dans un service :
```yaml
  mariadb:
    secrets:
      - db_root_password
      - db_password
```

Docker monte chaque secret en lecture seule dans le conteneur :
- `/run/secrets/db_root_password` → contient `RootPass42!`
- `/run/secrets/db_password` → contient `WpDbPass42!`

Dans l'entrypoint, on les lit avec :
```bash
DB_ROOT_PASSWORD=$(cat /run/secrets/db_root_password)
```
La substitution de commande `$(...)` supprime automatiquement le retour à la ligne final.

---

## 7. Le docker-compose.yml — ligne par ligne

```yaml
services:
```
Définit les services (= les conteneurs).

### Service mariadb

```yaml
  mariadb:
    build:
      context: requirements/mariadb
```
Construit l'image depuis le dossier `srcs/requirements/mariadb` (qui contient le Dockerfile). Le `context` est relatif à l'emplacement du compose file.

```yaml
    image: mariadb
```
Nomme l'image construite "mariadb". Obligatoire par le sujet : le nom de l'image = le nom du service.

```yaml
    container_name: mariadb
```
Fixe le nom du conteneur. Sans ça, compose génère un nom comme `srcs-mariadb-1`.

```yaml
    restart: always
```
Si le conteneur plante, Docker le redémarre automatiquement. Obligatoire par le sujet.

```yaml
    env_file: .env
```
Injecte toutes les variables du fichier `.env` dans le conteneur.

```yaml
    secrets:
      - db_root_password
      - db_password
```
Monte ces deux secrets dans `/run/secrets/` du conteneur.

```yaml
    volumes:
      - mariadb:/var/lib/mysql
```
Monte le volume nommé `mariadb` sur `/var/lib/mysql` (là où MariaDB stocke ses données).

```yaml
    networks:
      - inception
```
Connecte ce conteneur au réseau `inception`.

```yaml
    expose:
      - "3306"
```
**Documentation interne** : indique que ce conteneur écoute sur le port 3306. Ce port n'est PAS accessible depuis l'hôte, uniquement depuis les autres conteneurs du même réseau.

### Service wordpress

```yaml
    depends_on:
      - mariadb
```
Indique que le conteneur wordpress ne démarre qu'après le conteneur mariadb. Note : `depends_on` attend juste que le conteneur soit "started", pas que MariaDB soit vraiment prêt. C'est pourquoi l'entrypoint de WordPress fait un vrai check TCP.

### Service nginx

```yaml
    volumes:
      - wordpress:/var/www/html
```
Nginx monte le **même volume** que WordPress. Pourquoi ? Nginx a besoin d'accéder aux fichiers PHP pour les servir (même si l'exécution PHP est déléguée à php-fpm). Nginx lit les fichiers statiques directement depuis ce volume.

```yaml
    ports:
      - "443:443"
```
**Seul port publié vers l'hôte**. `443:443` signifie : le port 443 de l'hôte redirige vers le port 443 du conteneur nginx. Attention : `expose` ≠ `ports`. `expose` = interne au réseau Docker. `ports` = accessible depuis l'hôte (et l'extérieur).

### Section volumes

```yaml
volumes:
  mariadb:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /home/omischle/data/db
  wordpress:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /home/omischle/data/wp
```

- `driver: local` : utilise le driver local de Docker (standard)
- `type: none` : pas de système de fichiers spécial à monter
- `o: bind` : c'est un bind mount (monte un dossier hôte existant)
- `device:` : le chemin hôte où les données sont stockées physiquement

Résultat : Docker manage un volume nommé (`docker volume ls` le montre), mais les fichiers sont dans `/home/omischle/data/`.

### Section networks

```yaml
networks:
  inception:
    driver: bridge
```

Crée un réseau virtuel de type `bridge`. Sur ce réseau, les conteneurs se voient par leur nom de service. `mariadb`, `wordpress`, `nginx` sont résolubles comme des noms d'hôte.

### Section secrets (globale)

```yaml
secrets:
  db_root_password:
    file: ../secrets/db_root_password.txt
```

`../secrets/` est relatif à `srcs/`, donc ça pointe vers `Desktop/secrets/`. Docker lit le fichier et le monte dans les conteneurs qui le demandent.

---

## 8. MariaDB — expliqué de A à Z

### Dockerfile

```dockerfile
FROM debian:bookworm
```
On part de Debian 12. Pas de `FROM mysql` ni `FROM mariadb` officielle — interdit par le sujet.

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    mariadb-server \
    && rm -rf /var/lib/apt/lists/*
```
- `apt-get update` : met à jour la liste des paquets disponibles
- `apt-get install -y` : installe sans confirmation interactive
- `--no-install-recommends` : n'installe pas les paquets "recommandés" (économise de l'espace)
- `mariadb-server` : installe MariaDB (MySQL-compatible)
- `rm -rf /var/lib/apt/lists/*` : supprime le cache apt pour réduire la taille de l'image

**Subtilité importante** : quand `mariadb-server` est installé via apt, le script post-installation de Debian tourne `mysql_install_db` automatiquement. Cela initialise déjà les bases système de MariaDB dans `/var/lib/mysql`. C'est pour ça qu'on ne peut PAS détecter le "premier démarrage" avec `if [ ! -d /var/lib/mysql/mysql ]` — ce répertoire existe déjà dans l'image !

```dockerfile
COPY conf/my.cnf /etc/mysql/mariadb.conf.d/99-inception.cnf
```
Copie notre config MariaDB dans le dossier de config. Les fichiers dans `mariadb.conf.d/` sont lus dans l'ordre alphabétique (99 = lu en dernier = priorité maximale).

```dockerfile
COPY tools/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
```
Copie le script de démarrage et le rend exécutable.

```dockerfile
EXPOSE 3306
```
Documentation : MariaDB écoute sur le port 3306.

```dockerfile
ENTRYPOINT ["entrypoint.sh"]
```
Quand le conteneur démarre, il exécute `entrypoint.sh`. La forme **exec** `["cmd"]` (avec crochets) fait que `entrypoint.sh` devient **directement le processus 1 (PID 1)**. C'est crucial.

**Pourquoi PID 1 est important ?** Le PID 1 est le processus "parent de tout" sous Linux. Il reçoit les signaux d'arrêt (SIGTERM) du système. Si le PID 1 est un shell bash qui lance mysqld en arrière-plan, bash reçoit SIGTERM, se termine, et mysqld est tué brutalement. En utilisant `exec mysqld` dans l'entrypoint, on remplace le processus bash par mysqld : mysqld DEVIENT le PID 1 et reçoit correctement les signaux d'arrêt, ce qui lui permet de se fermer proprement.

### my.cnf — la config MariaDB

```ini
[mysqld]
bind-address            = 0.0.0.0
```
MariaDB écoute sur **toutes les interfaces réseau**, pas juste `localhost`. Sans ça, les autres conteneurs du réseau Docker ne pourraient pas se connecter.

```ini
datadir                 = /var/lib/mysql
socket                  = /run/mysqld/mysqld.sock
user                    = mysql
```
Configurations standard : où stocker les données, où mettre le socket Unix (pour les connexions locales), sous quel utilisateur tourner.

```ini
skip-name-resolve
```
Ne fait pas de résolution DNS inverse sur les connexions entrantes. Accélère les connexions et évite des problèmes dans les environnements sans DNS configuré.

### entrypoint.sh — le script de démarrage

```bash
#!/bin/bash
set -e
```
- `#!/bin/bash` : utilise bash (et non sh) pour interpréter ce script
- `set -e` : si **n'importe quelle commande** échoue (exit code non-zéro), le script s'arrête immédiatement. Filet de sécurité.

```bash
DB_ROOT_PASSWORD=$(cat /run/secrets/db_root_password)
DB_PASSWORD=$(cat /run/secrets/db_password)
```
Lit les mots de passe depuis les fichiers secrets. La substitution `$(...)` supprime le `\n` final.

```bash
mkdir -p /run/mysqld
chown mysql:mysql /run/mysqld
```
Crée le dossier pour le socket Unix de MariaDB et lui donne les bonnes permissions (l'utilisateur `mysql` doit pouvoir y écrire).

```bash
if [ ! -f "/var/lib/mysql/.initialized" ]; then
```
**Détection du premier démarrage via un fichier sentinel.** On ne peut pas tester `[ ! -d /var/lib/mysql/mysql ]` car ce répertoire est créé lors du build de l'image (par l'installation apt). On crée donc notre propre marqueur `.initialized`.

```bash
    mysqld --user=mysql --skip-networking --socket=/run/mysqld/mysqld.sock &
    MYSQLD_PID=$!
```
Lance mysqld **en arrière-plan** (`&`) juste pour l'initialisation :
- `--user=mysql` : mysqld tourne sous l'utilisateur `mysql` (pas root)
- `--skip-networking` : n'ouvre PAS le port TCP 3306 (sécurité pendant l'init)
- `--socket=...` : utilise un socket Unix pour la communication locale
- `$!` : capture le PID du processus lancé en arrière-plan

```bash
    until mysqladmin --socket=/run/mysqld/mysqld.sock ping --silent 2>/dev/null; do
        sleep 1
    done
```
Boucle jusqu'à ce que MariaDB soit vraiment prêt à répondre. `mysqladmin ping` retourne 0 quand le serveur est opérationnel.

```bash
    mysql --socket=/run/mysqld/mysqld.sock -uroot -e "
        FLUSH PRIVILEGES;
        ALTER USER 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PASSWORD}';
        CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\`;
        CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${DB_PASSWORD}';
        GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'%';
        FLUSH PRIVILEGES;
    "
```
Exécute du SQL directement. Détail de chaque requête :
- `FLUSH PRIVILEGES` : recharge la table des permissions
- `ALTER USER 'root'@'localhost' IDENTIFIED BY '...'` : définit le mot de passe root
- `CREATE DATABASE IF NOT EXISTS \`wordpress\`` : crée la base de données
- `CREATE USER IF NOT EXISTS 'wpuser'@'%'` : crée l'utilisateur avec `%` = depuis n'importe quelle IP
- `GRANT ALL PRIVILEGES ON wordpress.*` : donne tous les droits sur la DB `wordpress` à `wpuser`
- `FLUSH PRIVILEGES` : applique les changements

```bash
    touch /var/lib/mysql/.initialized
```
Crée le fichier sentinel. La prochaine fois que le conteneur démarre, cette condition sera fausse et l'init sera sautée.

```bash
    kill "${MYSQLD_PID}"
    wait "${MYSQLD_PID}" 2>/dev/null || true
```
Arrête proprement l'instance temporaire de mysqld.

```bash
exec mysqld --user=mysql
```
**La ligne clé.** `exec` remplace le processus bash actuel par `mysqld`. Bash disparaît, mysqld devient le **PID 1** du conteneur. Il tourne en premier plan (foreground) indéfiniment, ce qui maintient le conteneur en vie.

---

## 9. WordPress + php-fpm — expliqué de A à Z

### Qu'est-ce que php-fpm ?

**php-fpm** = PHP FastCGI Process Manager. C'est un gestionnaire de processus PHP qui tourne en arrière-plan et attend des requêtes.

Sans php-fpm, nginx devrait appeler PHP pour chaque requête individuellement (lent). Avec php-fpm, des processus PHP sont pré-chargés et attendent, prêts à exécuter du code immédiatement.

Le protocole de communication entre nginx et php-fpm s'appelle **FastCGI**. Nginx reçoit une requête HTTP pour un fichier `.php`, la transmet à php-fpm via FastCGI, php-fpm l'exécute et renvoie le HTML à nginx, qui le renvoie au navigateur.

```
Navigateur → HTTPS → Nginx → FastCGI → php-fpm → exécute PHP → HTML → Nginx → Navigateur
```

### Dockerfile

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    php8.2-fpm \
    php8.2-mysql \
    ...
```
- `ca-certificates` : certificats d'autorité racine pour que `curl` puisse faire des HTTPS (sinon `curl: error 77`)
- `php8.2-fpm` : le gestionnaire de processus PHP
- `php8.2-mysql` : extension PHP pour parler à MySQL/MariaDB
- `php8.2-curl`, `gd`, `mbstring`, `xml`, `zip` : extensions requises par WordPress

```dockerfile
RUN curl -o /usr/local/bin/wp https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
    && chmod +x /usr/local/bin/wp
```
Télécharge **wp-cli** (WordPress Command Line Interface). C'est un outil en ligne de commande pour gérer WordPress sans navigateur : installer, configurer, créer des utilisateurs, etc. On l'utilise dans l'entrypoint pour tout installer.

```dockerfile
RUN mkdir -p /var/www/html && chown -R www-data:www-data /var/www/html
RUN mkdir -p /run/php
```
- `/var/www/html` : là où WordPress sera installé. L'utilisateur `www-data` (celui qui exécute php-fpm) doit en être propriétaire.
- `/run/php` : dossier pour le socket php-fpm (pas utilisé ici car on utilise TCP, mais certaines versions le demandent).

### www.conf — la config php-fpm

```ini
[www]
user = www-data
group = www-data
```
php-fpm tourne sous l'utilisateur `www-data` (utilisateur web standard sur Debian).

```ini
listen = 0.0.0.0:9000
```
php-fpm écoute en **TCP** sur le port 9000, sur toutes les interfaces. Le sujet impose explicitement TCP (pas de socket Unix). Nginx peut ainsi joindre php-fpm en réseau Docker avec `fastcgi_pass wordpress:9000`.

```ini
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
```
Gestion des processus PHP ("process manager") en mode dynamique : démarre avec 2 workers, peut monter jusqu'à 5, garde au minimum 1 en attente. Suffisant pour une petite infrastructure.

```ini
clear_env = no
```
**Important** : par défaut php-fpm efface toutes les variables d'environnement avant d'exécuter PHP. Avec `clear_env = no`, les variables de notre `.env` (MYSQL_USER, etc.) restent accessibles dans PHP. WordPress en a besoin.

### entrypoint.sh

```bash
DB_HOST=$(echo "${WORDPRESS_DB_HOST}" | cut -d: -f1)
DB_PORT=$(echo "${WORDPRESS_DB_HOST}" | cut -d: -f2)
```
`WORDPRESS_DB_HOST=mariadb:3306`. On découpe sur `:` pour extraire :
- `DB_HOST=mariadb`
- `DB_PORT=3306`

```bash
until bash -c ">/dev/tcp/${DB_HOST}/${DB_PORT}" 2>/dev/null; do
    echo "Waiting for MariaDB on ${DB_HOST}:${DB_PORT}..."
    sleep 2
done
```
**Vérification TCP pure** sans outil externe. `>/dev/tcp/mariadb/3306` est une fonctionnalité bash spéciale : bash essaie d'ouvrir une connexion TCP à `mariadb:3306`. Si MariaDB n'est pas encore prêt, ça échoue avec exit code 1 → on attend 2 secondes et on réessaie. Dès que MariaDB accepte des connexions, la boucle se termine.

```bash
if [ ! -f "${WP_PATH}/wp-config.php" ]; then
    wp core download --path="${WP_PATH}" --allow-root
    wp config create --path=... --dbname=... --dbuser=... --dbpass=... --dbhost=... --allow-root
fi
```
- Si `wp-config.php` n'existe pas, on télécharge WordPress et on génère la config.
- `wp core download` : télécharge WordPress depuis wordpress.org et décompresse dans `/var/www/html`
- `wp config create` : génère le fichier `wp-config.php` avec les paramètres de BDD
- `--allow-root` : autorise wp-cli à tourner en tant que root (inhabituel pour un serveur web, mais normal dans un conteneur Docker)

```bash
if ! wp core is-installed --path="${WP_PATH}" --allow-root 2>/dev/null; then
    wp core install --url=... --title=... --admin_user=... --admin_password=... --admin_email=... --allow-root
    wp user create "${WP_USER}" "${WP_USER_EMAIL}" --role=author --user_pass=... --allow-root
    chown -R www-data:www-data "${WP_PATH}"
fi
```
- `wp core is-installed` : vérifie si les tables WordPress existent dans la BDD. Retourne 0 si oui, 1 si non.
- `! ...` : on execute le bloc SI WordPress N'est PAS installé.
- `wp core install` : crée toutes les tables WordPress dans MariaDB et configure le site.
  - `--admin_user=supervisor` : login de l'admin (pas admin/Admin/administrator → règle du sujet)
- `wp user create "${WP_USER}" "${WP_USER_EMAIL}"` : crée le 2e utilisateur avec le rôle `author`.
- `chown -R www-data:www-data` : donne la propriété de tous les fichiers WordPress à `www-data` pour que php-fpm puisse les lire/écrire.

```bash
exec php-fpm8.2 -F
```
Lance php-fpm en **foreground** (`-F`). `exec` fait de php-fpm le **PID 1** du conteneur.

---

## 10. Nginx — expliqué de A à Z

### Rôle de Nginx dans ce projet

Nginx est le **seul point d'entrée** vers l'infrastructure. Il reçoit toutes les connexions HTTPS sur le port 443 et les distribue :
- Fichiers statiques (images, CSS, JS) → servis directement depuis le volume
- Fichiers PHP → transmis à php-fpm via FastCGI

### Dockerfile

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    openssl \
    && rm -rf /var/lib/apt/lists/*
```
Installe nginx et openssl (pour générer le certificat TLS).

```dockerfile
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/inception.key \
    -out /etc/ssl/certs/inception.crt \
    -subj "/C=FR/ST=IDF/L=Paris/O=42/OU=inception/CN=omischle.42.fr"
```
Génère un **certificat TLS auto-signé** pendant le build de l'image :
- `-x509` : génère directement un certificat (pas une demande de signature)
- `-nodes` : pas de passphrase sur la clé privée (nginx ne peut pas la taper interactivement)
- `-days 365` : valide 1 an
- `-newkey rsa:2048` : génère une nouvelle clé RSA 2048 bits
- `-keyout` : où sauvegarder la clé privée
- `-out` : où sauvegarder le certificat
- `-subj` : informations du certificat (Country, State, Locality, Organization, CN=Common Name = le domaine)

Le certificat est "auto-signé" = il n'est pas signé par une autorité reconnue (Let's Encrypt, etc.). Le navigateur affichera un avertissement de sécurité. `curl -k` (insecure) permet d'ignorer cet avertissement.

```dockerfile
COPY conf/nginx.conf /etc/nginx/sites-available/default
```
Remplace la config nginx par défaut par la nôtre.

```dockerfile
CMD ["nginx", "-g", "daemon off;"]
```
- `CMD` (pas `ENTRYPOINT`) : on utilise la forme exec pour que nginx soit PID 1.
- `daemon off;` : par défaut, nginx se détache en arrière-plan (daemon). Dans un conteneur, le processus principal doit rester au premier plan pour que le conteneur reste en vie. Cette option force nginx à rester au premier plan.

**Différence entre ENTRYPOINT et CMD :**
- `ENTRYPOINT` : toujours exécuté, ne peut pas être remplacé facilement
- `CMD` : commande par défaut, peut être remplacée par `docker run image autre_commande`
- Dans notre cas, `CMD ["nginx", "-g", "daemon off;"]` est équivalent à `ENTRYPOINT` pour notre usage.

### nginx.conf

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
```
Écoute sur le port 443 en HTTPS, en IPv4 ET en IPv6 (`[::]`).

```nginx
    server_name omischle.42.fr;
```
Ce bloc server répond uniquement aux requêtes pour le domaine `omischle.42.fr`.

```nginx
    ssl_certificate     /etc/ssl/certs/inception.crt;
    ssl_certificate_key /etc/ssl/private/inception.key;
```
Le certificat et la clé générés pendant le build.

```nginx
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
```
**Restriction TLS** : on n'accepte que les protocoles TLS 1.2 et TLS 1.3. TLS 1.0 et 1.1 sont des protocoles anciens avec des vulnérabilités connues (POODLE, BEAST). `HIGH:!aNULL:!MD5` : uniquement des suites de chiffrement puissantes, pas de chiffrement nul, pas de MD5 (algorithme faible).

```nginx
    root /var/www/html;
    index index.php index.html;
```
Racine du site web = `/var/www/html` (le volume partagé avec WordPress). Si une URL pointe vers un répertoire, cherche d'abord `index.php`, puis `index.html`.

```nginx
    location / {
        try_files $uri $uri/ /index.php?$args;
    }
```
Pour toutes les URLs :
1. Essaie de servir le fichier exact (`$uri`)
2. Si c'est un répertoire, essaie de le lister (`$uri/`)
3. Sinon, passe à `index.php` avec les paramètres d'URL (`$args`)

C'est le mécanisme de routage WordPress : toutes les "jolies URLs" (/articles/mon-article) sont en réalité gérées par `index.php` de WordPress.

```nginx
    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_pass wordpress:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
```
Pour toutes les URLs se terminant par `.php` :
- `include fastcgi_params` : inclut les paramètres FastCGI standard (variables d'environnement pour PHP)
- `fastcgi_pass wordpress:9000` : transmet la requête à php-fpm sur le conteneur `wordpress`, port 9000
- `fastcgi_param SCRIPT_FILENAME ...` : dit à php-fpm quel fichier PHP exécuter. `$document_root` = `/var/www/html`, `$fastcgi_script_name` = le chemin du fichier PHP.

---

## 11. Le flux complet : de `make` à `curl`

### Étape 1 : `make` (= `make up`)

```
1. mkdir -p /home/omischle/data/db /home/omischle/data/wp
   → crée les dossiers hôte pour les volumes
   
2. docker compose -f srcs/docker-compose.yml up -d --build
   → construit les 3 images, crée le réseau, les volumes, lance les conteneurs
```

### Étape 2 : Démarrage de MariaDB

```
conteneur mariadb démarre
→ entrypoint.sh s'exécute
→ /var/lib/mysql/.initialized n'existe pas
→ mysqld démarre en mode temporaire (pas de réseau TCP)
→ SQL exécuté : root password, base wordpress, user wpuser
→ .initialized créé
→ mysqld temporaire arrêté
→ exec mysqld --user=mysql (mysqld devient PID 1)
→ MariaDB prêt sur le port 3306 du réseau Docker
```

### Étape 3 : Démarrage de WordPress

```
conteneur wordpress démarre
→ entrypoint.sh s'exécute
→ boucle TCP : tente de se connecter à mariadb:3306
→ quand MariaDB est prêt, continue
→ wp-config.php n'existe pas → wp core download (télécharge WordPress)
→ wp config create → génère wp-config.php avec les credentials BDD
→ WordPress n'est pas installé → wp core install (crée les tables en BDD)
→ wp user create author42 (crée le 2e user)
→ chown www-data sur /var/www/html
→ exec php-fpm8.2 -F (php-fpm devient PID 1)
→ php-fpm prêt sur le port 9000 du réseau Docker
```

### Étape 4 : Démarrage de Nginx

```
conteneur nginx démarre
→ nginx -g 'daemon off;' (nginx est PID 1)
→ nginx prêt sur le port 443 (TLS)
→ port 443 publié sur l'hôte
```

### Étape 5 : `curl -kI https://omischle.42.fr`

```
curl → résolution DNS de omischle.42.fr
     → /etc/hosts dit : 127.0.0.1 omischle.42.fr
     → connexion TCP vers 127.0.0.1:443
     → TLS handshake (TLS 1.2 ou 1.3, certificat auto-signé)
     → -k ignore l'avertissement certificat non-reconnu
     → requête HTTP GET / avec Host: omischle.42.fr
     → nginx reçoit la requête
     → essaie de servir /var/www/html/index.php
     → c'est un PHP → passe à php-fpm via FastCGI (wordpress:9000)
     → php-fpm exécute index.php de WordPress
     → WordPress génère le HTML
     → nginx reçoit le HTML et le renvoie à curl
     → curl affiche les headers HTTP : HTTP/1.1 200 OK ✓
```

---

## 12. Questions fréquentes en soutenance

**Q : Qu'est-ce qu'un conteneur Docker ?**
Un processus isolé qui partage le noyau de l'hôte mais a son propre système de fichiers, réseau et espace de processus. Plus léger qu'une VM, démarre en secondes.

**Q : Pourquoi debian:bookworm et pas une image toute faite ?**
Le sujet l'impose pour comprendre ce qu'on installe. On ne pull pas une image pré-configurée (pas de `FROM mysql`) — on part de la base Debian et on configure tout à la main.

**Q : C'est quoi PID 1 et pourquoi c'est important ?**
PID 1 est le premier processus d'un conteneur. Il reçoit les signaux du système (SIGTERM pour l'arrêt). Si c'est un shell wrapper, il peut ne pas transmettre ces signaux. On utilise `exec mysqld`, `exec php-fpm8.2 -F` pour que le service lui-même soit PID 1.

**Q : Différence entre `expose` et `ports` dans docker-compose ?**
- `expose: ["3306"]` → visible uniquement sur le réseau Docker interne
- `ports: ["443:443"]` → publie sur l'hôte, accessible depuis l'extérieur
On expose 3306 (MariaDB) et 9000 (php-fpm) en interne seulement. Seul le 443 (nginx) est publié.

**Q : Pourquoi TLS 1.2/1.3 seulement ?**
TLS 1.0 et 1.1 ont des vulnérabilités connues (attaques POODLE, BEAST). La directive `ssl_protocols TLSv1.2 TLSv1.3;` dans nginx les désactive explicitement.

**Q : Comment les mots de passe arrivent dans les conteneurs sans être dans les Dockerfiles ?**
Via les Docker secrets. Des fichiers dans `secrets/` sont montés en `/run/secrets/` dans les conteneurs. L'entrypoint les lit avec `cat /run/secrets/nom_secret`. Ils ne passent jamais par les variables d'environnement (pas visibles dans `docker inspect`).

**Q : Pourquoi un fichier `.initialized` dans MariaDB ?**
Quand `mariadb-server` est installé via apt, il lance `mysql_install_db` automatiquement, ce qui crée déjà le dossier `/var/lib/mysql/mysql`. On ne peut donc pas détecter le premier démarrage avec `[ ! -d /var/lib/mysql/mysql ]`. Le fichier `.initialized` est créé par nous après la configuration réussie.

**Q : Pourquoi nginx monte-t-il le volume wordpress ?**
Nginx sert les fichiers statiques directement (CSS, images, JS sans PHP). Pour ça il doit y avoir accès. Pour les PHP, il les passe à php-fpm, mais `fastcgi_param SCRIPT_FILENAME` doit pointer vers le même chemin que celui que php-fpm connaît — donc les deux voient `/var/www/html` via le même volume.

**Q : Que se passe-t-il si MariaDB redémarre après que WordPress est installé ?**
MariaDB voit `.initialized` → saute l'init → démarre mysqld directement avec les données déjà présentes sur le volume. WordPress voit que `wp-config.php` existe ET que WP est installé → va directement à `exec php-fpm`. Tout repart normalement.

**Q : Pourquoi `restart: always` ?**
Pour qu'en cas de crash ou de redémarrage de la machine hôte, Docker relance automatiquement tous les conteneurs. Sans ça, une VM rebootée nécessiterait de relancer `make` manuellement.

**Q : Que fait `make fclean` ?**
Arrête les conteneurs, supprime les volumes Docker, efface le cache de build Docker, et supprime physiquement les données dans `/home/omischle/data`. Après, le prochain `make` repart de zéro : re-télécharge WordPress, réinitialise la base de données, etc.

**Q : Qu'est-ce que FastCGI ?**
Un protocole de communication entre un serveur web (nginx) et un interpréteur de script (php-fpm). Nginx reçoit la requête HTTP, la transmet via FastCGI à php-fpm avec les paramètres nécessaires (quel fichier PHP exécuter, quelle est l'URL, etc.). php-fpm exécute le PHP et renvoie le résultat à nginx.

**Q : Pourquoi `/dev/tcp/mariadb/3306` dans le check WordPress ?**
C'est une fonctionnalité bash : ouvrir un fichier spécial `/dev/tcp/HOST/PORT` effectue une connexion TCP. C'est un moyen de vérifier qu'un port est ouvert sans avoir besoin d'outils comme `nc` (netcat) ou `curl`. On l'utilise car la connexion TCP fonctionne dès que MariaDB accepte des connexions, avant même que l'authentification soit configurée.

**Q : Quel est l'administrateur WordPress et pourquoi ce nom ?**
L'admin s'appelle `supervisor`. Le sujet interdit que le login contienne les mots `admin`, `Admin`, ou `administrator`. Le 2e utilisateur s'appelle `author42` avec le rôle `author`.

---

*Ce document a été généré pour accompagner le projet Inception du cursus 42. Toutes les décisions techniques sont motivées par les contraintes du sujet et les bonnes pratiques Docker.*
