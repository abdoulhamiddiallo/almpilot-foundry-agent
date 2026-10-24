"""Moteur ALM d'ALMPilot : la méthode de la politique, codée une fois pour toutes.

Ce module applique exactement les articles 2 à 5 de la Politique_ALM_BLE :
échéanciers de flux de chaque poste du bilan (remboursements anticipés et dépôts sans
échéance compris), valeur économique des fonds propres (EVE) sous les six scénarios de
choc de taux de Bâle, sensibilité de la marge nette d'intérêt (MNI) à 12 mois, impasses
de taux, ratio de liquidité à court terme (LCR) et ratio de financement stable (NSFR).

Utilisation dans l'interpréteur de code de l'agent :
    import glob
    exec(open(glob.glob("/mnt/data/*moteur_alm.py")[0]).read())
    r = calculer()                                   # hypothèses de la politique
    afficher(r)                                      # tous les résultats, en français
    s = calculer(sans_couverture=True)               # simulation : swap de couverture résilié
    s = calculer(notionnel_couverture=120_000_000)  # simulation : autre notionnel de couverture
    s = calculer(choc_parallele_pb=300)              # simulation : choc parallèle libre
    s = calculer(multiplicateur_fuites=1.5)          # simulation : stress de liquidité
    poste(r, "A04")                                  # détail d'un poste
    exporter_excel(r, "/mnt/data/alm_BLE.xlsx")

Utilisation locale, depuis la racine du dépôt :
    python agent/moteur_alm.py
"""
import glob
import math
import os

import numpy as np
import pandas as pd

TIER1 = 35_698_654                 # article 4 : fonds propres de catégorie 1 (CET1 net des ECL au 31/12/2025)
CHOC_COURT_PB, CHOC_LONG_PB = 250, 100   # article 3 : amplitudes de Bâle pour l'euro
CHOC_MNI_PB = 200                  # article 3 : choc parallèle de la sensibilité de la MNI
PLAFONDS_DEPOTS = {"P01": (90, 5.0), "P02": (70, 4.5), "P03": (50, 4.0)}   # article 2 : part stable, maturité moyenne
LIMITES = {                        # article 5 : (seuil d'alerte, limite)
    "eve_tier1": (10.0, 15.0),
    "mni_tier1": (3.5, 5.0),
    "lcr": (120.0, 100.0),
    "nsfr": (110.0, 100.0),
}
BANDES = [("Jour le jour à 1 mois", 0, 1 / 12), ("1 à 3 mois", 1 / 12, 0.25), ("3 à 12 mois", 0.25, 1),
          ("1 à 2 ans", 1, 2), ("2 à 5 ans", 2, 5), ("5 à 10 ans", 5, 10), ("Plus de 10 ans", 10, 99)]


# Copies de référence de la courbe et des scénarios (identiques aux fichiers), utilisées
# seulement si l'interpréteur de code n'a pas encore monté ces fichiers.
COURBE_REFERENCE = pd.DataFrame({"maturite_ans": [1 / 12, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30],
                                 "taux_zero_pct": [1.93, 1.98, 2.05, 2.10, 2.18, 2.27, 2.45, 2.62, 2.82, 3.00, 3.05, 2.95]})
SCENARIOS_REFERENCE = pd.DataFrame({
    "scenario": ["Parallèle haussier", "Parallèle baissier", "Pentification", "Aplatissement", "Hausse des taux courts", "Baisse des taux courts"],
    "choc_parallele_pb": [200, -200, 0, 0, 0, 0], "coef_court": [0, 0, -0.65, 0.8, 1, -1], "coef_long": [0, 0, 0.9, -0.6, 0, 0]})


def _trouver(nom, essais=6, pause=2.0):
    """Retrouve un fichier, même renommé par Foundry (préfixe assistant-...).

    Les fichiers de l'interpréteur de code peuvent être montés avec quelques secondes
    de retard : la recherche est répétée avant de conclure qu'un fichier manque.
    """
    import time
    for k in range(essais):
        for motif in (f"/mnt/data/*{nom}", f"/mnt/data/**/*{nom}", nom, f"*{nom}"):
            trouves = glob.glob(motif, recursive=True)
            if trouves:
                return trouves[0]
        if k < essais - 1 and os.path.isdir("/mnt/data"):
            time.sleep(pause)
    raise FileNotFoundError(f"Fichier introuvable : {nom}")


