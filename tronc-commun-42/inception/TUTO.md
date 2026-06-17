# Inception — Tuto complet (login: omischle, base: Debian bookworm)

Ce projet est **déjà entièrement écrit** dans ce dossier. Ce tuto explique :
1. ce qui a été fait et pourquoi (pour la défense),
2. comment le lancer en 5 minutes,
3. comment vérifier que tout valide le barème.

> ⚠️ Tout DOIT tourner **dans une VM**. C'est une règle du sujet (et `make fclean`
> utilise `sudo rm -rf /home/omischle/data`).

---

## 0. Mettre en place la VM (à faire en premier)

### Quel logiciel de virtualisation ?
- **VirtualBox** (gratuit, multiplateforme) → le choix standard à 42, recommandé ici.
- Alternatives : VMware, UTM (Mac Apple Silicon), KVM/virt-manager (Linux). Le
  principe est le même.

Installer VirtualBox :
- **Mac/Windows** : https://www.virtualbox.org/wiki/Downloads
- **Linux (Debian/Ubuntu)** : `sudo apt-get install -y virtualbox`
 
> 💡 Sur les machines 42, le dossier `~/goinfre` ou `~/sgoinfre` est souvent
> imposé pour stocker le disque de la VM (sinon plus de quota). Mets le disque
> virtuel là si tu es sur un poste du campus.

### Quel OS dans la VM ?
**Debian 12 (bookworm)** — le même que la base de nos images, donc cohérent et
simple. Ubuntu Server 22.04/24.04 marche aussi.
- ISO Debian (netinst) : https://www.debian.org/distrib/ → "netinst" amd64.

### Créer la VM dans VirtualBox
1. **Nouvelle** → Nom `inception`, Type *Linux*, Version *Debian (64-bit)*.
2. **RAM** : 2048 Mo minimum (4096 conseillé). **CPU** : 2 cœurs.
3. **Disque** : VDI, taille fixe ou dynamique, **~15–20 Go**.
4. Dans **Configuration → Stockage** : monte l'ISO Debian dans le lecteur optique.
5. **Réseau** : NAT suffit. Pour accéder au site depuis ton navigateur hôte,
   ajoute une **redirection de port** (Configuration → Réseau → Avancé →
   Redirection de ports) : Hôte `8443` → Invité `443` (TCP). Sinon, teste
   directement dans le navigateur **de la VM**.
6. **Démarrer** et installer Debian (installation graphique) :
   - crée ton utilisateur (idéalement le login `omischle`),
   - à l'étape "logiciels", coche au moins **"SSH server"** et **"utilitaires
     usuels du système"** (l'environnement de bureau est optionnel ; si tu veux
     un navigateur dans la VM, coche un bureau léger comme XFCE).
7. Redémarre, retire l'ISO.

### Une fois Debian installé, dans la VM
```bash
# Mises à jour + sudo
su -                                   # passe root (mot de passe root choisi à l'install)
apt-get update && apt-get -y upgrade
apt-get install -y sudo curl git make
usermod -aG sudo omischle              # donne les droits sudo à ton user
exit                                   # reviens à ton user (déconnexion/reconnexion)
```

Puis enchaîne sur la **section 1** ci-dessous (installation de Docker + lancement).

> 🔁 **Récupérer ce projet dans la VM** : soit tu `git clone` ton repo, soit tu
> copies le dossier `inception/` (dossier partagé VirtualBox, `scp`, clé USB…).
> Tout ce qui suit se fait **à l'intérieur de la VM**.

---

## 0bis. Arborescence finale

```
inception/
├── Makefile
├── README.md          # 1re ligne en italique + sections obligatoires
├── USER_DOC.md        # doc utilisateur (obligatoire pour valider)
├── DEV_DOC.md         # doc développeur (obligatoire pour valider)
├── .gitignore         # ignore secrets/
├── secrets/           # mots de passe (JAMAIS sur git)
│   ├── db_root_password.txt
│   ├── db_password.txt
│   └── credentials.txt        # ligne1 = admin WP, ligne2 = author WP
└── srcs/
    ├── .env                   # variables NON sensibles
    ├── docker-compose.yml
    └── requirements/
        ├── mariadb/  {Dockerfile, .dockerignore, conf/50-server.cnf, tools/init.sh}
        ├── nginx/    {Dockerfile, .dockerignore, conf/nginx.conf}
        └── wordpress/{Dockerfile, .dockerignore, conf/www.conf, tools/setup.sh}
```

