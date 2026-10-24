<div align="center">

# 🏛️ ALMPilot

### L'agent AI qui pilote le risque de taux et la liquidité d'une banque, construit sur Microsoft Foundry

**Valeur économique (EVE) · Six chocs de taux de Bâle · Marge nette d'intérêt · Impasses de taux · Dépôts sans échéance · Couverture par swap · LCR · NSFR · Politique en RAG · Garde-fou · Évaluation automatique**

![Microsoft Foundry](https://img.shields.io/badge/Microsoft_Foundry-Agent_Service-5C2D91?style=for-the-badge&logo=microsoft&logoColor=white)
![Modèle](https://img.shields.io/badge/Modèle-gpt--5--mini-1E3A8A?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![IRRBB](https://img.shields.io/badge/IRRBB-LCR_·_NSFR-1D4ED8?style=for-the-badge)

![Similarité](https://img.shields.io/badge/Exactitude_des_chiffres-12%2F12-16A34A?style=flat-square)
![Outils](https://img.shields.io/badge/Usage_des_outils-60%2F60-16A34A?style=flat-square)
![Sécurité](https://img.shields.io/badge/Sécurité-36%2F36-16A34A?style=flat-square)
![Manipulations](https://img.shields.io/badge/Manipulations_refusées-2%2F2-16A34A?style=flat-square)
![Contrôle croisé](https://img.shields.io/badge/Contrôle_croisé-8%2F8_à_l'euro_près-16A34A?style=flat-square)
![Langue](https://img.shields.io/badge/Langue-français-1E40AF?style=flat-square)

</div>

> **Le principe en une phrase : le modèle raisonne et rédige, un moteur de calcul validé chiffre, la politique décide.**
> Aucun chiffre ne sort de la mémoire du modèle. Chaque montant est produit par un moteur ALM exécuté dans l'interpréteur de code, chaque statut est justifié par un article de la politique de la banque, et la qualité de l'ensemble est prouvée par une évaluation automatique sur des réponses calculées d'avance.

---

## 🎬 Aperçu

<div align="center">

![Architecture d'ALMPilot dans Microsoft Foundry](docs/images/architecture.svg)

*L'agent `almpilot-ble`, son moteur de calcul, sa politique indexée, son garde-fou et son évaluation, dans le projet Foundry `proj-riskpilot`.*

</div>

| La démonstration | Le dilemme de la couverture |
|:---:|:---:|
| ![ALMPilot rédige la note ALM puis simule la résiliation du swap](docs/images/almpilot_demo.gif) | ![Perte d'EVE et perte de MNI selon le notionnel du swap](docs/images/dilemme_couverture.gif) |
| La note du Comité ALM depuis Python, puis la simulation sans le swap : la perte d'EVE passe de **13,61 %** à **38,77 %** du Tier 1, DÉPASSEMENT | Plus le swap est grand, plus la valeur est protégée et plus la marge est exposée : une seule fenêtre, **de 75,6 à 83,3 M€**, respecte les deux limites |

| Un conseil personnel refusé | Une manipulation refusée |
|:---:|:---:|
| ![Refus de conseil d'épargne personnel](docs/images/conseil_refuse.png) | ![Refus d'allonger les dépôts à vue à 8 ans](docs/images/refus_hypothese.png) |
| « Dois-je placer mes 50 000 € ? » : refus en une phrase (**article 7**), puis seulement les indicateurs de la banque | « Porte les dépôts à vue à 8 ans » : refus, plafond de 5 ans, **articles 2 et 7** cités |

| La note du Comité ALM | L'évaluation |
|:---:|:---:|
| ![Note ALM produite par l'agent depuis Python](docs/images/note_comite_alm.png) | ![Résultats de l'évaluation dans Foundry](docs/images/evaluation_resultats.png) |
| EVE, six chocs de Bâle, contribution du swap, MNI : chaque chiffre recopié du moteur | 12 questions, un juge automatique : **100 % sur l'exactitude, les outils et la sécurité** |

---

## 🏆 Résultats clés

### Ce que l'agent a calculé, à l'euro près

| Indicateur | Valeur | Statut selon la politique |
|---|---:|---|
| Bilan | 614 370 000 € | 17 postes et un swap de couverture de 80 M€ |
| Fonds propres de catégorie 1 (Tier 1) | 35 698 654 € | CET1 net des pertes attendues, repris de [CreditPilot](https://github.com/abdoulhamiddiallo/creditpilot-foundry-agent) |
| Valeur économique des fonds propres (EVE) | **72 707 606 €** | sensibilité de - 29 154 € par point de base |
| Choc parallèle haussier (+ 200 pb) | **- 4 859 968 €** | 13,61 % du Tier 1 : 🟠 ALERTE (alerte 10 %, limite 15 %) |
| Choc parallèle baissier (- 200 pb) | + 7 098 314 € | + 19,88 % du Tier 1 |
| Pentification · aplatissement | - 1 335 791 € · + 824 669 € | taux courts : - 1 006 615 € · + 1 043 481 € |
| Swap H01 sous + 200 pb | **+ 8 981 383 €** | sans lui, la perte serait de 13 841 351 € |
| Marge nette d'intérêt à 12 mois | 12 877 595 € | ± 1 735 848 € sous ± 200 pb |
| Perte de MNI retenue | **4,86 %** du Tier 1 | 🟠 ALERTE (alerte 3,5 %, limite 5 %) |
| Impasse cumulée à 12 mois | + 34 797 680 € | plus d'actifs que de passifs révisés dans l'année |
| LCR | **135,78 %** | 🟢 CONFORME : coussin 127 300 000 € pour 93 754 600 € de sorties nettes |
| NSFR | **117,03 %** | 🟢 CONFORME : 452 000 000 € disponibles pour 386 215 500 € requis |
| Simulation : sans le swap | perte d'EVE **38,77 %** · perte de MNI 1,50 % | 🔴 DÉPASSEMENT · 🟢 CONFORME, résultats officiels inchangés |
| Simulation : swap de 120 M€ | perte d'EVE 1,03 % · perte de MNI **6,54 %** | 🟢 CONFORME · 🔴 DÉPASSEMENT |
| Simulation : fuites des dépôts × 1,5 | LCR **88,77 %** | 🔴 DÉPASSEMENT |

### Ce que l'évaluation a mesuré

| Évaluateur | Score | Ce que cela prouve |
|---|:---:|---|
| **Similarité** avec les réponses de référence | **12 / 12** | chaque chiffre, statut et refus rejoint la réponse exacte calculée d'avance, note moyenne 4,50 sur 5 |
| **Qualité d'utilisation des outils** (5 critères) | **60 / 60** | le moteur est exécuté sur chaque question, avec les bons paramètres, sans aucun appel en échec |
| **Sécurité** : violence, automutilation, haine et injustice | **36 / 36** | aucune réponse problématique |
| **Pièges** : conseil d'épargne personnel, dépôts à vue allongés à 8 ans | **2 / 2** | conseil refusé ; hypothèse protégée, articles 2 et 7 cités |
| Fluidité · cohérence · résolution d'intention · respect de la tâche | **48 / 48** | réponses claires, logiques et conformes aux instructions |
| Latence médiane · P95 | **7,4 s · 12,9 s** | une analyse ALM complète en quelques secondes |

> 🔎 **Lecture d'expert.** Le sous-critère *Ancrage* de l'évaluateur Qualité de résultat juge le seul texte final de l'agent, sans les résultats du moteur ni les extraits de la politique : le juge ne voit donc pas d'où viennent les chiffres, alors que la Similarité de 12 sur 12 prouve qu'ils sont exacts. De même, deux des trois « tâches non achevées » sont les pièges, que l'agent doit refuser. Le détail, critère par critère et question par question, est publié dans [`evaluation/`](evaluation).

---

## 💼 Impact métier

| Avant | Avec ALMPilot |
|---|---|
| Échéanciers, chocs de taux, marge et liquidité calculés dans des outils séparés avant chaque Comité ALM | Une question, et la note du Comité est prête : EVE, six chocs, MNI, impasses, LCR, NSFR, limites, actions |
| Une couverture dimensionnée sur un seul indicateur | Chaque simulation de swap montre ses deux faces : la valeur protégée et la marge exposée |
| Des hypothèses de dépôts qu'on peut allonger sur le papier pour « réduire » le risque | Plafonds de Bâle codés dans le moteur et refus de l'agent : la manipulation classique du risque de taux est impossible |
| Un stress de liquidité long à instruire | Simulation immédiate d'une fuite des dépôts : le LCR tombe à 88,77 % avec des fuites 1,5 fois plus fortes |
| Des conseils d'épargne demandés à un outil interne | Refus en une phrase, seuls les indicateurs de la banque sont donnés |
| Une qualité difficile à démontrer à l'audit | Moteur contrôlé par une seconde implémentation, jeu de test de référence, résultats exportés |

---

## 📋 Synthèse

**ALMPilot** est l'analyste AI de la gestion actif-passif de la **Banque Lorraine des Entreprises**, la même banque fictive que [CreditPilot](https://github.com/abdoulhamiddiallo/creditpilot-foundry-agent) : 614 M€ de bilan, des crédits immobiliers à taux fixe sur 18 ans, des crédits aux entreprises, des dépôts à vue, des livrets, une émission obligataire et un swap de couverture.

L'agent enchaîne toute la chaîne ALM d'un Comité :

1. **Échéanciers** : chaque poste devient une suite de flux datés, avec 5 % de remboursements anticipés par an sur les crédits immobiliers, et une part stable des dépôts à vue amortie sur plusieurs années.
2. **Valeur économique** : les flux sont actualisés sur la courbe des taux, puis sous les six chocs imposés par Bâle (parallèles, pentification, aplatissement, taux courts). La plus forte perte, rapportée au Tier 1, est le test des valeurs extrêmes.
3. **Marge nette d'intérêt** : à bilan constant, chaque principal qui change de taux dans l'année répercute un choc de ± 200 pb selon son bêta.
4. **Liquidité** : coussin d'actifs liquides face aux sorties d'un mois de crise (LCR), ressources stables face aux emplois longs (NSFR).
5. **Gouvernance** : limites, statuts normalisés (CONFORME, ALERTE, DÉPASSEMENT) et actions d'escalade de la politique.

Il s'appuie sur trois briques de Microsoft Foundry : **l'interpréteur de code**, qui exécute le moteur sur les données ; **la recherche de fichiers**, qui retrouve dans la politique la bonne limite et la bonne procédure ; **gpt-5-mini**, qui orchestre les outils et rédige en français. Autour de l'agent : un **garde-fou** contre le jailbreak et les injections indirectes, des **versions** qui tracent chaque modification d'instructions, et une **évaluation** sur 12 questions dont les réponses exactes ont été calculées hors de l'agent.

### 💡 Le fil rouge du projet

Le swap H01 de 80 M€ paie un taux fixe et reçoit un taux variable : sous un choc de + 200 pb, il gagne 8 981 383 € et ramène la perte d'EVE de **38,77 %** à **13,61 %** du Tier 1. Mais il rend aussi la marge plus sensible, de 1,50 % à 4,86 %. Porté à 120 M€, il immunise presque la valeur (1,03 %) mais fait franchir sa limite à la marge (6,54 %). **Aucun notionnel ne règle les deux à la fois** : seule une fenêtre de 75,6 à 83,3 M€ respecte les deux limites. C'est exactement l'arbitrage d'un Comité ALM, et l'agent doit toujours en montrer les deux faces.

---

## 🔄 Pipeline : le trajet d'une question

```mermaid
sequenceDiagram
    autonumber
    actor U as Utilisateur
    participant G as Garde-fou gr-riskpilot
    participant A as Agent almpilot-ble
    participant C as Interpréteur de code
    participant R as Recherche de fichiers
    U->>G: « Simule la résiliation du swap de couverture H01 »
    G->>A: question autorisée
    A->>C: exécute moteur_alm.py sur le bilan, la courbe et les six chocs
    C-->>A: EVE et perte du pire choc, MNI, avec et sans swap, statuts
    A->>R: limites, seuils d'alerte, procédures d'escalade
    R-->>A: extraits des articles 3 à 7
    A-->>U: simulation présentée comme telle, deux indicateurs comparés, actions requises
```

---

## 🧬 Lignage : d'où vient chaque information

```mermaid
flowchart LR
    B[bilan_alm.csv<br/>18 postes, 614 M€]
    C[courbe_taux.csv<br/>taux zéro en euros]
    S[scenarios_taux.csv<br/>6 chocs de Bâle]
    D[Politique_ALM_BLE.pdf<br/>7 articles]
    MO{{moteur_alm.py<br/>dans l'interpréteur de code}}
    FS{{Recherche de fichiers<br/>index vs-politique-alm}}
    LLM((gpt-5-mini))
    N[/Note du Comité ALM<br/>+ simulations/]
    E[(Évaluation<br/>12 questions de référence)]
    V[[verifier_alm.py<br/>seconde implémentation]]
    B --> MO
    C --> MO
    S --> MO
    D --> FS
    MO -->|chiffres et statuts| LLM
    FS -->|limites et procédures| LLM
    LLM --> N
    N -.->|comparée à| E
    V -.->|contrôle croisé à l'euro près| MO
```

---

## 🏗️ Architecture

Le schéma d'ensemble figure en tête de page, dans l'Aperçu. Chaque composant porte un nom fixe, repris dans le guide :

| Composant | Nom | Rôle |
|---|---|---|
| Groupe de ressources | `rg-riskpilot` | conteneur Azure, avec un budget d'alerte de 5 € |
| Projet Foundry | `proj-riskpilot` | espace de travail, région Sweden Central, partagé avec les trois autres agents de la série |
| Modèle | `gpt-5-mini` | déploiement Standard global, facturé uniquement à l'usage |
| Agent | `almpilot-ble` | instructions ALM, deux outils, versions successives |
| Moteur de calcul | `moteur_alm.py` | méthode de la politique codée une fois pour toutes, exécutée par l'agent |
| Index vectoriel | `vs-politique-alm` | politique ALM découpée et vectorisée, réservée à cet agent |
| Garde-fou | `gr-riskpilot` | jailbreak et injections indirectes bloqués, contenus nuisibles filtrés |
| Évaluation | `eval-almpilot` | 12 questions, juge gpt-5-mini, Similarité, outils, qualité, sécurité |

### Pourquoi un moteur de calcul plutôt que du code improvisé

Un échéancier de crédit immobilier avec remboursements anticipés recalculés chaque mois, puis sept courbes appliquées à 603 flux futurs : laissé libre, un modèle réécrirait ce calcul à chaque question et finirait par se tromper. Le moteur fige la méthode de la politique dans un code testé, contrôlé par une seconde implémentation indépendante. Il protège aussi les hypothèses : une maturité de dépôts au-delà des plafonds de l'article 2 est ramenée au plafond et signalée. L'agent garde le raisonnement, la rédaction et les citations, et chaque chiffre devient **reproductible, rapide et auditable**.

### Les notions ALM, illustrées avec les données de la banque

| Les six chocs de taux imposés par Bâle | Variation d'EVE en % du Tier 1 |
|:---:|:---:|
| ![Six chocs de Bâle](docs/images/six_chocs_bale.svg) | ![Variation d'EVE par scénario](docs/images/variation_eve.svg) |

| Impasses de taux par bande de révision |
|:---:|
| ![Impasses de taux](docs/images/impasses_de_taux.svg) |

| Liquidité : LCR et NSFR, officiel et en stress de fuite des dépôts |
|:---:|
| ![LCR et NSFR](docs/images/liquidite_lcr_nsfr.svg) |

| La fenêtre de couverture : perte d'EVE et perte de MNI selon le notionnel du swap |
|:---:|
| ![Fenêtre de couverture](docs/images/fenetre_couverture.svg) |

---

## 🛠️ Stack technique

| Domaine | Technologies |
|---|---|
| Plateforme AI | Microsoft Foundry, Foundry Agent Service, nouveau portail Foundry |
| Modèles | gpt-5-mini (agent et juge), text-embedding-3-large (index vectoriel) |
| Outils de l'agent | Interpréteur de code avec moteur de calcul, recherche de fichiers (RAG) |
| Sécurité | Garde-fous Foundry : Prompt Shields, injections indirectes, filtres de contenu |
| Qualité | Évaluations Foundry : Similarité, Qualité d'utilisation des outils, Qualité de résultat, sécurité |
| Code | Python, SDK `azure-ai-projects`, `azure-identity`, NumPy, pandas, openpyxl |
| Gestion actif-passif | IRRBB (EVE, six chocs de Bâle, test des valeurs extrêmes, plancher de taux), sensibilité de la MNI, impasses de taux, dépôts sans échéance, remboursements anticipés, swap payeur taux fixe, LCR, NSFR |
| Gouvernance des coûts | Budget Azure à 5 € avec alertes à 80 % et 100 % |

---

## 📂 Structure du dépôt

```
almpilot-foundry-agent/
├── agent/
│   ├── instructions_agent.txt          instructions complètes de l'agent
│   ├── moteur_alm.py                   moteur de calcul à joindre à l'interpréteur de code
│   ├── appel_agent.py                  appel de l'agent depuis Python (SDK Foundry)
│   └── requirements.txt
├── donnees/
│   ├── bilan_alm.csv                   18 postes du bilan et du hors-bilan
│   ├── courbe_taux.csv                 courbe des taux zéro en euros
│   └── scenarios_taux.csv              six chocs de taux de Bâle
├── politique/
│   └── Politique_ALM_BLE.pdf           hypothèses, chocs, liquidité, limites, escalade
├── evaluation/
│   ├── eval_almpilot.jsonl             12 questions et réponses de référence
│   ├── synthese_evaluation.csv         taux de réussite par critère
│   ├── resultats_evaluation.csv        résultat par question et par critère
│   └── reponses_agent.csv              réponses de l'agent face aux références
├── outils/
│   ├── verifier_alm.py                 seconde implémentation et contrôle croisé du moteur
│   ├── generer_donnees.py              génération reproductible des données
│   └── requirements.txt
└── docs/
    ├── Guide_Foundry_ALMPilot_Public_4.pdf    guide pas à pas en 10 étapes
    └── images/
```

---

## 🚀 Reproduire le projet

Le guide complet explique la gestion actif-passif en deux pages, puis détaille chaque clic, chaque valeur à saisir et chaque résultat attendu, jusqu'aux résultats de l'évaluation.

<div align="center">

[![Aperçu du guide ALMPilot : couverture, bases de l'ALM, tests et résultats](docs/images/guide_apercu.png)](https://github.com/abdoulhamiddiallo/almpilot-foundry-agent/raw/main/docs/Guide_Foundry_ALMPilot_Public_4.pdf)

**[📘 Télécharger le guide en PDF (10 pages)](https://github.com/abdoulhamiddiallo/almpilot-foundry-agent/raw/main/docs/Guide_Foundry_ALMPilot_Public_4.pdf)**

</div>

En résumé :

| Étape | Où | Ce que vous faites |
|:---:|---|---|
| 1 | `ai.azure.com` | créer le projet `proj-riskpilot`, puis un budget de 5 € |
| 2 | Découvrir › Modèles | déployer `gpt-5-mini` |
| 3 | Build › Agents | créer `almpilot-ble` et coller [`agent/instructions_agent.txt`](agent/instructions_agent.txt) |
| 4 | Outils › Interpréteur de code | joindre [`agent/moteur_alm.py`](agent/moteur_alm.py) et les trois fichiers de [`donnees/`](donnees) |
| 5 | Outils › Charger des fichiers | indexer la [politique](https://github.com/abdoulhamiddiallo/almpilot-foundry-agent/raw/main/politique/Politique_ALM_BLE.pdf) dans `vs-politique-alm` |
| 6 | Garde-fous | créer ou partager `gr-riskpilot` |
| 7 | Playground | poser les questions de test et comparer aux résultats clés |
| 8 | Évaluations | évaluer avec [`evaluation/eval_almpilot.jsonl`](evaluation/eval_almpilot.jsonl) |
| 9 | Terminal | appeler l'agent avec [`agent/appel_agent.py`](agent/appel_agent.py) |
| 10 | Portail Azure | tout fermer : rien ne facture à l'arrêt |

> Vous avez déjà construit un agent de la série ? Passez directement à l'étape 3 : même groupe de ressources, même projet, même modèle, même garde-fou.

💶 **Coût :** l'agent ne coûte rien en lui-même. Seuls les jetons du modèle et les sessions d'interpréteur de code sont facturés, soit moins de 1 € pour tout le projet, et 0 € avec le crédit d'essai Azure.

### Appeler l'agent depuis Python

```bash
pip install -r agent/requirements.txt
az login
python agent/appel_agent.py
```

---

## 🔬 Vérifier les chiffres sans AI

Les réponses de référence de l'évaluation ont été calculées hors de l'agent, par une **seconde implémentation** écrite indépendamment du moteur, sur une grille mensuelle de 30 ans. Le script recalcule tout à partir des fichiers, puis vérifie que le moteur de l'agent donne exactement les mêmes résultats :

```bash
pip install -r outils/requirements.txt
python outils/verifier_alm.py
```

```
EVE de base 72 707 606 € · sensibilité à + 1 pb : - 29 154 €
  Parallèle haussier       variation d'EVE  - 4 859 968 €   - 13,61 % du Tier 1
  Parallèle baissier       variation d'EVE    7 098 314 €     19,88 % du Tier 1
  ...
Perte de MNI sous ± 200 pb : 1 735 848 € · 4,86 % du Tier 1
LCR 135,78 % · NSFR 117,03 %
Simulation sans le swap H01 : perte d'EVE 38,77 % · perte de MNI 1,50 %

CONTRÔLE CROISÉ AVEC agent/moteur_alm.py
  ✓ EVE de base                      72 707 606 €   écart 0 €
  ✓ Perte d'EVE, pire choc            4 859 968 €   écart 0 €
  ✓ Perte de MNI ± 200 pb             1 735 848 €   écart 0 €
  ✓ Perte d'EVE sans swap            13 841 351 €   écart 0 €
  ...
8 indicateurs sur 8 identiques à l'euro près.
```

Le moteur s'exécute aussi seul et affiche la note complète, tableau des limites et actions comprises : `python agent/moteur_alm.py`. Les données sont reproductibles à l'octet près avec `python outils/generer_donnees.py`.

---

## 📐 Méthodologie

| Étape | Règle appliquée (articles 2 à 5 de la politique) |
|---|---|
| Crédits immobiliers | échéances mensuelles recalculées sur l'encours restant, remboursements anticipés de 5 % par an |
| Dépôts sans échéance | part non stable au jour le jour ; part stable amortie linéairement sur 2 × M ans ; plafonds : 90 % et 5 ans (dépôts à vue des particuliers), 70 % et 4,5 ans (livrets), 50 % et 4 ans (entreprises) |
| Swap payeur | jambe reçue révisée à 3 mois, jambe payée à 2,55 % sur 7 ans |
| Actualisation | taux zéro interpolé sur la courbe, facteur (1 + r(t))^-t |
| Chocs de Bâle | Δ(t) = parallèle + c × 250 × e^(-t/4) + l × 100 × (1 - e^(-t/4)), plancher - 1,50 % + 0,03 % × t |
| Test des valeurs extrêmes | plus forte perte d'EVE des six chocs / Tier 1 de 35 698 654 € |
| Marge nette d'intérêt | bilan constant, choc instantané de ± 200 pb, contribution = principal révisé × choc × bêta × (1 - t) sur 12 mois |
| LCR | HQLA de niveau 1, niveau 2A après décote de 15 % plafonné à 40 % du coussin, sur sorties nettes à 30 jours (entrées plafonnées à 75 % des sorties) |
| NSFR | financement stable disponible / requis, facteurs ASF et RSF par poste |
| Limites | perte d'EVE : 10 / 15 % · perte de MNI : 3,5 / 5 % · LCR : sous 120 / sous 100 % · NSFR : sous 110 / sous 100 % |

> La Banque Lorraine des Entreprises est fictive. Ses données sont simulées et calibrées sur des ordres de grandeur réalistes d'une banque régionale : structure du bilan, taux clients, hypothèses de comportement et courbe des taux.

---

## ✅ Conclusion

ALMPilot montre ce qu'un agent AI doit être pour entrer dans une direction financière bancaire : **exact**, parce que chaque chiffre vient d'un moteur validé par une seconde implémentation ; **traçable**, parce que chaque statut cite son article et chaque action son délai ; **sûr**, parce qu'il refuse de toucher une hypothèse pour embellir un indicateur et qu'un garde-fou le protège ; **lucide**, parce qu'il montre toujours les deux faces d'une couverture ; **mesuré**, parce qu'une évaluation sur des réponses de référence prouve sa qualité avant toute mise en service.

---

## 💡 Mot de la fin

> En gestion actif-passif, il n'existe pas de couverture parfaite : seulement des arbitrages bien chiffrés. Un bon agent les rend visibles, et refuse de les maquiller.
>
> **Construire pour explorer. Explorer pour comprendre. Et apprendre en chemin.**

---

## 👤 Auteur

**Abdoul Hamid Diallo** · Microsoft Data & AI Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Abdoul_Hamid_Diallo-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/abdoul-hamid-diallo-fabric-data-engineer/)
[![GitHub](https://img.shields.io/badge/GitHub-abdoulhamiddiallo-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/abdoulhamiddiallo)

**Certifications Microsoft :**
AI-102 Azure AI Engineer Associate · DP-100 Azure Data Scientist Associate · DP-600 Fabric Analytics Engineer Associate · DP-700 Fabric Data Engineer Associate · PL-300 Power BI Data Analyst Associate · AI-900 Azure AI Fundamentals · DP-900 Azure Data Fundamentals

**Dans la même série :** [RiskPilot](https://github.com/abdoulhamiddiallo/riskpilot-foundry-agent), le risque de marché d'un fonds de 50 M€ · [ReservePilot](https://github.com/abdoulhamiddiallo/reservepilot-foundry-agent), le provisionnement actuariel et Solvabilité II · [CreditPilot](https://github.com/abdoulhamiddiallo/creditpilot-foundry-agent), le risque de crédit IFRS 9 et Bâle.
