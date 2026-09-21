import pandas as pd
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.linear_model import LinearRegression

df = pd.read_excel("../data/cleaned/entreprises_cleaned.xlsx")

colonnes_a_imputer = ["note", "nombre_avis"]
colonnes_contexte = ["note", "nombre_avis", "latitude", "longitude"]

print("Valeurs manquantes avant imputation :")
print(df[colonnes_a_imputer].isna().sum())
print(f"({df[colonnes_a_imputer].isna().any(axis=1).sum()} entreprises concernées sur {len(df)})\n")

resultats_comparaison = {}

# 1. Imputation par la moyenne
imputer_mean = SimpleImputer(strategy="mean")
df_mean = df.copy()
df_mean[colonnes_a_imputer] = imputer_mean.fit_transform(df[colonnes_a_imputer])
resultats_comparaison["Moyenne"] = df_mean[colonnes_a_imputer].mean()

# 2. Imputation par la médiane
imputer_median = SimpleImputer(strategy="median")
df_median = df.copy()
df_median[colonnes_a_imputer] = imputer_median.fit_transform(df[colonnes_a_imputer])
resultats_comparaison["Médiane"] = df_median[colonnes_a_imputer].mean()

# 3. Imputation par régression
imputer_regression = IterativeImputer(estimator=LinearRegression(), random_state=0)
df_regression = df.copy()
df_regression[colonnes_contexte] = imputer_regression.fit_transform(df[colonnes_contexte])
resultats_comparaison["Régression"] = df_regression[colonnes_a_imputer].mean()

# 4. Imputation par KNN
imputer_knn = KNNImputer(n_neighbors=5)
df_knn = df.copy()
df_knn[colonnes_contexte] = imputer_knn.fit_transform(df[colonnes_contexte])
resultats_comparaison["KNN"] = df_knn[colonnes_a_imputer].mean()

comparaison = pd.DataFrame(resultats_comparaison).T
comparaison.columns = ["note (moyenne)", "nombre_avis (moyenne)"]
print("Comparaison des méthodes d'imputation :")
print(comparaison)

df_mean.to_csv("../data/processed/entreprises_imputation_moyenne.csv", index=False)
df_median.to_csv("../data/processed/entreprises_imputation_mediane.csv", index=False)
df_regression.to_csv("../data/processed/entreprises_imputation_regression.csv", index=False)
df_knn.to_csv("../data/processed/entreprises_imputation_knn.csv", index=False)
comparaison.to_csv("../outputs/figures/comparaison_imputations.csv")

# Choix final : KNN (tient compte du contexte géographique)
df_final = df_knn.copy()
df_final["nombre_avis"] = df_final["nombre_avis"].round().astype(int)
df_final.to_csv("../data/processed/entreprises_final.csv", index=False)

print("\n4 versions sauvegardées dans data/processed/")
print("Comparaison sauvegardée dans outputs/figures/comparaison_imputations.csv")
print("Version finale retenue (KNN) sauvegardée dans data/processed/entreprises_final.csv")