---

## 1. Lancement rapide (sur la VM)

```bash
# a) Installer les outils si besoin
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin make
sudo usermod -aG docker $USER     # puis se déconnecter/reconnecter

# b) Faire pointer le domaine vers la machine (une seule fois)
echo "127.0.0.1 omischle.42.fr" | sudo tee -a /etc/hosts

# c) (recommandé) Mettre TES propres mots de passe
nano secrets/db_root_password.txt        # 1 ligne
nano secrets/db_password.txt             # 1 ligne
nano secrets/credentials.txt             # ligne1 = pwd admin, ligne2 = pwd author

# d) Tout construire et lancer
make
```

Puis dans le navigateur de la VM : **https://omischle.42.fr**
(accepter le certificat auto-signé). Admin : **/wp-admin**
- admin : `supervisor` / (ligne 1 de `credentials.txt`)
- author : `author` / (ligne 2 de `credentials.txt`)

---

## 2. Ce que fait chaque brique (pour la défense)

### docker-compose.yml
- **3 services** : `mariadb`, `wordpress`, `nginx`. Chaque image porte le nom du
  service (`image: mariadb`, etc.), chacune buildée depuis son `Dockerfile`.
- **network** `inception` (bridge) → la ligne `networks:` est bien présente,
  **pas** de `network: host`, `--link` ni `links:`.
- **volumes nommés** `db_data` et `wp_data` : on utilise le driver `local` avec
  `o: bind` + `device: /home/omischle/data/...`. C'est l'astuce qui satisfait
  les deux contraintes du sujet : « volumes **nommés** » ET « données dans
  `/home/login/data` ». Ce n'est pas un bind mount au sens `- ./x:/y`.
- **secrets** : les 3 fichiers de `secrets/` sont montés en lecture seule dans
  `/run/secrets/` des conteneurs → aucun mot de passe dans les Dockerfiles ni
  dans `.env`.
- **`restart: always`** partout → redémarrage après crash.
- Seul **nginx publie un port** (`443:443`). MariaDB (3306) et php-fpm (9000)
  sont seulement `expose` (réseau interne uniquement).
- ⚠️ Pas de ligne `version:` (obsolète dans Compose v2).

### MariaDB (`requirements/mariadb`)
- `Dockerfile` : `FROM debian:bookworm`, installe `mariadb-server`.
- `conf/50-server.cnf` : `bind-address = 0.0.0.0` pour que WordPress s'y connecte.
- `tools/init.sh` (entrypoint) :
  - lit les secrets `db_root_password` / `db_password`,
  - à la **première** init (volume vide) : `mariadb-install-db`, crée la base,
    l'utilisateur WordPress et le mot de passe root via `mysqld --bootstrap`,
  - puis **`exec mysqld`** → le démon devient **PID 1** (pas de `tail -f`,
    pas de `sleep infinity`).

### WordPress + php-fpm (`requirements/wordpress`)
- `Dockerfile` : `debian:bookworm` + `php-fpm php-mysql php-cli`, `mariadb-client`,
  et **wp-cli**. Pas de nginx ici.
- `conf/www.conf` : php-fpm écoute en **TCP 9000** (et pas en socket) pour être
  joignable par nginx.
- `tools/setup.sh` (entrypoint) :
  - attend que MariaDB réponde,
  - si pas encore installé : `wp core download` → `wp config create` →
    `wp core install` (crée l'**admin** `supervisor`, dont le nom ne contient
    PAS « admin »/« administrator ») → `wp user create` (2e utilisateur `author`),
  - **`exec php-fpm8.2 -F`** → PID 1.

### NGINX (`requirements/nginx`)
- `Dockerfile` : `debian:bookworm` + `nginx openssl`, génère un certificat
  auto-signé, copie la conf, supprime le site par défaut.
- `conf/nginx.conf` : écoute **443 ssl** uniquement, `ssl_protocols TLSv1.2
  TLSv1.3` seulement, et passe le PHP à `wordpress:9000` via fastcgi.
- Entrypoint : `nginx -g 'daemon off;'` → PID 1, reste au premier plan.

---

## 3. Checklist de validation (barème)