def _lire(nom, reference=None):
    """Lit un fichier de données ; à défaut, la copie de référence identique intégrée au moteur."""
    try:
        return pd.read_csv(_trouver(nom), keep_default_na=False)
    except FileNotFoundError:
        if reference is None:
            raise
        return reference.copy()


def statut(valeur, alerte, limite, vers_le_bas=False):
    """Statuts de l'article 5. Pour le LCR et le NSFR, les seuils s'appliquent vers le bas."""
    if vers_le_bas:
        if valeur < limite:
            return "DÉPASSEMENT"
        if valeur < alerte:
            return "ALERTE"
        return "CONFORME"
    if valeur > limite:
        return "DÉPASSEMENT"
    if valeur >= alerte:
        return "ALERTE"
    return "CONFORME"


def flux(p, taux_variable_3m):
    """Article 2 : échéancier (t en années, principal, intérêts) d'un poste, signe positif.

    Renvoie une liste de tuples (t, principal, interets, jambe). La jambe vaut +1 pour
    un flux reçu par la banque et -1 pour un flux payé (sens des actifs et des passifs).
    """
    sens = 1 if p.cote == "Actif" else -1
    n, r = p.encours_eur, p.taux_client_pct / 100
    out = []
    if p.profil == "variable":
        t = p.revision_mois / 12
        out.append((t, n, n * r * t, sens))
    elif p.profil == "in_fine":
        m = int(p.maturite_ans)
        for a in range(1, m + 1):
            out.append((float(a), n if a == m else 0.0, n * r, sens))
    elif p.profil == "echelonne":
        m = int(p.maturite_ans)
        reste = n
        for a in range(1, m + 1):
            out.append((float(a), n / m, reste * r, sens))
            reste -= n / m
    elif p.profil == "amortissable":
        mois = int(round(p.maturite_ans * 12))
        i = r / 12
        smm = 1 - (1 - p.remb_anticipe_pct / 100) ** (1 / 12)   # taux mensuel de remboursement anticipé
        reste = n
        for k in range(1, mois + 1):
            interets = reste * i
            annuite = reste * i / (1 - (1 + i) ** -(mois - k + 1)) if i > 0 else reste / (mois - k + 1)
            amorti = annuite - interets
            anticipe = (reste - amorti) * smm
            out.append((k / 12, amorti + anticipe, interets, sens))
            reste -= amorti + anticipe
    elif p.profil == "sans_echeance":
        stable = n * p.part_stable_pct / 100
        out.append((0.0, n - stable, 0.0, sens))                   # part non stable : jour le jour
        mois = int(round(2 * p.maturite_stable_ans * 12))          # part stable : amortie linéairement sur 2 × M
        reste = stable
        for k in range(1, mois + 1):
            out.append((k / 12, stable / mois, reste * r / 12, sens))
            reste -= stable / mois
    elif p.profil == "swap_payeur":
        t = p.revision_mois / 12                                   # jambe reçue : variable Euribor 3 mois
        out.append((t, n, n * taux_variable_3m * t, 1))
        m = int(p.maturite_ans)                                    # jambe payée : taux fixe annuel
        for a in range(1, m + 1):
            out.append((float(a), n if a == m else 0.0, n * r, -1))
    return out


def courbe_choc(courbe, scenario=None, parallele_pb=None):
    """Article 3 : taux zéro choqué r(t) + Δ(t), avec le plancher de l'Autorité bancaire européenne."""
    mats, taux = courbe.maturite_ans.to_numpy(float), courbe.taux_zero_pct.to_numpy(float) / 100

    def r(t):
        base = float(np.interp(t, mats, taux))
        if scenario is None and parallele_pb is None:
            return base
        if parallele_pb is not None:
            d = parallele_pb / 10000
        else:
            d = (scenario.choc_parallele_pb + scenario.coef_court * CHOC_COURT_PB * math.exp(-t / 4)
                 + scenario.coef_long * CHOC_LONG_PB * (1 - math.exp(-t / 4))) / 10000
        plancher = min(0.0, -0.015 + 0.0003 * t)
        return max(base + d, min(base, plancher))
    return r


def valeur(lignes, r):
    """Valeur actuelle nette des flux : Σ signe × (principal + intérêts) × (1 + r(t))^-t."""
    return sum(j * (pr + it) * (1 + r(t)) ** -t for t, pr, it, j in lignes)


