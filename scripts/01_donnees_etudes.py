"""
Étape 1 : reconstruire les données de chaque étude (pays, régions, familles de traitements,
période, statut) à partir de l'export ClinicalTrials.gov, pour le dashboard.

À lancer depuis la racine du dépôt :  python scripts/01_donnees_etudes.py
Entrée : data_brute/ctg-studies.csv   Sortie : data_propre/etudes_dashboard.json
Les totaux affichés doivent correspondre au rapport :
1 215 études, 1 120 avec pays, 120 avec un site en Afrique, 95 en Afrique subsaharienne.
"""
import pandas as pd, re, json, collections
df=pd.read_csv('data_brute/ctg-studies.csv')
corr={"Arthur M. Blank Hospital":"United States","Turkey (Türkiye)":"Turkey"}
def pays(t):
    if pd.isna(t): return []
    out=set()
    for lieu in t.split('|'):
        p=lieu.split(',')[-1].strip()
        out.add(corr.get(p,p))
    return sorted(out)
df['Pays']=df['Locations'].apply(pays)
ajouts={"NCT07719972":"Mozambique","NCT05837871":"Nigeria","NCT03293641":"Kenya"}
df['Pays']=df.apply(lambda r:[ajouts[r['NCT Number']]] if r['NCT Number'] in ajouts else r['Pays'],axis=1)

regions={
 "Afrique subsaharienne":["Angola","Burkina Faso","Cameroon","Côte d’Ivoire","Democratic Republic of the Congo","Gabon","Ghana","Kenya","Malawi","Mali","Mozambique","Nigeria","Reunion","Senegal","Sierra Leone","South Africa","Tanzania","Uganda","Zambia"],
 "Afrique du Nord":["Egypt","Morocco","Sudan","Tunisia"],
 "Moyen-Orient":["Bahrain","Iraq","Israel","Jordan","Kuwait","Lebanon","Oman","Qatar","Saudi Arabia","Turkey","United Arab Emirates"],
 "Europe":["Austria","Belgium","Cyprus","Czechia","Denmark","Finland","France","Germany","Greece","Ireland","Italy","Netherlands","Poland","Portugal","Russia","Spain","Switzerland","United Kingdom"],
 "Amérique du Nord":["Canada","United States"],
 "Caraïbes et Amérique latine":["Argentina","Brazil","Colombia","Dominican Republic","French Guiana","Guadeloupe","Honduras","Jamaica","Martinique","Panama","Puerto Rico","Trinidad and Tobago"],
 "Asie et Océanie":["Australia","Bangladesh","Brunei","China","Hong Kong","India","Japan","Malaysia","Nepal","Pakistan","South Korea","Taiwan","Thailand"],
}
p2r={p:r for r,l in regions.items() for p in l}
missing=[p for l in df['Pays'] for p in l if p not in p2r]; assert not missing, set(missing)
df['Regions']=df['Pays'].apply(lambda l:sorted({p2r[p] for p in l}))

familles={
 "Hydroxyurée":["hydroxyurea","hydroxycarbamide","siklos","droxia","hydrea","xromi"],
 "Nouveaux médicaments ciblés":["voxelotor","gbt440","gbt021601","mitapivat","etavopivat","imr-687","pde9i","crizanlizumab","aes-103","l-glutamine","hqk-1001","inclacumab","pociredir","ica-17043","osivelotor","rivipansel","gmi-1070","crovalimab","hbi-002","glutamine","senicapoc","mst-188"],
 "Greffe de moelle (conditionnement)":["alemtuzumab","sirolimus","fludarabine","cyclophosphamide","busulfan","tacrolimus","thiotepa","melphalan","mycophenolate","cyclosporine","rituximab","abatacept","methotrexate","mesna","pentostatin","thymoglobulin","atg","bortezomib","fk506","campath","anti-thymocyte","siplizumab","azathioprine","rimiducid","apamistamab"],
 "Mobilisation de cellules souches":["plerixafor","motixafortide","filgrastim"],
 "Douleur":["ketamine","morphine","ibuprofen","fentanyl","sufentanil","acetaminophen","midazolam"],
 "Chélation du fer":["deferasirox","deferoxamine","deferiprone"],
 "Vasculaire et cardio-pulmonaire":["citrulline","arginine","l-nmma","nitric oxide","prasugrel","losartan","ticagrelor","aspirin","sildenafil","bosentan","acetylcholine","lexiscan","atorvastatin","simvastatin","defibrotide","isoquercetin","rosuvastatin","tadalafil","riociguat","regadenoson"],
 "Antioxydants, vitamines et suppléments":["n-acetylcysteine","zinc","vitamin d"],
 "Anti-infectieux":["azithromycin"],
 "Placebo / contrôle":["placebo","saline","standard of care","sodium chloride","nacl"],
 "Corticoïdes":["dexamethasone","methylprednisolone"],
}
def classer(nom):
    n=nom.lower()
    for f,m in familles.items():
        if any(x in n for x in m): return f
    return "Autres / à vérifier"
