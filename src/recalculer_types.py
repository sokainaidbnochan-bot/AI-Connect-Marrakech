import re
import pandas as pd

FICHIER = "../data/raw/offres_jooble.csv"

RE_STAGE = re.compile(
    r"\b(stage|stages|stagiaire|stagiaires|intern|interns|internship|internships|trainee|traineeship|pfe|pfa)\b",
    re.I,
)

RE_ALTERNANCE = re.compile(
    r"\b(alternance|alternant|alternante|apprentissage|apprenti|apprentie|apprenticeship)\b",
    re.I,
)


def type_offre(titre):
    titre = str(titre or "").lower()

    if RE_STAGE.search(titre):
        return "Stage"
    return "Emploi"


df = pd.read_csv(FICHIER, dtype=str).fillna("")
df["type_offre"] = df["titre"].apply(type_offre)
df.to_csv(FICHIER, index=False)

print(df["type_offre"].value_counts())
print("Types mis à jour dans :", FICHIER)