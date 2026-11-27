"""
Étape 2 : vérifier ClinicalTrials.gov avec les autres registres (plateforme ICTRP de l'OMS).

À lancer depuis la racine du dépôt :  python scripts/02_verification_ictrp.py
Entrées : data_brute/ctg-studies.csv (export ClinicalTrials.gov)
          data_brute/ICTRP-Results.xml (export ICTRP, recherche « sickle cell », tous statuts)
Sortie  : data_propre/ictrp_autres_registres.csv (un essai par ligne, avec son classement)

Classement : doublon (déjà dans ClinicalTrials.gov), hors drépanocytose, ou ajout.
Les doublons sont repérés automatiquement (numéro NCT, autre identifiant, titre proche).
Les cas ambigus ont été tranchés à la main : voir le dictionnaire MANUEL.
"""
import re, collections, difflib
import xml.etree.ElementTree as ET
import pandas as pd

df = pd.read_csv("data_brute/ctg-studies.csv")
ncts = set(df["NCT Number"])
tokens = set()
for s in df["Other IDs"].dropna():
    for t in re.split(r"[|;,]", s):
        t = t.strip().lower()
        if len(t) >= 6:
            tokens.add(t)
titres = [(r["NCT Number"], str(r["Study Title"])) for _, r in df.iterrows()]

rows = []
for tr in ET.parse("data_brute/ICTRP-Results.xml").getroot().findall("Trial"):
    d = collections.defaultdict(str)
    for c in tr:
        d[c.tag] = (c.text or "").strip()
    rows.append(d)

AFRIQUE = ["Nigeria","Ghana","Kenya","Uganda","Tanzania","Zambia","Malawi","Zimbabwe","Rwanda","Ethiopia","Cameroon","Congo","Gabon","Angola","Senegal","Mali","Burkina","Benin","Togo","Cote d","Côte d","Ivory","Sierra Leone","Liberia","Guinea","Niger","Chad","Madagascar","Sudan","Egypt","Tunisia","Morocco","Algeria","Libya","South Africa","Mozambique","Gambia","Mauritania","Burundi","Somalia","Namibia","Botswana","Eswatini","Central African","Djibouti","Eritrea","Lesotho","Mauritius","Seychelles","Reunion"]
def pays_africains(c):
    toks = sorted({t.strip() for t in re.split(r"[;,]", c) if t.strip()})
    return [t for t in toks if any(a.lower() in t.lower() for a in AFRIQUE) and "Papua" not in t]

def norm(s): return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()

# Décisions prises à la main, après lecture des titres, promoteurs et dates
MANUEL = {
  # doublons d'essais industriels déjà dans ClinicalTrials.gov
  "CTIS2025-524464-38-00": ("doublon", "NCT06612268 (etavopivat)"),
  "PACTR202209867711506": ("doublon", "NCT04188509 (extension du voxelotor)"),
  "PACTR202108532761448": ("doublon", "NCT05348915 (inclacumab, GBT2104-133)"),
  "PACTR202106511293049": ("doublon", "NCT04935879 (inclacumab, GBT2104-131)"),
  "PACTR202106894720601": ("doublon", "NCT04927247 (inclacumab, GBT2104-132)"),
  "LBCTR2024045330": ("doublon", "NCT04912869 (crovalimab, Crosswalk-a)"),
  "LBCTR2024015480": ("doublon", "essai industriel probable (ACENT 1), non apparié avec certitude"),
  # pas propres à la drépanocytose
  "EUCTR2015-005732-18-FR": ("hors drépanocytose", "anticoagulant chez l'enfant"),
  "EUCTR2011-006322-25-GB": ("hors drépanocytose", "surcharge en fer"),
  "ISRCTN20317241": ("hors drépanocytose", "maladies tropicales de la peau"),
}
for i in ["ISRCTN54312363","ISRCTN80844630","ISRCTN96891086","ISRCTN17054215","ISRCTN15724013",
          "ISRCTN20156345","PACTR201609001789310","PACTR201610001807329","PACTR201702002009193",
          "PACTR201611001864290","PACTR201803003160262","PACTR201812917283565",
          "PACTR202507605302954","TCTR20200227003"]:
    MANUEL[i] = ("ajout", "essai africain absent de ClinicalTrials.gov")

sortie = []
for r in rows:
    if r["Source_Register"] == "ClinicalTrials.gov":
        continue
    texte = " ".join([r["Secondary_ID"], r["web_address"], r["Public_title"], r["Scientific_title"], r["Acronym"]])
    nct = [n for n in re.findall(r"NCT\d{8}", texte) if n in ncts]
    base = re.sub(r"-(GB|FR|DE|ES|NL|BE|IT|GR|SE|DK|PL|CZ|HU|AT|IE|PT|FI|BG|SK|LT|3rd|Outside-EU/EEA)$", "", r["TrialID"])
    ids = [base.lower()] + [t.strip().lower() for t in re.split(r"[;,|]", r["Secondary_ID"]) if len(t.strip()) >= 6]
    classe, raison = "à examiner", ""
    if nct:
        classe, raison = "doublon", "numéro NCT cité : " + nct[0]
    elif any(i in tokens for i in ids):
        classe, raison = "doublon", "autre identifiant identique"
    else:
        meilleur = (0, None)
        for n, t in titres:
            for x in (norm(r["Public_title"]), norm(r["Scientific_title"])):
                if x and difflib.SequenceMatcher(None, x[:150], norm(t)[:150]).quick_ratio() >= 0.8:
                    q = difflib.SequenceMatcher(None, x[:150], norm(t)[:150]).ratio()
                    if q > meilleur[0]:
                        meilleur = (q, n)
        if meilleur[0] >= 0.85:
            classe, raison = "doublon probable", f"titre proche de {meilleur[1]} ({meilleur[0]:.2f})"
    if r["TrialID"] in MANUEL:
        classe, raison = MANUEL[r["TrialID"]]
    afr = pays_africains(r["Countries"])
    sortie.append({"Registre": r["Source_Register"], "Identifiant": r["TrialID"], "Titre": r["Public_title"][:140],
                   "Promoteur": r["Primary_sponsor"][:60], "Pays": r["Countries"], "Pays africains": "; ".join(afr),
                   "Statut": r["Recruitment_Status"], "Classement": classe, "Raison": raison})

t = pd.DataFrame(sortie)
t.to_csv("data_propre/ictrp_autres_registres.csv", index=False, encoding="utf-8-sig")
print("Essais hors ClinicalTrials.gov :", len(t))
a = t[t["Pays africains"] != ""]
print("Dont avec un pays africain :", len(a))
print(a["Classement"].value_counts().to_string())
print("\nAjouts africains (absents de ClinicalTrials.gov) :")
print(a[a["Classement"] == "ajout"][["Registre", "Identifiant", "Pays africains"]].to_string(index=False))

# Essais ClinicalTrials.gov vus par ICTRP mais absents de l'export
ct = {r["TrialID"]: r for r in rows if r["Source_Register"] == "ClinicalTrials.gov"}
manque = [n for n in ct if n not in ncts]
print("\nEssais de ClinicalTrials.gov dans ICTRP mais absents de l'export :", len(manque))
for n in manque:
    print(" ", n, "|", ct[n]["Countries"][:30], "|", ct[n]["Condition"][:40])
