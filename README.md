# Drépanocytose : où se font les essais cliniques, et pour qui ?

Analyse de 1 215 essais du registre ClinicalTrials.gov, comparés au poids de la maladie dans chaque pays (Global Burden of Disease 2021) et vérifiés avec 15 autres registres (plateforme ICTRP de l'OMS).

**Question** : que montrent les essais sur la drépanocytose qui ont publié leurs résultats, et ces traitements sont-ils testés là où la maladie pèse le plus ?

## Résultats principaux

- L'Afrique subsaharienne compte 73,4 % des personnes qui vivent avec la maladie, mais seulement 8,5 % des essais dont le pays est connu (95 sur 1 120), ou environ 9,5 % avec les autres registres.
- Le Nigeria, l'Inde et la RDC regroupent 58,5 % des malades pour au plus 5,0 % des essais. Les États-Unis comptent 0,77 % des malades et 69,0 % des essais.
- Parmi les 51 essais menés uniquement en Afrique subsaharienne, 59 à 67 % sont pilotés par une organisation hors d'Afrique.
- Aucun essai de greffe ou de thérapie génique n'a de site africain.
- Sur 182 essais arrêtés ou retirés, le manque de patients explique 43 % des cas ; la sécurité 5 % et le manque d'efficacité 4 %.
- Le seul traitement qui réduit les crises dans un essai randomisé de phase 3 est la L-glutamine ; l'hydroxyurée est le seul traitement de fond dont le bénéfice est documenté en Afrique (essai REACH, sans groupe de comparaison).

## Contenu du dépôt

| Dossier ou fichier | Rôle |
| --- | --- |
| `notebooks/01_exploration.ipynb` | Nettoyage et analyse (pays, régions, familles de traitements, motifs d'arrêt, critères, effets graves) |
| `scripts/01_donnees_etudes.py` | Reconstruit les données de chaque étude pour le dashboard |
| `scripts/02_verification_ictrp.py` | Vérifie ClinicalTrials.gov avec les autres registres et classe chaque essai (doublon, hors sujet, ajout) |
| `data_propre/` | Données nettoyées au format JSON ou CSV |
| `data_brute/` | Données d'origine (non modifiées) |

## Reproduire l'analyse

1. Installer Python 3.10 ou plus, puis `pip install pandas ipykernel`.
2. Placer dans `data_brute/` :
   - `ctg-studies.csv` : export de ClinicalTrials.gov (recherche « Sickle Cell Disease », tous les champs, 28 octobre 2026) ;
   - `ICTRP-Results.xml` : export de la plateforme ICTRP (recherche « sickle cell », statut « All », 29 octobre 2026).
3. Depuis la racine du dépôt : `python scripts/01_donnees_etudes.py`, puis `python scripts/02_verification_ictrp.py`. Les totaux affichés doivent correspondre à ceux du rapport.

Les données du Global Burden of Disease ne sont pas dans ce dépôt : elles se téléchargent sur ghdx.healthdata.org (« Sickle Cell Disease Birth Incidence, Prevalence, and Mortality 2000-2021 »), selon les conditions d'utilisation de l'IHME.

## Limites

- Le registre principal est ClinicalTrials.gov ; la vérification avec les autres registres ajoute au plus 17 essais, mais des essais africains peuvent n'être enregistrés nulle part.
- Les résultats sont déclarés par les promoteurs, sans vérification, et seuls 21 % des essais en ont publié.
- 95 essais n'ont aucun pays : les comptages africains sont des minimums. Un site cité ne prouve pas que des patients y aient été inclus.
- Les chiffres du GBD sont des estimations modélisées, avec une forte incertitude.
- Les familles de traitements et les motifs d'arrêt sont classés par mots-clés : c'est un choix d'analyste.

## Sources et crédits

- ClinicalTrials.gov : données publiques, export du 28 octobre 2026.
- Plateforme ICTRP de l'Organisation mondiale de la santé : export du 29 octobre 2026.
- Global Burden of Disease Collaborative Network. *Global Burden of Disease Study 2021 (GBD 2021) Sickle Cell Disease Birth Incidence, Prevalence, and Mortality 2000-2021*. Seattle : Institute for Health Metrics and Evaluation (IHME), 2023.
- Tshilolo L et al. Hydroxyurea for Children with Sickle Cell Anemia in Sub-Saharan Africa. *N Engl J Med* 2019 ; 380:121-131.

## Auteure

Maeva Ozouaki · Maeva DataVision
Rapport complet : https://ubiquitous-pizza-8c9.notion.site/Drepanocytose-o-se-font-les-essais-cliniques-et-pour-qui-3bca892fd53f80219887db2336d05eac · Dashboard : https://drepanocytosedashboard.netlify.app/
