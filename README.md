# Dashboard Running & Trail — Analyse de données Garmin

Pipeline data complet allant de l'export CSV Garmin jusqu'à un dashboard web interactif, pour analyser mon activité running et trail (volume, fréquence cardiaque, allure, dénivelé).

## Fonctionnalités

- **Nettoyage et transformation** des données brutes Garmin (CSV) avec Pandas
- **Stockage** dans Google BigQuery pour l'analyse via SQL
- **Dashboard interactif** avec Flask + Plotly :
  - Filtre dynamique par type d'activité (Trail / Course à pied)
  - Navigation par onglets (Volume / Santé / Performance)
  - Thème sombre personnalisé

## Aperçu

### Vue d'ensemble et navigation par onglets
![Dashboard - onglet Santé](screenshots/dashboard_sante.png)

### Répartition des activités
![Répartition par type d'activité](screenshots/repartition_activites.png)

## Stack technique

- **Python** — Pandas pour le nettoyage et la transformation des données
- **Google BigQuery** — stockage et requêtes SQL pour le calcul des KPIs
- **Flask** — serveur web et logique applicative
- **Plotly** — visualisation de données interactive
- **HTML / CSS / JavaScript** — mise en forme et navigation par onglets

## Graphiques disponibles

| Onglet | Graphiques |
|---|---|
| Volume | Volume hebdomadaire (km), Répartition par type d'activité |
| Santé | Évolution de la FC moyenne dans le temps, Corrélation dénivelé positif / FC moyenne |
| Performance | Allure moyenne par type d'activité |

## Installation et lancement en local

```bash
# Cloner le repo
git clone <url-du-repo>
cd csvgarmin

# Créer et activer l'environnement virtuel
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Installer les dépendances
pip install -r requirements.txt

# S'authentifier auprès de Google Cloud
gcloud auth application-default login

# Lancer le dashboard
python app.py
```

Puis ouvrir `http://127.0.0.1:5000` dans un navigateur.

## Structure du projet

```
csvgarmin/
├── app.py                  # Application Flask + dashboard
├── clean_and_load.py       # Script de nettoyage CSV et chargement BigQuery
├── requirements.txt        # Dépendances Python
├── .gitignore
└── screenshots/            # Captures d'écran du dashboard
```

## Pistes d'amélioration

- Automatiser le rechargement des données à chaque nouvel export Garmin
- Ajouter des indicateurs de progression (comparaison mois/mois, records personnels)
- Déployer le dashboard en ligne (Cloud Run ou équivalent)
