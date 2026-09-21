"""
Analyse statistique et génération des graphiques pour le rapport.
Lit data/processed/entreprises_final.csv et exporte les figures
dans outputs/figures/.
"""
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../data/processed/entreprises_final.csv")

print(f"Nombre total d'entreprises : {len(df)}\n")

# --- 1. Statistiques descriptives ---
print("Statistiques descriptives (note et nombre d'avis) :")
print(df[["note", "nombre_avis"]].describe())

print("\nRépartition par domaine :")
print(df["categorie_recherchee"].value_counts())

print("\nRépartition par quartier :")
print(df["quartier"].value_counts())

print("\nNote moyenne par quartier :")
print(df.groupby("quartier")["note"].mean().round(2).sort_values(ascending=False))

print("\nCorrélation note / nombre d'avis :")
print(df[["note", "nombre_avis"]].corr().iloc[0, 1].round(3))

# --- 2. Graphique : répartition par domaine ---
plt.figure(figsize=(8, 5))
df["categorie_recherchee"].value_counts().plot(kind="bar", color="#2F4EC4")
plt.title("Répartition des entreprises par domaine")
plt.ylabel("Nombre d'entreprises")
plt.xlabel("Domaine")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("../outputs/figures/entreprises_par_categorie.png")
plt.close()

# --- 3. Graphique : répartition par quartier ---
plt.figure(figsize=(8, 5))
df["quartier"].value_counts().plot(kind="bar", color="#B85C34")
plt.title("Répartition des entreprises par quartier")
plt.ylabel("Nombre d'entreprises")
plt.xlabel("Quartier")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("../outputs/figures/entreprises_par_zone.png")
plt.close()

# --- 4. Graphique : distribution des notes ---
plt.figure(figsize=(8, 5))
df["note"].plot(kind="hist", bins=10, color="#3E6B52", edgecolor="white")
plt.title("Distribution des notes Google")
plt.xlabel("Note (sur 5)")
plt.ylabel("Nombre d'entreprises")
plt.tight_layout()
plt.savefig("../outputs/figures/notes_google.png")
plt.close()

# --- 5. Graphique : top 15 entreprises par nombre d'avis ---
plt.figure(figsize=(9, 6))
top15 = df.nlargest(15, "nombre_avis").sort_values("nombre_avis")
plt.barh(top15["nom"], top15["nombre_avis"], color="#2F4EC4")
plt.title("Top 15 entreprises par nombre d'avis")
plt.xlabel("Nombre d'avis")
plt.tight_layout()
plt.savefig("../outputs/figures/nombre_avis.png")
plt.close()

# --- 6. Graphique : note moyenne par quartier ---
plt.figure(figsize=(8, 5))
df.groupby("quartier")["note"].mean().sort_values(ascending=False).plot(
    kind="bar", color="#E8C36B", edgecolor="#B85C34"
)
plt.title("Note moyenne par quartier")
plt.ylabel("Note moyenne")
plt.xlabel("Quartier")
plt.xticks(rotation=30, ha="right")
plt.ylim(0, 5)
plt.tight_layout()
plt.savefig("../outputs/figures/note_moyenne_par_quartier.png")
plt.close()

print("\n5 graphiques sauvegardés dans outputs/figures/ :")
print(" - entreprises_par_categorie.png")
print(" - entreprises_par_zone.png")
print(" - notes_google.png")
print(" - nombre_avis.png")
print(" - note_moyenne_par_quartier.png")

"""
Compléments à analysis.py : les types de graphiques supplémentaires
demandés (camembert, line plot, scatter, heatmap, box plot, radar).
À coller à la suite de analysis.py, après les graphiques déjà existants.
"""
import numpy as np

# --- 7. Pie chart : part de chaque domaine ---
plt.figure(figsize=(7, 7))
repartition = df["categorie_recherchee"].value_counts()
plt.pie(repartition, labels=repartition.index, autopct="%1.1f%%",
        colors=["#2F4EC4", "#B85C34", "#3E6B52", "#E8C36B", "#5B7CFA", "#7C86B8", "#9C978C"])
plt.title("Part de chaque domaine (%)")
plt.tight_layout()
plt.savefig("../outputs/figures/camembert_domaines.png")
plt.close()

