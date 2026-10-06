from flask import Flask, render_template_string, request
from google.cloud import bigquery
import plotly.express as px

px.defaults.color_discrete_map = {
    "Trail" : "#156619",
    "Course à pied" : "#CC8A0FCE",
    "Course à pied (tapis)" : "#9C16D1CE",
}

app = Flask(__name__)
client = bigquery.Client()

@app.route("/")
def dashboard():
    # Récupère le filtre choisi dans l'URL (ex: ?type=Trail), vide par défaut = tout afficher
    type_filtre = request.args.get("type", "")

    # On construit une clause WHERE conditionnelle selon le filtre
    where_clause = f"WHERE type_activite = '{type_filtre}'" if type_filtre else ""

    # --- Graphique 1 : volume hebdomadaire ---
    query1 = f"""
        SELECT semaine, SUM(distance_km) AS distance_totale
        FROM `running_data.activities`
        {where_clause}
        GROUP BY semaine
        ORDER BY semaine
    """
    df1 = client.query(query1).to_dataframe()
    df1["semaine_debut"] = df1["semaine"].str.split("/").str[0]
    fig1 = px.bar(df1, x="semaine_debut", y="distance_totale", title="Volume hebdomadaire (km)",
                  color_discrete_sequence=["#434A63CE"])

    # --- Graphique 2 : répartition par type d'activité (toujours sur l'ensemble, non filtré) ---
    query2 = """
        SELECT type_activite, COUNT(*) AS nb_sorties
        FROM `running_data.activities`
        GROUP BY type_activite
    """
    df2 = client.query(query2).to_dataframe()
    fig2 = px.pie(df2, names="type_activite", values="nb_sorties", title="Répartition par type d'activité",
                  color="type_activite",
                  labels={"type_activite": "Type d'activité", "nb_sorties": "Nombre de sorties"})

    # --- Graphique 3 : évolution de la FC moyenne dans le temps ---
    query3 = f"""
        SELECT date, fc_moyenne, type_activite
        FROM `running_data.activities`
        {where_clause}
        {"AND" if where_clause else "WHERE"} fc_moyenne IS NOT NULL
        ORDER BY date
    """
    df3 = client.query(query3).to_dataframe()
    fig3 = px.line(df3, x="date", y="fc_moyenne", title="Évolution de la FC moyenne", markers=True,
                   color_discrete_sequence=["#EE0606CE"],
                   labels={"date": "Date", "fc_moyenne": "FC moyenne (bpm)"})

    # --- Graphique 4 : allure moyenne par type d'activité ---
    query4 = """
        SELECT type_activite, AVG(allure_moyenne_min_km) AS allure_moyenne
        FROM `running_data.activities`
        WHERE allure_moyenne_min_km IS NOT NULL
        GROUP BY type_activite
    """
    df4 = client.query(query4).to_dataframe()
    fig4 = px.bar(df4, x="type_activite", y="allure_moyenne", title="Allure moyenne par type d'activité (min/km)",color="type_activite",
                  labels={"type_activite": "Type d'activité", "allure_moyenne": "Allure moyenne (min/km)"})

    # --- Graphique 5 : corrélation dénivelé / FC moyenne ---
    query5 = f"""
        SELECT denivele_positif, fc_moyenne, type_activite
        FROM `running_data.activities`
        {where_clause}
        {"AND" if where_clause else "WHERE"} fc_moyenne IS NOT NULL AND denivele_positif IS NOT NULL
    """
    df5 = client.query(query5).to_dataframe()
    fig5 = px.scatter(df5, x="denivele_positif", y="fc_moyenne", color="type_activite",
                       title="Corrélation dénivelé positif / FC moyenne",
                       labels={"denivele_positif": "Dénivelé positif (m)", "fc_moyenne": "FC moyenne (bpm)",
                               "type_activite": "Type d'activité"})

    # Menu déroulant : soumet le formulaire automatiquement au changement (onchange)
    filtre_html = f"""
        <form method="get" style="margin: 20px 0;">
            <label for="type">Filtrer par type d'activité : </label>
            <select name="type" id="type" onchange="this.form.submit()">
                <option value="" {"selected" if type_filtre == "" else ""}>Tous</option>
                <option value="Trail" {"selected" if type_filtre == "Trail" else ""}>Trail</option>
                <option value="Course à pied" {"selected" if type_filtre == "Course à pied" else ""}>Course à pied</option>
            </select>
        </form>
    """

    return render_template_string(
    """
    <html>
    <head>
        <style>
            :root {
                --bg-color: #1E1E2E;
                --card-bg: #2A2A3C;
                --text-color: #EAEAEA;
                --accent-color: #7C9CF0;
            }

            body {
                background-color: var(--bg-color);
                color: var(--text-color);
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
            }

            h1 {
                color: var(--text-color);
            }
            .tabs button {
                background-color: var(--card-bg);
                color: var(--text-color);
                border: 1px solid var(--accent-color);
                padding: 10px 20px;
                margin-right : 10px;
                cursor: pointer;
                border-radius: 6px;
            }
            .tabs button:hover {
                background-color: var(--accent_color)
            }
        </style>
    </head>
    <body>
        <h1> Mon dashboard running </h1>
        {{ filtre|safe }}

        <div class="tabs">
            <button onclick="afficherOnglet('volume')">Volume</button>
            <button onclick="afficherOnglet('sante')">Santé</button>
            <button onclick="afficherOnglet('performance')">Performance</button>
        </div>

        <div id="volume" class="tab-content">
            {{ graph1|safe }}
            {{ graph2|safe }}
        </div>

        <div id="sante" class="tab-content" style="display:none;">
            {{ graph3|safe }}
            {{ graph5|safe }}        
        </div>    

        <div id="performance" class="tab-content" style="display:none;">
            {{ graph4|safe }}
        </div>

        <script>
            function afficherOnglet(onglet) {
                document.querySelectorAll('.tab-content').forEach(function(bloc){
                    bloc.style.display = 'none';
                });
                document.getElementById(onglet).style.display = 'block';
            }
        </script>
    </body>
    </html>
    """,
    filtre=filtre_html,
    graph1=fig1.to_html(full_html=False),
    graph2=fig2.to_html(full_html=False),
    graph3=fig3.to_html(full_html=False),
    graph4=fig4.to_html(full_html=False),
    graph5=fig5.to_html(full_html=False),
)

if __name__ == "__main__":
    app.run(debug=True)