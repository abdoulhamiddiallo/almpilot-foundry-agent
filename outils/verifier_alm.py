"""Recalcule toute la chaîne ALM sans AI, puis la compare au moteur de l'agent.

Ce script est une seconde implémentation, écrite indépendamment du moteur agent/moteur_alm.py,
des articles 2 à 4 de la politique ALM : échéanciers de flux sur une grille mensuelle
(remboursements anticipés et dépôts sans échéance compris), valeur économique des fonds propres
sous les six chocs de taux de Bâle, sensibilité de la marge nette d'intérêt à 12 mois, LCR et NSFR.
Il produit les réponses de référence de l'évaluation, puis vérifie que le moteur donne exactement
les mêmes résultats, à l'euro près.

Utilisation, depuis la racine du dépôt :
    pip install -r outils/requirements.txt
    python outils/verifier_alm.py
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
DONNEES = RACINE / "donnees"
TIER1 = 35_698_654
B = pd.read_csv(DONNEES / "bilan_alm.csv", keep_default_na=False)
C = pd.read_csv(DONNEES / "courbe_taux.csv")
S = pd.read_csv(DONNEES / "scenarios_taux.csv")
G = np.arange(0, 30 * 12 + 1) / 12          # grille mensuelle de 0 à 30 ans


def euros(x):
    return ("- " if round(x) < 0 else "") + f"{abs(x):,.0f} €".replace(",", " ")


def pct(x):
    return ("- " if x < 0 else "") + f"{abs(x):.2f} %".replace(".", ",")


def zc(t):
    return np.interp(t, C.maturite_ans, C.taux_zero_pct / 100)


def choc(t, parallele=0.0, court=0.0, long=0.0):
    t = np.asarray(t, float)
    return (parallele + court * 250 * np.exp(-t / 4) + long * 100 * (1 - np.exp(-t / 4))) / 1e4


def taux_choques(t, d):
    base = zc(t)
    plancher = np.minimum(0, -0.015 + 0.0003 * np.asarray(t, float))
    return np.maximum(base + d, np.minimum(base, plancher))


def vecteurs(p, r3m, notionnel=None):
    """Principal et flux totaux d'un poste sur la grille, signés du point de vue de la banque."""
    P, F = np.zeros_like(G), np.zeros_like(G)
    s = 1.0 if p.cote == "Actif" else -1.0
    n = float(p.encours_eur if notionnel is None else notionnel)
    r = p.taux_client_pct / 100
    k = lambda t: int(round(t * 12))
    if p.profil == "variable":
        P[k(p.revision_mois / 12)] += s * n
        F[k(p.revision_mois / 12)] += s * n * (1 + r * p.revision_mois / 12)
    elif p.profil == "in_fine":
        m = int(p.maturite_ans)
        for a in range(1, m + 1):
            F[k(a)] += s * n * r
        P[k(m)] += s * n
        F[k(m)] += s * n
    elif p.profil == "echelonne":
        m = int(p.maturite_ans)
        restant = n - n / m * np.arange(m)
        for a in range(1, m + 1):
            P[k(a)] += s * n / m
            F[k(a)] += s * (n / m + restant[a - 1] * r)
    elif p.profil == "amortissable":
        N, i = int(round(p.maturite_ans * 12)), r / 12
        q = 1 - (1 - p.remb_anticipe_pct / 100) ** (1 / 12)
        solde = n
        for j in range(1, N + 1):
            annuite = solde * i / (1 - (1 + i) ** -(N - j + 1))
            rembourse = annuite - solde * i
            total = rembourse + (solde - rembourse) * q
            P[j] += s * total
            F[j] += s * (total + solde * i)
            solde -= total
    elif p.profil == "sans_echeance":
        stable = n * p.part_stable_pct / 100
        N = int(round(24 * p.maturite_stable_ans))
        P[0] += s * (n - stable)
        F[0] += s * (n - stable)
        j = np.arange(1, N + 1)
        P[j] += s * stable / N
        F[j] += s * (stable / N + (stable - stable / N * (j - 1)) * r / 12)
    elif p.profil == "swap_payeur":
        j3 = k(p.revision_mois / 12)
        P[j3] += n
        F[j3] += n * (1 + r3m * p.revision_mois / 12)
        m = int(p.maturite_ans)
        for a in range(1, m + 1):
            F[k(a)] -= n * r
        P[k(m)] -= n
        F[k(m)] -= n
    return P, F