| Exigence du sujet | OK ? | Où |
|---|---|---|
| Tout dans une VM | à faire par toi | — |
| `Makefile` à la racine, build via docker-compose | ✅ | `Makefile` |
| Fichiers de conf dans `srcs/` | ✅ | `srcs/` |
| 1 Dockerfile par service, écrits par toi | ✅ | `requirements/*/Dockerfile` |
| Base = avant-dernière stable Debian | ✅ | `FROM debian:bookworm` |
| Pas d'images toutes faites (sauf Debian) | ✅ | — |
| Nom d'image = nom du service | ✅ | `image: mariadb/wordpress/nginx` |
| 1 conteneur dédié par service | ✅ | compose |
| NGINX TLSv1.2/1.3 only, seul point d'entrée, port 443 | ✅ | `nginx.conf` |
| WordPress + php-fpm sans nginx | ✅ | `wordpress/` |
| MariaDB sans nginx | ✅ | `mariadb/` |
| Volume BDD + volume fichiers WP | ✅ | `db_data`, `wp_data` |
| Volumes **nommés**, données dans `/home/omischle/data` | ✅ | `driver_opts` |
| docker-network entre conteneurs | ✅ | `networks: inception` |
| `restart` en cas de crash | ✅ | `restart: always` |
| 2 users WP dont 1 admin (nom ≠ admin/administrator) | ✅ | `supervisor` + `author` |
| Domaine `omischle.42.fr` → IP locale | à faire | `/etc/hosts` |
| Pas de `latest` | ✅ | tags `bookworm` |
| Pas de mot de passe dans les Dockerfiles | ✅ | secrets |
| Variables d'env + fichier `.env` | ✅ | `srcs/.env` |
| Secrets pour les infos confidentielles | ✅ | `secrets/` + `secrets:` |
| Credentials ignorés par git | ✅ | `.gitignore` |
| Pas de hack (tail -f, sleep infinity, while true) | ✅ | entrypoints `exec` |
| Pas de `network: host` / `--link` / `links:` | ✅ | compose |
| README.md (1re ligne italique + sections) | ✅ | `README.md` |
| USER_DOC.md + DEV_DOC.md | ✅ | racine |

---

## 4. Commandes de vérification

```bash
make ps                                   # 3 conteneurs "Up"
docker exec -it nginx nginx -t            # conf nginx OK
docker exec -it mariadb mariadb -e "SHOW DATABASES;"   # demande le pwd root
docker exec -it wordpress wp user list --allow-root --path=/var/www/html
curl -kI https://omischle.42.fr           # HTTP/1.1 200 OK

# Vérifier le TLS : doit accepter 1.2/1.3 et refuser 1.1
openssl s_client -connect omischle.42.fr:443 -tls1_3 </dev/null 2>/dev/null | grep Protocol
openssl s_client -connect omischle.42.fr:443 -tls1_1 </dev/null 2>&1 | grep -i "alert\|error"

# Persistance : les données sont bien sur l'hôte
ls -la /home/omischle/data/db /home/omischle/data/wp
```

---

## 5. Git (sur la VM, dans ton repo rendu)

```bash
git init
git add Makefile README.md USER_DOC.md DEV_DOC.md .gitignore srcs/
git status        # VÉRIFIER que secrets/ et aucun mot de passe n'apparaissent
git commit -m "Inception"
git push
```

> Le `.env` peut être versionné **uniquement** parce qu'il ne contient AUCUN mot
> de passe (que des noms/users/domaine). Les mots de passe sont exclusivement
> dans `secrets/`, qui est dans `.gitignore`. Si un correcteur trouve un mot de
> passe dans le repo → échec direct.

---

## 6. Dépannage rapide

- **wordpress redémarre en boucle** : MariaDB pas prête / mauvais mot de passe.
  `make fclean && make` (repart d'une BDD vierge ; les pwd ne sont appliqués
  qu'à la 1re création).
- **502 Bad Gateway** : php-fpm n'écoute pas en 9000 → vérifier `www.conf` et
  que la version PHP du chemin (`8.2`) correspond (`docker exec wordpress ls
  /etc/php`).
- **Certificat refusé** : normal (auto-signé), cliquer « Accepter le risque ».
- **`make fclean` échoue** : `sudo` requis, à lancer sur la VM.
- **Changement de mot de passe sans effet** : il faut une BDD vierge →
  `make fclean && make`.

---

## 7. Bonus (seulement si le mandatory est PARFAIT)

À ajouter ensuite, chacun dans `requirements/<service>/` avec son propre
Dockerfile et son service dans le compose : `redis` (cache WP), `ftp` (pointant
sur le volume WP), un **site statique** (langage ≠ PHP), **Adminer**, et un
service libre justifiable. Demande-moi si tu veux que je les génère.

Bon courage 💪