def calculer(sans_couverture=False, notionnel_couverture=None, choc_parallele_pb=None, multiplicateur_fuites=1.0, exclure=None):
    """Enchaîne toute la chaîne ALM et renvoie un dictionnaire de résultats.

    sans_couverture : simulation sans le swap de couverture H01 ;
    notionnel_couverture : simulation d'un autre notionnel pour le swap H01, en euros ;
    choc_parallele_pb : choc parallèle libre en points de base, ajouté aux six scénarios ;
    multiplicateur_fuites : multiplie les taux de fuite à 30 jours (stress de liquidité) ;
    exclure : liste d'identifiants de postes à retirer (simulation de cession).
    """
    bilan = _lire("bilan_alm.csv")
    courbe = _lire("courbe_taux.csv", COURBE_REFERENCE)
    scen = _lire("scenarios_taux.csv", SCENARIOS_REFERENCE)
    if sans_couverture:
        bilan = bilan[bilan.profil != "swap_payeur"]
    if notionnel_couverture is not None:
        bilan.loc[bilan.profil == "swap_payeur", "encours_eur"] = float(notionnel_couverture)
    if exclure:
        bilan = bilan[~bilan.id_poste.isin(exclure)]
    bilan = bilan.reset_index(drop=True)
    # Article 2 : plafonds des hypothèses comportementales des dépôts sans échéance
    ecarts = []
    for k, p in bilan[bilan.profil == "sans_echeance"].iterrows():
        part_max, mat_max = PLAFONDS_DEPOTS.get(p.id_poste, (100, 99))
        if p.part_stable_pct > part_max or p.maturite_stable_ans > mat_max:
            ecarts.append(f"{p.id_poste} : hypothèse ramenée au plafond de l'article 2 (part stable {part_max} %, maturité moyenne {f'{mat_max:g}'.replace('.', ',')} ans)")
            bilan.loc[k, "part_stable_pct"] = min(p.part_stable_pct, part_max)
            bilan.loc[k, "maturite_stable_ans"] = min(p.maturite_stable_ans, mat_max)
    r0 = courbe_choc(courbe)
    taux_3m = r0(0.25)

    sensibles = bilan[~bilan.profil.isin(["non_sensible"])]
    echeanciers = {p.id_poste: flux(p, taux_3m) for p in sensibles.itertuples()}
    tous = [f for l in echeanciers.values() for f in l]

    # Article 3 : valeur économique des fonds propres et six scénarios de Bâle
    eve_base = valeur(tous, r0)
    lignes_scen = []
    for s in scen.itertuples():
        eve = valeur(tous, courbe_choc(courbe, scenario=s))
        lignes_scen.append((s.scenario, eve, eve - eve_base))
    if choc_parallele_pb is not None:
        eve = valeur(tous, courbe_choc(courbe, parallele_pb=choc_parallele_pb))
        lignes_scen.append((f"Choc parallèle de {choc_parallele_pb:+d} pb (simulation)", eve, eve - eve_base))
    scenarios = pd.DataFrame(lignes_scen, columns=["scenario", "eve", "delta_eve"]).set_index("scenario")
    pire = scenarios.delta_eve.idxmin()
    perte_eve = max(0.0, -scenarios.delta_eve.min())
    sensi_1pb = valeur(tous, courbe_choc(courbe, parallele_pb=1)) - eve_base

    # Article 3 : marge nette d'intérêt à 12 mois, bilan constant, chocs parallèles de ± 200 pb
    mni_base = float(sum((1 if p.cote == "Actif" else -1) * p.encours_eur * p.taux_client_pct / 100 for p in sensibles.itertuples()
                         if p.profil != "swap_payeur"))
    for p in sensibles[sensibles.profil == "swap_payeur"].itertuples():
        mni_base += p.encours_eur * (taux_3m - p.taux_client_pct / 100)
    beta = dict(zip(bilan.id_poste, bilan.beta_pct / 100))
    delta_mni = {}
    for choc in (CHOC_MNI_PB, -CHOC_MNI_PB):
        d = 0.0
        for idp, lignes in echeanciers.items():
            for t, pr, it, j in lignes:
                if t < 1 and pr:
                    d += j * pr * (choc / 10000) * beta[idp] * (1 - t)
        delta_mni[choc] = d
    if choc_parallele_pb is not None and choc_parallele_pb not in delta_mni:
        delta_mni[choc_parallele_pb] = sum(j * pr * (choc_parallele_pb / 10000) * beta[idp] * (1 - t)
                                           for idp, lignes in echeanciers.items() for t, pr, it, j in lignes if t < 1 and pr)
    perte_mni = max(0.0, -min(delta_mni[CHOC_MNI_PB], delta_mni[-CHOC_MNI_PB]))

    # Article 3 : impasses de taux par bande de révision (principal)
    imp = []
    for nom, a, b in BANDES:
        act = sum(pr for t, pr, it, j in tous if j > 0 and a <= t < b)
        pas = sum(pr for t, pr, it, j in tous if j < 0 and a <= t < b)
        imp.append((nom, act, pas, act - pas))
    impasses = pd.DataFrame(imp, columns=["bande", "actifs", "passifs", "impasse"]).set_index("bande")
    impasses["impasse_cumulee"] = impasses.impasse.cumsum()

    # Article 4 : liquidité, LCR et NSFR
    n1 = float(bilan[bilan.niveau_hqla == "1"].eval("encours_eur * (1 - decote_hqla_pct / 100)").sum())
    n2 = float(bilan[bilan.niveau_hqla == "2A"].eval("encours_eur * (1 - decote_hqla_pct / 100)").sum())
    n2_retenu = min(n2, n1 * 2 / 3)                                # niveau 2 plafonné à 40 % du coussin
    hqla = n1 + n2_retenu
    sorties = float((bilan.encours_eur * bilan.fuite_30j_pct / 100).sum()) * multiplicateur_fuites
    entrees = float((bilan.encours_eur * bilan.entree_30j_pct / 100).sum())
    entrees_retenues = min(entrees, 0.75 * sorties)
    sorties_nettes = sorties - entrees_retenues
    lcr = hqla / sorties_nettes * 100
    asf = float((bilan.encours_eur * bilan.asf_pct / 100).sum())
    rsf = float((bilan.encours_eur * bilan.rsf_pct / 100).sum())
    nsfr = asf / rsf * 100

    valeurs = {"eve_tier1": perte_eve / TIER1 * 100, "mni_tier1": perte_mni / TIER1 * 100, "lcr": lcr, "nsfr": nsfr}
    statuts = {k: statut(v, *LIMITES[k], vers_le_bas=k in ("lcr", "nsfr")) for k, v in valeurs.items()}

    detail = []
    for p in bilan.itertuples():
        l = echeanciers.get(p.id_poste, [])
        v0 = valeur(l, r0) if l else 0.0
        vh = valeur(l, courbe_choc(courbe, parallele_pb=200)) if l else 0.0
        duree = abs(sum(t * j * (pr + it) * (1 + r0(t)) ** -t for t, pr, it, j in l) / v0) if l and v0 and p.profil != "swap_payeur" else 0.0
        detail.append((p.id_poste, p.poste, p.cote, p.profil, p.encours_eur, p.taux_client_pct, v0, vh - v0, duree))
    postes = pd.DataFrame(detail, columns=["id_poste", "poste", "cote", "profil", "encours", "taux_pct", "valeur_actuelle",
                                           "delta_parallele_haussier", "duration"]).set_index("id_poste")
    return {
        "bilan": bilan, "postes": postes, "scenarios": scenarios, "impasses": impasses,
        "totaux": {
            "total_actif": float(bilan[bilan.cote == "Actif"].encours_eur.sum()), "tier1": TIER1,
            "eve_base": eve_base, "pire_scenario": pire, "perte_eve": perte_eve, "sensibilite_1pb": sensi_1pb,
            "mni_base": mni_base, "delta_mni_hausse": delta_mni[CHOC_MNI_PB], "delta_mni_baisse": delta_mni[-CHOC_MNI_PB],
            "delta_mni": delta_mni, "perte_mni": perte_mni,
            "hqla_niveau1": n1, "hqla_niveau2a": n2, "hqla": hqla, "sorties_30j": sorties, "entrees_30j": entrees,
            "entrees_retenues": entrees_retenues, "sorties_nettes": sorties_nettes, "lcr": lcr,
            "asf": asf, "rsf": rsf, "nsfr": nsfr, "taux_3m": taux_3m,
            "simulation": bool(sans_couverture or notionnel_couverture is not None or choc_parallele_pb is not None or multiplicateur_fuites != 1.0 or exclure),
        },
        "valeurs": valeurs, "statuts": statuts, "ecarts_hypotheses": ecarts,
    }


