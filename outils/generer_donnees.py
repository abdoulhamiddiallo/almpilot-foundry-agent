"""Génère les trois fichiers de données ALM de la Banque Lorraine des Entreprises (banque fictive), au 31/12/2025.

Les postes du bilan sont fixés à la main, calibrés sur des ordres de grandeur réalistes d'une banque
régionale ; le script réécrit donnees/bilan_alm.csv, donnees/courbe_taux.csv et donnees/scenarios_taux.csv
à l'identique.

Utilisation, depuis la racine du dépôt :
    python outils/generer_donnees.py
"""
from pathlib import Path
import pandas as pd
D = Path(__file__).resolve().parent.parent / "donnees"

COLS = ["id_poste", "poste", "cote", "profil", "encours_eur", "taux_client_pct", "maturite_ans", "revision_mois",
        "remb_anticipe_pct", "part_stable_pct", "maturite_stable_ans", "beta_pct",
        "niveau_hqla", "decote_hqla_pct", "fuite_30j_pct", "entree_30j_pct", "asf_pct", "rsf_pct"]
L = [
 # Actifs
 ("A01", "Réserves à la banque centrale", "Actif", "variable", 30_000_000, 2.00, 0, 0, 0, 0, 0, 100, "1", 0, 0, 0, 0, 0),
 ("A02", "Obligations d'État (échéancier 1 à 10 ans)", "Actif", "echelonne", 82_000_000, 2.60, 10, 0, 0, 0, 0, 100, "1", 0, 0, 0, 0, 5),
 ("A03", "Obligations sécurisées (échéancier 1 à 6 ans)", "Actif", "echelonne", 18_000_000, 2.85, 6, 0, 0, 0, 0, 100, "2A", 15, 0, 0, 0, 15),
 ("A04", "Crédits immobiliers aux particuliers, taux fixe", "Actif", "amortissable", 190_000_000, 3.05, 18, 0, 5, 0, 0, 100, "", 0, 0, 0.6, 0, 65),
 ("A05", "Crédits aux entreprises, taux fixe", "Actif", "amortissable", 200_000_000, 4.10, 5, 0, 0, 0, 0, 100, "", 0, 0, 1.5, 0, 85),
 ("A06", "Crédits aux entreprises, taux variable Euribor 3 mois", "Actif", "variable", 70_370_000, 4.35, 0, 3, 0, 0, 0, 100, "", 0, 0, 2.0, 0, 85),
 ("A07", "Immobilisations et autres actifs", "Actif", "non_sensible", 24_000_000, 0, 0, 0, 0, 0, 0, 0, "", 0, 0, 0, 0, 100),
 # Passifs
 ("P01", "Dépôts à vue des particuliers", "Passif", "sans_echeance", 160_000_000, 0.00, 0, 0, 0, 85, 5, 0, "", 0, 7, 0, 92, 0),
 ("P02", "Livrets d'épargne", "Passif", "sans_echeance", 120_000_000, 1.75, 0, 0, 0, 65, 4, 50, "", 0, 10, 0, 90, 0),
 ("P03", "Dépôts à vue des entreprises", "Passif", "sans_echeance", 85_000_000, 0.10, 0, 0, 0, 45, 3, 20, "", 0, 40, 0, 50, 0),
 ("P04", "Dépôts à terme (échéancier 1 à 3 ans)", "Passif", "echelonne", 60_000_000, 2.40, 3, 0, 0, 0, 0, 100, "", 0, 5, 0, 70, 0),
 ("P05", "Emprunt obligataire senior à 5 ans", "Passif", "in_fine", 70_000_000, 3.20, 5, 0, 0, 0, 0, 100, "", 0, 0, 0, 100, 0),
 ("P06", "Certificats de dépôt à 3 mois", "Passif", "variable", 30_000_000, 2.05, 0, 3, 0, 0, 0, 100, "", 0, 33, 0, 0, 0),
 ("P07", "Emprunts interbancaires au jour le jour", "Passif", "variable", 25_000_000, 1.95, 0, 0, 0, 0, 0, 100, "", 0, 100, 0, 0, 0),
 ("P08", "Fonds propres et réserves", "Passif", "non_sensible", 42_300_000, 0, 0, 0, 0, 0, 0, 0, "", 0, 0, 0, 100, 0),
 ("P09", "Autres passifs et provisions", "Passif", "non_sensible", 22_070_000, 0, 0, 0, 0, 0, 0, 0, "", 0, 0, 0, 0, 0),
 # Hors bilan
 ("H01", "Swap de couverture payeur taux fixe à 7 ans", "Hors bilan", "swap_payeur", 80_000_000, 2.55, 7, 3, 0, 0, 0, 100, "", 0, 0, 0, 0, 0),
 ("H02", "Engagements de crédit non tirés aux entreprises", "Hors bilan", "non_sensible", 42_020_000, 0, 0, 0, 0, 0, 0, 0, "", 0, 10, 0, 0, 5),
]
b = pd.DataFrame(L, columns=COLS); b["encours_eur"] = b.encours_eur.astype("int64")
b.to_csv(D / "bilan_alm.csv", index=False)
pd.DataFrame({"maturite_ans": [1/12, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30],
              "taux_zero_pct": [1.93, 1.98, 2.05, 2.10, 2.18, 2.27, 2.45, 2.62, 2.82, 3.00, 3.05, 2.95]}).round(6).to_csv(D / "courbe_taux.csv", index=False)
pd.DataFrame({"scenario": ["Parallèle haussier", "Parallèle baissier", "Pentification", "Aplatissement", "Hausse des taux courts", "Baisse des taux courts"],
              "choc_parallele_pb": [200, -200, 0, 0, 0, 0], "coef_court": [0, 0, -0.65, 0.8, 1, -1], "coef_long": [0, 0, 0.9, -0.6, 0, 0]}).to_csv(D / "scenarios_taux.csv", index=False)
a = b[b.cote == "Actif"].encours_eur.sum(); p = b[b.cote == "Passif"].encours_eur.sum()
print(f"Total de l'actif : {a:,.0f} € · total du passif : {p:,.0f} €".replace(",", " "))