# --- 8. Line plot : concentration cumulée des entreprises par quartier ---
plt.figure(figsize=(8, 5))
counts = df["quartier"].value_counts().sort_values(ascending=False)
cumule = counts.cumsum() / counts.sum() * 100
plt.plot(range(1, len(cumule) + 1), cumule.values, marker="o", color="#2F4EC4")
plt.xticks(range(1, len(cumule) + 1), cumule.index, rotation=30, ha="right")
plt.ylabel("% cumulé des entreprises")
plt.title("Concentration cumulée des entreprises par quartier")
plt.axhline(80, color="#B85C34", linestyle="--", linewidth=1, label="Seuil 80%")
plt.legend()
plt.tight_layout()
plt.savefig("../outputs/figures/courbe_concentration_quartiers.png")
plt.close()

# --- 9. Scatter plot : note vs nombre d'avis ---
plt.figure(figsize=(8, 5))
plt.scatter(df["nombre_avis"], df["note"], color="#2F4EC4", alpha=0.6, edgecolor="white")
plt.xlabel("Nombre d'avis")
plt.ylabel("Note")
plt.title("Note en fonction du nombre d'avis")
plt.tight_layout()
plt.savefig("../outputs/figures/scatter_note_avis.png")
plt.close()

# --- 10. Heatmap : nombre d'entreprises par (quartier x domaine) ---
tableau_croise = pd.crosstab(df["quartier"], df["categorie_recherchee"])
plt.figure(figsize=(9, 6))
plt.imshow(tableau_croise, cmap="Blues", aspect="auto")
plt.colorbar(label="Nombre d'entreprises")
plt.xticks(range(len(tableau_croise.columns)), tableau_croise.columns, rotation=30, ha="right")
plt.yticks(range(len(tableau_croise.index)), tableau_croise.index)
for i in range(tableau_croise.shape[0]):
    for j in range(tableau_croise.shape[1]):
        valeur = tableau_croise.iloc[i, j]
        if valeur > 0:
            plt.text(j, i, valeur, ha="center", va="center",
                      color="white" if valeur > tableau_croise.values.max() / 2 else "black")
plt.title("Répartition croisée : quartier x domaine")
plt.tight_layout()
plt.savefig("../outputs/figures/heatmap_quartier_domaine.png")
plt.close()

# --- 11. Box plot : distribution des notes par quartier ---
plt.figure(figsize=(9, 5))
quartiers_ordre = df["quartier"].value_counts().index
donnees_par_quartier = [df[df["quartier"] == q]["note"].values for q in quartiers_ordre]
plt.boxplot(donnees_par_quartier)
plt.xticks(range(1, len(quartiers_ordre) + 1), quartiers_ordre, rotation=30, ha="right")
plt.ylabel("Note")
plt.title("Distribution des notes par quartier")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("../outputs/figures/boxplot_notes_quartier.png")
plt.close()

# --- 12. Radar chart : comparaison des quartiers sur 3 métriques normalisées ---
stats_quartier = df.groupby("quartier").agg(
    nb_entreprises=("nom", "count"),
    note_moyenne=("note", "mean"),
    avis_moyen=("nombre_avis", "mean"),
)
stats_norm = (stats_quartier - stats_quartier.min()) / (stats_quartier.max() - stats_quartier.min())

labels = ["Nombre d'entreprises", "Note moyenne", "Avis moyen"]
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
couleurs_radar = ["#2F4EC4", "#B85C34", "#3E6B52", "#E8C36B", "#5B7CFA", "#7C86B8", "#9C978C"]

for i, (quartier, ligne) in enumerate(stats_norm.iterrows()):
    valeurs = ligne.tolist()
    valeurs += valeurs[:1]
    ax.plot(angles, valeurs, label=quartier, color=couleurs_radar[i % len(couleurs_radar)])
    ax.fill(angles, valeurs, alpha=0.08, color=couleurs_radar[i % len(couleurs_radar)])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)
ax.set_title("Comparaison des quartiers (métriques normalisées)")
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8)
plt.tight_layout()
plt.savefig("../outputs/figures/radar_quartiers.png")
plt.close()

print("6 graphiques supplémentaires sauvegardés dans outputs/figures/ :")
print(" - camembert_domaines.png (pie chart)")
print(" - courbe_concentration_quartiers.png (line plot)")
print(" - scatter_note_avis.png (scatter plot)")
print(" - heatmap_quartier_domaine.png (heatmap)")
print(" - boxplot_notes_quartier.png (box plot)")
print(" - radar_quartiers.png (radar chart)")