def recalculer(sans_swap=False, notionnel=None, fuites=1.0):
    r3m = float(zc(0.25))
    Ptot, Ftot = np.zeros_like(G), np.zeros_like(G)
    mni = {200: 0.0, -200: 0.0}
    for p in B.itertuples():
        if p.profil == "non_sensible" or (sans_swap and p.profil == "swap_payeur"):
            continue
        P, F = vecteurs(p, r3m, notionnel if p.profil == "swap_payeur" else None)
        Ptot += P
        Ftot += F
        an = G < 1
        for c in mni:
            mni[c] += float((P[an] * c / 1e4 * p.beta_pct / 100 * (1 - G[an])).sum())
    va = lambda d: float((Ftot * (1 + taux_choques(G, d)) ** -G).sum())
    base = va(0.0)
    delta = {s.scenario: va(choc(G, s.choc_parallele_pb, s.coef_court, s.coef_long)) - base for s in S.itertuples()}
    pire = min(delta, key=delta.get)
    n1 = float((B.encours_eur * (1 - B.decote_hqla_pct / 100))[B.niveau_hqla == "1"].sum())
    n2 = float((B.encours_eur * (1 - B.decote_hqla_pct / 100))[B.niveau_hqla == "2A"].sum())
    hqla = n1 + min(n2, 2 / 3 * n1)
    sorties = float((B.encours_eur * B.fuite_30j_pct).sum() / 100) * fuites
    entrees = float((B.encours_eur * B.entree_30j_pct).sum() / 100)
    nettes = sorties - min(entrees, 0.75 * sorties)
    asf = float((B.encours_eur * B.asf_pct).sum() / 100)
    rsf = float((B.encours_eur * B.rsf_pct).sum() / 100)
    return dict(eve=base, delta=delta, pire=pire, perte_eve=-delta[pire], sensi=va(choc(G, 1)) - base,
                perte_mni=-min(mni.values()), hqla=hqla, nettes=nettes, lcr=hqla / nettes * 100,
                asf=asf, rsf=rsf, nsfr=asf / rsf * 100)


ref = recalculer()
print("=" * 78)
print("BANQUE LORRAINE DES ENTREPRISES · bilan ALM · données au 31/12/2025")
print("=" * 78)
print(f"EVE de base {euros(ref['eve'])} · sensibilité à + 1 pb : {euros(ref['sensi'])}")
for nom, d in ref["delta"].items():
    print(f"  {nom:<24} variation d'EVE {euros(d):>14}   {pct(d / TIER1 * 100):>9} du Tier 1")
print(f"Pire scénario : {ref['pire']} · {pct(ref['perte_eve'] / TIER1 * 100)} du Tier 1")
print(f"Perte de MNI sous ± 200 pb : {euros(ref['perte_mni'])} · {pct(ref['perte_mni'] / TIER1 * 100)} du Tier 1")
print(f"LCR {pct(ref['lcr'])} · NSFR {pct(ref['nsfr'])}")
sans = recalculer(sans_swap=True)
print(f"Simulation sans le swap H01 : perte d'EVE {pct(sans['perte_eve'] / TIER1 * 100)} · perte de MNI {pct(sans['perte_mni'] / TIER1 * 100)}")

print("\nCONTRÔLE CROISÉ AVEC agent/moteur_alm.py")
os.chdir(DONNEES)
moteur = {}
exec((RACINE / "agent" / "moteur_alm.py").read_text(encoding="utf-8"), moteur)
r = moteur["calculer"]()
t = r["totaux"]
s2 = moteur["calculer"](sans_couverture=True)["totaux"]
paires = {
    "EVE de base": (t["eve_base"], ref["eve"]),
    "Perte d'EVE, pire choc": (t["perte_eve"], ref["perte_eve"]),
    "Sensibilité à + 1 pb": (t["sensibilite_1pb"], ref["sensi"]),
    "Perte de MNI ± 200 pb": (t["perte_mni"], ref["perte_mni"]),
    "Coussin de HQLA": (t["hqla"], ref["hqla"]),
    "Sorties nettes à 30 jours": (t["sorties_nettes"], ref["nettes"]),
    "Financement stable requis": (t["rsf"], ref["rsf"]),
    "Perte d'EVE sans swap": (s2["perte_eve"], sans["perte_eve"]),
}
ecarts = {nom: abs(round(a) - round(b)) for nom, (a, b) in paires.items()}
for nom, e in ecarts.items():
    print(f"  {'✓' if e == 0 else '✗'} {nom:<28} {euros(paires[nom][1]):>16}   écart {e} €")
print(f"\n{sum(e == 0 for e in ecarts.values())} indicateurs sur {len(ecarts)} identiques à l'euro près.")