def euros(x):
    return f"{x:,.0f} €".replace(",", " ").replace("-", "- ") if x < 0 else f"{x:,.0f} €".replace(",", " ")


def pct(x):
    return f"- {-x:.2f} %".replace(".", ",") if x < 0 else f"{x:.2f} %".replace(".", ",")


def poste(r, identifiant):
    """Affiche le détail d'un poste : encours, valeur actuelle, duration, sensibilité au choc parallèle haussier."""
    p = r["postes"].loc[identifiant]
    print(f"{identifiant} · {p.poste} · {p.cote} · profil {p.profil}")
    print(f"Encours {euros(p.encours)} · taux client {pct(p.taux_pct)} · valeur actuelle {euros(p.valeur_actuelle)}")
    duree = "non significative (swap)" if p.profil == "swap_payeur" else f"{p.duration:.2f} ans".replace(".", ",")
    print(f"Duration {duree} · variation de valeur sous le choc parallèle haussier : {euros(p.delta_parallele_haussier)}")


def afficher(r):
    """Affiche tous les résultats au format de la politique."""
    t, s, v = r["totaux"], r["statuts"], r["valeurs"]
    if t["simulation"]:
        print("SIMULATION : les résultats officiels de la politique ne changent pas.\n")
    for e in r["ecarts_hypotheses"]:
        print(f"CONTRÔLE DES HYPOTHÈSES : {e}")
    print(f"BILAN : total de l'actif {euros(t['total_actif'])} · fonds propres de catégorie 1 (Tier 1) {euros(t['tier1'])}")
    print("\nPOSTE | CÔTÉ | ENCOURS | TAUX | VALEUR ACTUELLE | DURATION (ANS)")
    for idp, p in r["postes"].iterrows():
        if p.profil != "non_sensible":
            duree = "non significative (swap)" if p.profil == "swap_payeur" else f"{p.duration:.2f}".replace(".", ",")
            print(f"{idp} {p.poste} | {p.cote} | {euros(p.encours)} | {pct(p.taux_pct)} | {euros(p.valeur_actuelle)} | {duree}")
    print(f"\nVALEUR ÉCONOMIQUE DES FONDS PROPRES (article 3) : EVE de base {euros(t['eve_base'])} · sensibilité à + 1 pb : {euros(t['sensibilite_1pb'])}")
    print("SCÉNARIO | EVE | VARIATION D'EVE | VARIATION / TIER 1")
    for nom, l in r["scenarios"].iterrows():
        print(f"{nom} | {euros(l.eve)} | {euros(l.delta_eve)} | {pct(l.delta_eve / t['tier1'] * 100)}")
    print(f"Pire scénario : {t['pire_scenario']} · perte de valeur {euros(t['perte_eve'])} · {pct(v['eve_tier1'])} du Tier 1")
    for idp, p in r["postes"].iterrows():
        if p.profil == "swap_payeur":
            print(f"Contribution du swap de couverture {idp} ({euros(p.encours)}) au choc parallèle haussier : {euros(p.delta_parallele_haussier)} · valeur actuelle {euros(p.valeur_actuelle)}")
    print(f"\nMARGE NETTE D'INTÉRÊT À 12 MOIS (article 3) : MNI de base {euros(t['mni_base'])}")
    print(f"Choc + 200 pb : {euros(t['delta_mni_hausse'])} · choc - 200 pb : {euros(t['delta_mni_baisse'])} · perte retenue {euros(t['perte_mni'])} · {pct(v['mni_tier1'])} du Tier 1")
    for choc, d in t["delta_mni"].items():
        if abs(choc) != CHOC_MNI_PB:
            print(f"Choc de {choc:+d} pb (simulation) : {euros(d)}")
    print("\nIMPASSES DE TAUX (principal révisé par bande)")
    print("BANDE | ACTIFS | PASSIFS | IMPASSE | IMPASSE CUMULÉE")
    for nom, l in r["impasses"].iterrows():
        print(f"{nom} | {euros(l.actifs)} | {euros(l.passifs)} | {euros(l.impasse)} | {euros(l.impasse_cumulee)}")
    print(f"\nLIQUIDITÉ (article 4) : HQLA niveau 1 {euros(t['hqla_niveau1'])} · niveau 2A après décote {euros(t['hqla_niveau2a'])} · coussin {euros(t['hqla'])}")
    print(f"Sorties à 30 jours {euros(t['sorties_30j'])} · entrées {euros(t['entrees_30j'])} (retenues {euros(t['entrees_retenues'])}) · sorties nettes {euros(t['sorties_nettes'])}")
    print(f"LCR {pct(t['lcr'])} · financement stable disponible {euros(t['asf'])} · requis {euros(t['rsf'])} · NSFR {pct(t['nsfr'])}")
    print("\nTABLEAU DES LIMITES (article 5)")
    print("INDICATEUR | VALEUR | SEUIL D'ALERTE | LIMITE | STATUT")
    noms = {"eve_tier1": f"Perte d'EVE du pire scénario ({t['pire_scenario']}) / Tier 1",
            "mni_tier1": "Perte de MNI à 12 mois (± 200 pb) / Tier 1", "lcr": "Ratio de liquidité à court terme (LCR)",
            "nsfr": "Ratio de financement stable (NSFR)"}
    for k in v:
        a, l = LIMITES[k]
        seuils = (f"inférieur à {pct(a)}", f"inférieur à {pct(l)}") if k in ("lcr", "nsfr") else (pct(a), pct(l))
        print(f"{noms[k]} | {pct(v[k])} | {seuils[0]} | {seuils[1]} | {s[k]}")
    print("\nACTIONS REQUISES (article 6)")
    actions = {
        "eve_tier1": "Risque de taux sur la valeur : proposition de couverture au Comité ALM sous 15 jours, avec l'impact de chaque option sur la perte d'EVE.",
        "mni_tier1": "Risque de taux sur la marge : plan d'ajustement de la structure de taux (couverture ou politique tarifaire) présenté au Comité ALM sous 30 jours.",
        "lcr": "Liquidité à court terme : reconstitution du coussin de HQLA et suivi quotidien du LCR par la Trésorerie jusqu'au retour au-dessus de 120 %.",
        "nsfr": "Financement stable : plan d'allongement des ressources (émission ou dépôts à terme) présenté au Comité ALM sous 30 jours.",
    }
    liste = [f"{actions[k]} ({s[k]})" for k in v if s[k] != "CONFORME"]
    if "DÉPASSEMENT" in s.values():
        liste.append("DÉPASSEMENT : information immédiate du Directeur général et du Conseil d'administration ; notification au superviseur pour un dépassement de la limite d'EVE (test des valeurs extrêmes à 15 %) ou d'un ratio réglementaire de liquidité.")
    for k, a in enumerate(liste or ["Aucune action d'escalade requise."], 1):
        print(f"{k}. {a}")