def fam(t):
    if pd.isna(t): return []
    s=set()
    for i in t.split('|'):
        if i.startswith('DRUG:'): s.add(classer(i.replace('DRUG:','').strip()))
    return sorted(s)
df['Familles']=df['Interventions'].apply(fam)

df['Annee']=pd.to_numeric(df['Start Date'].astype(str).str[:4],errors='coerce')
def periode(a):
    if pd.isna(a): return None
    return "Avant 2005" if a<=2004 else "2005-2009" if a<=2009 else "2010-2014" if a<=2014 else "2015-2019" if a<=2019 else "2020 et après"
df['Periode']=df['Annee'].apply(periode)
def gphase(p):
    if p in ["EARLY_PHASE1","PHASE1"]: return "Phase 1"
    if p in ["PHASE1|PHASE2","PHASE2"]: return "Phase 2"
    if p in ["PHASE2|PHASE3","PHASE3","PHASE4"]: return "Phase 3 et 4"
    return "Sans phase"
df['Phase']=df['Phases'].apply(gphase)
def gstatut(s):
    if s=="COMPLETED": return "Terminé"
    if s in ("RECRUITING","ACTIVE_NOT_RECRUITING","NOT_YET_RECRUITING","ENROLLING_BY_INVITATION"): return "En cours ou à venir"
    if s in ("TERMINATED","WITHDRAWN","SUSPENDED"): return "Arrêté ou retiré"
    if s=="UNKNOWN": return "Statut inconnu"
    return "Autre"
df['Statut']=df['Study Status'].apply(gstatut)
fund={"INDUSTRY":"Industrie","NIH":"NIH","OTHER":"Universités et hôpitaux","OTHER_GOV":"Autres organismes publics","NETWORK":"Réseaux"}
df['Financeur']=df['Funder Type'].map(fund).fillna("Autre")
typ={"INTERVENTIONAL":"Interventionnelle","OBSERVATIONAL":"Observationnelle","EXPANDED_ACCESS":"Accès élargi"}
df['Type']=df['Study Type'].map(typ).fillna("Autre")
afr=["Afrique subsaharienne","Afrique du Nord"]
df['Afrique']=df['Regions'].apply(lambda l:any(r in afr for r in l))
df['ASS']=df['Regions'].apply(lambda l:"Afrique subsaharienne" in l)

# --- validations
print('études',len(df),'| avec pays',(df['Pays'].str.len()>0).sum())
print('Afrique',df['Afrique'].sum(),'| ASS',df['ASS'].sum())
print('résultats',(df['Study Results']=='YES').sum(),'| arrêtées/retirées',(df['Statut']=="Arrêté ou retiré").sum())
cf=collections.Counter(f for l in df['Familles'] for f in l); print(cf.most_common())
print('sans médicament',(df['Familles'].str.len()==0).sum(),'| uniquement autres',df['Familles'].apply(lambda l:l==["Autres / à vérifier"]).sum())
print(df['Periode'].value_counts().to_dict(), 'sans date',df['Annee'].isna().sum())
print(df['Phase'].value_counts().to_dict()); print(df['Financeur'].value_counts().to_dict()); print(df['Statut'].value_counts().to_dict())
cr=collections.Counter(r for l in df['Regions'] for r in l); print(cr)
mono=df[df['Regions'].apply(lambda l:len(l)>0 and all(r in afr for r in l))]; print('Afrique seule',len(mono))

rows=[]
for _,r in df.iterrows():
    rows.append({"id":r['NCT Number'],"t":str(r['Study Title'])[:120],"s":r['Statut'],"ss":r['Study Status'],"p":r['Phase'],"f":r['Financeur'],"y":None if pd.isna(r['Annee']) else int(r['Annee']),
      "per":r['Periode'],"type":r['Type'],"res":1 if r['Study Results']=='YES' else 0,"pays":r['Pays'],"reg":r['Regions'],"fam":r['Familles'],
      "afr":1 if r['Afrique'] else 0,"ass":1 if r['ASS'] else 0})
json.dump(rows,open('data_propre/etudes_dashboard.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print('fichier écrit : data_propre/etudes_dashboard.json')
