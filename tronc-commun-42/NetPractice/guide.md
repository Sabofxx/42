# NetPractice — Guide complet

> Tout ce qu'il faut savoir pour finir les 10 niveaux + méthode étape par étape.

---

## 1. Les bases du réseau TCP/IP

### 1.1 Qu'est-ce qu'une adresse IP ?
Une adresse IPv4 = **4 octets** (4 nombres de 0 à 255), séparés par des points.
Exemple : `192.168.1.42`

En binaire, chaque octet = 8 bits → une IP fait **32 bits** au total.
`192.168.1.42` → `11000000.10101000.00000001.00101010`

### 1.2 Le masque de sous-réseau (subnet mask)
Le masque sépare une IP en deux parties :
- **Partie réseau** (les bits à 1 du masque) → identifie le réseau
- **Partie hôte** (les bits à 0 du masque) → identifie la machine dans ce réseau

Deux notations équivalentes :
- Décimale : `255.255.255.0`
- CIDR : `/24` (= 24 bits à 1 dans le masque)

| CIDR | Masque            | Hôtes utilisables |
|------|-------------------|-------------------|
| /24  | 255.255.255.0     | 254               |
| /25  | 255.255.255.128   | 126               |
| /26  | 255.255.255.192   | 62                |
| /27  | 255.255.255.224   | 30                |
| /28  | 255.255.255.240   | 14                |
| /29  | 255.255.255.248   | 6                 |
| /30  | 255.255.255.252   | 2                 |

**Formule** : nombre d'hôtes utilisables = `2^(32 - CIDR) - 2`
(on enlève 2 : l'adresse réseau et l'adresse de broadcast)

### 1.3 Adresse réseau et adresse de broadcast
Pour un réseau `192.168.1.0/24` :
- **Adresse réseau** : `192.168.1.0` (tous les bits hôtes à 0) → **non assignable**
- **Adresse de broadcast** : `192.168.1.255` (tous les bits hôtes à 1) → **non assignable**
- **Hôtes utilisables** : `192.168.1.1` à `192.168.1.254`

### 1.4 Comment savoir si deux IPs sont sur le même réseau ?
Applique le masque à chaque IP avec un AND binaire. Si les deux résultats sont identiques → même réseau.

Exemple : `192.168.1.10/24` et `192.168.1.200/24`
- Les 24 premiers bits sont `192.168.1` pour les deux → **même réseau** ✅

Exemple : `192.168.1.10/25` et `192.168.1.200/25`
- /25 → masque `255.255.255.128`
- `.10` = `00001010` → bit fort = 0 → réseau `192.168.1.0`
- `.200` = `11001000` → bit fort = 1 → réseau `192.168.1.128`
- → **réseaux différents** ❌

### 1.5 La passerelle par défaut (default gateway)
Quand une machine veut parler à une IP qui **n'est pas dans son réseau**, elle envoie le paquet à sa passerelle. La passerelle = une **IP du même réseau** que la machine, généralement l'interface d'un routeur.

Règle d'or : **la gateway DOIT être dans le même sous-réseau que l'IP de la machine.**

### 1.6 Routeur vs Switch
- **Switch** : connecte des machines dans le **même réseau** (couche 2). Pas d'IP nécessaire.
- **Routeur** : connecte des **réseaux différents** (couche 3). A une IP par interface, chacune dans le réseau qu'elle relie.

### 1.7 IPs privées vs publiques
Plages privées (utilisées en interne, non routables sur Internet) :
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

Tout le reste est public (sauf cas spéciaux : `127.0.0.0/8` loopback, `169.254.0.0/16` link-local, etc.)

---

## 2. Méthode pour résoudre un niveau

À chaque exercice on te donne un schéma avec des cases à remplir (IP, masque, gateway). Voici la procédure :

### Étape 1 — Lire l'objectif
En haut de la page : "A doit communiquer avec B", etc. Repère **qui doit parler à qui**.

### Étape 2 — Identifier les sous-réseaux
Repère les groupes séparés par un routeur. Chaque côté d'un routeur = un sous-réseau différent.
Un switch ne change pas de sous-réseau.

### Étape 3 — Vérifier les masques
Toutes les machines d'un même sous-réseau doivent avoir **le même masque**.

### Étape 4 — Vérifier que les IPs sont dans le bon réseau
Pour chaque machine d'un sous-réseau, applique le masque : toutes doivent tomber sur la même adresse réseau.

### Étape 5 — Vérifier les gateways
Pour chaque machine qui doit communiquer **hors de son réseau** :
- la gateway doit être dans **son réseau** à elle
- la gateway = l'IP du **routeur côté machine**

### Étape 6 — Éviter les conflits
Deux machines ne peuvent **pas** avoir la même IP dans un sous-réseau.
N'utilise jamais l'adresse réseau (.0 souvent) ni l'adresse de broadcast (.255 souvent).

### Étape 7 — Cliquer sur [Check again]
Lis les logs en bas si ça échoue : ils disent souvent exactement ce qui cloche.

### Étape 8 — Exporter avec [Get my config]
**À ne pas oublier** : télécharge le fichier de config et place-le à la racine du repo Git.