def exporter_excel(r, chemin="/mnt/data/alm_BLE.xlsx"):
    """Écrit le fichier Excel : postes, scénarios, impasses et liquidité."""
    t = r["totaux"]
    postes = r["postes"].reset_index().rename(columns={"id_poste": "Poste", "poste": "Libellé", "cote": "Côté", "profil": "Profil",
        "encours": "Encours (€)", "taux_pct": "Taux client (%)", "valeur_actuelle": "Valeur actuelle (€)",
        "delta_parallele_haussier": "Variation choc + 200 pb (€)", "duration": "Duration (ans)"})
    scen = r["scenarios"].reset_index().rename(columns={"scenario": "Scénario", "eve": "EVE (€)", "delta_eve": "Variation d'EVE (€)"})
    scen["Variation / Tier 1 (%)"] = scen["Variation d'EVE (€)"] / t["tier1"] * 100
    imp = r["impasses"].reset_index().rename(columns={"bande": "Bande", "actifs": "Actifs (€)", "passifs": "Passifs (€)",
        "impasse": "Impasse (€)", "impasse_cumulee": "Impasse cumulée (€)"})
    liq = pd.DataFrame([("Coussin de HQLA", t["hqla"]), ("Sorties nettes à 30 jours", t["sorties_nettes"]), ("LCR (%)", t["lcr"]),
                        ("Financement stable disponible", t["asf"]), ("Financement stable requis", t["rsf"]), ("NSFR (%)", t["nsfr"])],
                       columns=["Indicateur", "Valeur"])
    with pd.ExcelWriter(chemin) as classeur:
        postes.round(2).to_excel(classeur, sheet_name="Postes", index=False)
        scen.round(2).to_excel(classeur, sheet_name="Scénarios de taux", index=False)
        imp.round(0).to_excel(classeur, sheet_name="Impasses", index=False)
        liq.round(2).to_excel(classeur, sheet_name="Liquidité", index=False)
    return chemin


if __name__ == "__main__" and globals().get("__file__", "").endswith("moteur_alm.py"):
    ici = os.path.dirname(os.path.abspath(__file__))
    donnees = os.path.join(ici, "..", "donnees")
    os.chdir(donnees if os.path.isdir(donnees) and not os.path.exists(os.path.join(ici, "bilan_alm.csv")) else ici)
    afficher(calculer())