---

## 3. Pièges classiques

1. **Gateway hors du sous-réseau** → erreur la plus fréquente. La gateway doit être joignable directement par la machine.
2. **Masque incohérent** entre machines du même sous-réseau.
3. **IP de réseau ou de broadcast** assignée à une machine → invalide.
4. **Deux interfaces d'un même routeur dans le même sous-réseau** → impossible, chaque interface est dans un réseau distinct.
5. **Masque trop petit** : avec /30 tu n'as que 2 IPs utilisables. Si on te demande 3 machines + 1 routeur dans le même sous-réseau, /30 ne suffit pas.
6. **Oublier qu'un switch ne sépare pas les réseaux** : tout ce qui est derrière un switch est dans le même sous-réseau que ce qui est devant.
7. **Confondre l'IP du routeur côté A avec l'IP du routeur côté B** : un routeur a une IP différente sur chaque interface.

---

## 4. Astuces de calcul rapide

### Convertir un CIDR en masque
- /8 = 255.0.0.0
- /16 = 255.255.0.0
- /24 = 255.255.255.0
- Ensuite, pour /25 à /32, le dernier octet :
  - /25 → 128, /26 → 192, /27 → 224, /28 → 240, /29 → 248, /30 → 252, /31 → 254, /32 → 255

### Trouver la taille de bloc
Taille de bloc = `256 - dernier_octet_du_masque`
Exemple : /26 → masque .192 → blocs de 64
Réseaux possibles : `.0`, `.64`, `.128`, `.192`

### Trouver le réseau d'une IP
Prends l'IP, descends à la frontière de bloc inférieure.
Exemple : `192.168.1.130/26` → bloc de 64 → `130 / 64 = 2.03` → réseau = `192.168.1.128`
Broadcast = `192.168.1.191` (128 + 64 - 1)
Hôtes : `.129` à `.190`

### bc autorisé pendant la défense
`echo "obase=2; 192" | bc` → conversion décimal → binaire si besoin.

---

## 5. Workflow projet (étape par étape)

1. **Télécharger** l'archive depuis l'intranet 42 (`net_practice.tgz`).
2. **Extraire** dans un dossier.
3. Lancer `./run.sh` (ou `python3 -m http.server 49242` puis ouvrir `http://localhost:49242`).
4. **Entrer ton login 42** dans le champ prévu (sinon les configs ne sont pas sauvegardables proprement).
5. Faire le **niveau 1**, cliquer [Check again], puis [Get my config] → sauvegarder le fichier.
6. Cliquer sur le bouton qui apparaît pour passer au niveau suivant.
7. Répéter pour les **10 niveaux**.
8. Créer le repo Git du projet.
9. Placer les **10 fichiers de config** à la racine du repo.
10. Écrire le `README.md` (voir section suivante).
11. Push.

---

## 6. README.md — exigences

À placer à la racine du repo. Doit contenir :

- **Première ligne en italique** :
  *This project has been created as part of the 42 curriculum by <ton_login>.*
- Section **Description** : but du projet, vue d'ensemble.
- Section **Instructions** :
  - Comment lancer l'interface (`./run.sh` ou `python3 -m http.server 49242`)
  - Comment exporter les configs ([Get my config])
  - Soumission : **10 fichiers de config à la racine du repo**, un par niveau
- Section **Resources** :
  - Concepts : adressage TCP/IP, masque de sous-réseau, gateway, routeur, switch, couches OSI
  - Liens vers docs/articles utilisés
  - Description de **comment l'IA a été utilisée** (pour quelles tâches/parties)

README en **anglais**.

---

## 7. Soumission & défense

- **10 fichiers de config exportés** à la racine du repo.
- Avoir saisi son **login** dans l'interface avant export.
- Pendant la défense : refaire **3 niveaux aléatoires** dans un temps limité.
- **Pas d'outils externes** sauf `bc` (calculatrice simple).
- Donc : être à l'aise avec les calculs binaires/CIDR à la main.

---

## 8. Ressources recommandées

- RFC 791 (IPv4), RFC 950 (subnetting) — pour les puristes
- "TCP/IP Illustrated" — Stevens
- subnet-calculator.com (entraînement uniquement, pas pendant l'éval)
- Cours réseau de 42 / openclassrooms / Cisco Networking Academy
- Vidéos YouTube : "subnetting in 7 seconds" / Practical Networking

---

## 9. Antisèche finale (à mémoriser)

```
/24 = 255.255.255.0   bloc 256   ⚠ /24 par défaut
/25 = 255.255.255.128 bloc 128
/26 = 255.255.255.192 bloc 64
/27 = 255.255.255.224 bloc 32
/28 = 255.255.255.240 bloc 16
/29 = 255.255.255.248 bloc 8
/30 = 255.255.255.252 bloc 4   (2 hôtes utilisables — parfait pour lien routeur-routeur)
```

Trois règles à ne JAMAIS oublier :
1. Gateway dans le **même sous-réseau** que la machine.
2. Toutes les machines d'un même réseau ont le **même masque**.
3. Pas d'IP en `.réseau` ni `.broadcast`.

Bonne chance broski 🚀
