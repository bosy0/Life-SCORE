'''
                        [NOTATION.PY]
                         
         Programme qui répertorie toutes nos classes
                      et nos fonctions



- CLASSE "Donnees" : traitement des données pour le programmme :
     . Traitement des données (transformer les infos d'uun csv en note) par Nathan
     . Savoir si la commune est française par Raphaël
     . Note finale par Raphaël et Nathan
     
- "est_connecte" : vérifie si l'utilisateur a accès à internet / au site demandé, fait par Nathan

- Fonctions pour lire/écrire/initialiser les paramètres, fait par Thor

- Fonction pour calculer une fonction affine & sigmoïdales, fait par Nathan

'''





'''
BIBLIOTHEQUES
 
'''
# Bibliothèques souvent utilisées :
import requests                        # Demandes de connexion
from tkinter import *                  # Interface utilisateur
import os                              # Interaction avec le système
import random                          # Pour un petit easter egg
import re                              # pour les splits

# Bibliothèque pour l'utilisation des CSV :
import pandas as p    # Lecture des csv

#* Fix pour une erreur avec pandas.read_csv(), il n'y a pas d'explication pourquoi ça marche
#* Source : https://stackoverflow.com/questions/44629631/while-using-pandas-got-error-urlopen-error-ssl-certificate-verify-failed-cert
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Bibliothèques pour éviter erreurs de coupure réseau :
from requests.exceptions import ConnectionError, ReadTimeout

# Pour la fonction sigmoïde
import math





'''
OUVERTURE DE LA BASE DE DONNEES

'''
global infos_csv

import json # Pour la lecture des données csv
nom_du_repertoire = os.path.dirname(__file__)
with open(os.path.join(nom_du_repertoire, "systeme/base_de_donnees.json"), "r",encoding="utf-8") as fichier_json :
    infos_csv = json.load(fichier_json)





'''
SAVOIR S'IL Y A UNE CONNEXION INTERNET
(avec qu'un seul essai pour éviter les bugs)

Fait par Nathan d'après un ancien projet (v.4 de l'application)
'''
def est_connecte(url) :
    
    try :
        requests.get(url, timeout=5)
              
                
    except ConnectionError or ReadTimeout or TimeoutError :    
                
        return False 
        
    return True





"""
FONCTIONS UTILE DANS TOUTE L'APPLICATION

Fait par Thor

"""
def distanceEuclidienne(point1: tuple[float, float],point2: tuple[float, float]) -> float: # utilisé pour la fonction kppv()
    """Renvoie la distance entre deux points donnees.
    
    Fonction de Thor fait en classe
    """ 
    assert type(point1) in (list, tuple) and type(point2) in (list, tuple) # peut n'import si list ou tuple, mais tuple est mieux

    distEucli = (point2[0] - point1[0])**2 + (point2[1] - point1[1])**2 # calcule de distance au carré
    return distEucli**0.5 # renvoi cette distance avec racine carré appliqué


def kppv(donnees: dict,
         point: tuple[float, float],
         k: int
    ) -> list:
    """
    Trouve les k plus proches voisins.

    `donnees`: une dico de points de coordonees (x,y) avec en clé le nom des villes
    `point`: un seul point de coordonees (x,y) (peut contenir int ou float)
    `k`: les k plus proches voisins de la liste `donnees` au point `point`.

    La fonction renvoie une liste des indices pour `donnees` contenant les `k` plus proches voisins a `point`

    Fonction de Thor fait en classe 
    """
    # on verifie les conditions necessaires pour les parametres
    assert type(k) == int
    assert type(point) == tuple
    assert type(donnees) == dict

    distVoisins = [] # contient la distance du point `point` au point dans `donnees`` avec leur indices correspondants
    for cle in donnees.keys():   
        distance = distanceEuclidienne(point, (donnees[cle][0],donnees[cle][1])) # calcul de la distance
        distVoisins.append((distance,cle,donnees[cle][2])) # ajoute au liste de points avec distance

    distVoisins = sorted(distVoisins) # on trie la liste par leurs distances d'ordre croissant
    indicesDesKvoisins = [(cle,insee) for distance, cle, insee in distVoisins[:k]] # on prend les indices des k premiers points de cette liste de distances
    return indicesDesKvoisins

# system de calcule de note par distance
def calcul_note_ideale(dict_valeursIdeales :dict, dict_valeursSaisies: dict) -> dict:
    '''
    Calcule les notes de tout les differents valeurs par rapport a leurs valeur ideal/preferable

    La structure du dictionaire `dict_valeursIdeales` doit etre: `{critere: (valeurMinimal, valeursIdeal, valeurMaximal)}`

    Et la structure du dictionaire `dict_valeursSaisies` doit etre: `{critere: valeur}`

    Renvoi un dictoinaire de type `{critere: note}`

    - `dict_valeursIdeales` et `dict_valeursSaisies` doivent avoir les memes noms de clefs.
    - Un critere de `dict_valeursIdeales` ne peut pas avoir 3 valeurs identiques. Mais il peut en avoir 2 si l'ideal est soit le Minimum ou le Maximum.
    
    ---

    - Idée de Thor : L'idée s'apparente à celle du calcul du pourcentage d'une pente sauf qu'ici on cherche l'écart 
                    de la valeur en fonction de la longueur d'étude de ces valeurs
    '''
    assert type(dict_valeursIdeales) == type(dict_valeursIdeales) == dict, "Les valeurs saisit doivent etre dans des dictionaires."
    
    dict_notes = {}

    for critere in dict_valeursSaisies.keys(): # pour chaque critere dont on a un valeur desiré
        # recupere les donnees pour ce critere
        valMin, valIdeal, valMax = dict_valeursIdeales[critere]
        valSaisit = dict_valeursSaisies[critere]

        assert len(set((valMin, valIdeal, valMax))) != 1, f"Les valeurs ideales de `{critere}` ne peuvent pas etre 3 valeurs identiques (Mais ils peuvent en etre 2)."
        assert valMin <= valIdeal <= valMax, f"Les valeurs ideales et limites de `{critere}` ne sont pas en ordre croissant."
        

        if valSaisit == valIdeal: # si on a la valeur exacte que l'on recherche
            noteSurCent = 1

        elif valMin <= valSaisit <= valMax: # si la valeur locale est entre les limites données

            # on cherche la domain de valSaisit, donc si il est inferieur ou superieur a valIdeal
            domainDuValeur = valMin if valSaisit <= valIdeal else valMax   
            longeurDuDomain = abs(valIdeal - domainDuValeur) # "longeur" du domaine ou se trouve valSaisit

            distanceDesValeurs = abs(valIdeal - valSaisit) # difference entre valSaisit et valIdeal
            noteSurCent = 1 - (distanceDesValeurs/longeurDuDomain) # calcule un note par rapport a cette difference et la longeur du domain

        else: # si la valeur est en-dehors des limites, on ne l'accepte pas
            noteSurCent = 0


        dict_notes[critere] = round(noteSurCent*100, 4) # ajoute le note au dictionaire de notes (et les multiplie par 100 pour un pourcentage)

    return dict_notes # renvoi la dictionaire avec tout les notes


# Vérifier si le fichier options est présent
def est_un_fichier(chemin : str = "donnees/options.txt") :
    """
    Fonction qui vérifie si le fichier options.txt existe pour eviter des erreurs avec les autres fontions options
    - Idée + Implémentation par Nathan
    """
    path_options = os.path.join(os.path.dirname(__file__),chemin) # localise le fichier cible
    if not os.path.isfile(path_options) : # on verifie si ce fichier n'existe pas
        dict_def = {} # données intial qu'on ecrira au fichier

        if chemin == "donnees/options.txt":
            dict_def = {'APPARENCE': 'System', # les options defaut qu'on veut
                    'FREQ_MAJ': 0,
                    'DERNIERE_MAJ': 0,
                    "REPONSE_QCM": {}}
        open(path_options, "w").write(str(dict_def)) # on ecrit les données initials au fichier


# Modifier un option/dico
def modifier_fichier_dico(cle: any, valeur: any, fichier:str = "donnees/options.txt", msg=None):
    """Modifie la valeur d'une valeur donnée dans un fichier contenant un string format dictionaire python.

    - Par default on modifie le fichier options, sauf si on donne un fichier en parametre.
    - Ce fonction action sur tout les repertoires enfants de /Life-SCORE/code/ 

    - Idée et Implémentation par Thor
    """
    assert type(cle) not in (list, dict), "Le clé doit pas etre un type mutible" 
    assert type(fichier) == str, "Le chemin pour le fichier doit etre un string" 

    if fichier[0] == "/": # pour eviter un bug avec os.path.join()
        fichier = fichier[1:]
    path_options = os.path.join(os.path.dirname(__file__), fichier)

    est_un_fichier(fichier) # creation de donnees initial si fichier vide

    if msg != None:
        msg.configure(text = "Modification effectuée !")      # Si un message est renseigné

    dictionaire_options = eval(open(path_options,"r").read()) # on recupere d'abord le dico
    dictionaire_options[cle] = valeur                         # on change la valeur dans le dico
    open(path_options, "w").write(str(dictionaire_options))   # on re-ecrit le dico au fichier


# Récupérer une option/dico du fichier
def lire_fichier_dico(cle: any = None, fichier: str = "donnees/options.txt"):
    """Renvoie la valeur d'un clef donné d'un fichier (options par defaut). 

    - Recuper par default des donnes du fichier options, sauf si on donne un fichier en parametre.
    - Ce fonction action sur tout les repertoires enfants de /Life-SCORE/code/

    - Idée et Implémentation par Thor
    """
    assert type(fichier) == str, "Le chemin pour le fichier doit etre un string" 
    assert type(cle) not in (list, dict), "Le clé doit pas etre un type mutible"
    
    if fichier[0] == "/": # pour eviter un bug avec os.path.join()
        fichier = fichier[1:]
        
    est_un_fichier(fichier) # creation de donnees initial si fichier vide

    path_options = os.path.join(os.path.dirname(__file__), fichier)
    if cle != None :
        return eval(open(path_options, "r").read()).get(cle)   # on ouvre et recupere l'option qu'on veut
    else: # Si on veut le fichier entier
        return eval(open(path_options,"r",encoding = 'utf-8').read())
    
    
# Renvoie uniquement les nombres
def est_nombre(num: str) -> bool:
    """Verifie si l'entrée est un nombre
    - Code de Thor
    """
    assert type(num) == str, "L'argument entré doit etre un string"

    try:
        float(num) # on utilise float() pour accepter les "." dans un nombre decimale
        return True
    except:
        return False





'''
Pour calculer une fonction à l'aide de deux points

Idée et réalisation de Nathan

'''
def calculer_fonction_affine(moyenne, max, x) : # Deux points correspondant à la moyenne (50) et le maximum (100)
    if x == 0 :
       return 0
   
    m = (max - 1.4*moyenne) / 50                # On calcule le coef directeur
    p = moyenne - (m*50)                        # On calcule l'ordonnée à l'oginine
   
    return (x-p)/m                              # On renvoie la note

def calculer_fonction_sigmoide(moyenne, maximum, x) : # Deux points correspondant à la moyenne (50) et le maximum (100)
    '''
    Ici on utilise une fonction sigmoïde (en forme de S) pour accentuer les notations :
    
    Souvent les villes sont proches de la moyenne nationnale, pour éviter d'avoir des notes trop homogène on
    accentue le résultat avec ceci.
    
    '''
    if x == 0 :
       return 0
    difference = maximum - moyenne           # On calcule la différence entre le max et la moyenne
    coefficient = (x - moyenne) / difference # On fait un coeficient pour savoir où est situé le résultat par rapport aux moyennes
    rep = coefficient*100
    rep = 100/(1+math.exp(-0.08*rep))        # On utilise la fonction Sigmoïde
    return rep

def fonction_sigmoide(x):
    if x == 0 :
       return 0
    return 100/(1+math.exp(-0.08*(x-50)))
    



'''
CLASSE PRINCIPALE

'''  
class Donnees:
    def __init__(self, commune, insee=None) :
        
        self.commune = str(commune)
        self.repertoire = os.path.dirname(__file__)
        self.liste_notes = [] # La liste dans laquelle on rempli les notes 
        self.habitants = None
        self.population = 0
        
        self.notes_finales = {}

        if insee != None: # Pour les 10 villes plus proches
            self.code_insee = insee

    dico_meteo = {} # Variable qui peut etre accédée et modifée par toutes les instances de la classe





    '''
    METHODE QUI RECUPERE AUTOMATIQUEMENT LES DONNEES D'UN CSV (simple)
    
    Pensé et réalisé par Nathan
    
    '''
    def recup_donnees_simple(self, csv, recursivite=False, ancien_nom_ville='') :
        
        # On récupère le répertoire pour accéder au csv
        lien_fichier = os.path.join(os.path.dirname(__file__),'donnees')+'/csv/'+csv+'.csv'
        
        # On récupère les infos des données qu'on voudrait récupérer
        colonnes = [infos_csv[csv][2]['colonne_ville']]
        for i in range(len(infos_csv[csv][2]['colonne_donnee'])) :
            colonnes.append(infos_csv[csv][2]['colonne_donnee'][i])
        # On va lire le fichier
        fichier = p.read_csv(lien_fichier,
                            delimiter=infos_csv[csv][2]['delimiteur'],
                            usecols=colonnes,
                            encoding='utf-8',
                            low_memory=False)
        
        liste_provisoire = []
        for a in fichier.columns:
            liste_provisoire.append(str(a))
        
        # On trouve la rangée qui valide le code insee
        #liste[0] est présumé la case avec le code insee
        
        # Si le CSV utilise le code INSEE
        if infos_csv[csv][2]['insee'] == 1 :
            rangee = fichier[fichier[liste_provisoire[0]] == self.code_insee]
        # Si le CSV n'a pas de code INSEE (on regarde le nom de la ville)
        else :
            rangee = fichier[fichier[liste_provisoire[0]] == self.commune]
            
        if recursivite :
            self.commune = ancien_nom_ville
            
        try:
            resultat = []
            for i in range(len(infos_csv[csv][2]['colonne_donnee'])) :
                resultat.append(rangee.values[0][i+1])
            return resultat
            
        # Au cas où il n'y a pas de données
        except : #Si pas de données
    
            if recursivite:
                self.commune = ancien_nom_ville
               
            elif infos_csv[csv][2]['insee'] == 0 :
        
                ancien_nom = self.commune
                self.commune = re.split(" ",self.commune)[0]
                self.recup_donnees_simple(csv, True, ancien_nom)
            
            return None

        
            
            
            
    '''
    METHODE QUI RECUPERE AUTOMATIQUEMENT LES DONNEES D'UN CSV (en comptant le nombre d'éléments)
    
    Pensé et réalisé par Nathan, basé par la fonction recup_donnees_simple
    
    '''
    def recup_donnees_compter_par_habitant(self, csv, recursivite=False, ancien_nom_ville=''):
        
        try:
            
            # Ici c'est tout comme la fonction au dessus
            lien_fichier = os.path.join(os.path.dirname(__file__),'donnees/csv/'+csv+".csv")
            
            colonnes = [infos_csv[csv][2]['colonne_ville']]
            for i in range(len(infos_csv[csv][2]['colonne_donnee'])) :
                colonnes.append(infos_csv[csv][2]['colonne_donnee'][i])
            
            fichier = p.read_csv(lien_fichier,
                                delimiter=infos_csv[csv][2]['delimiteur'],
                                usecols=colonnes,
                                encoding='utf-8',
                                low_memory=False)
            
            liste_provisoire = []
            for a in fichier.columns:
                liste_provisoire.append(str(a))

            # Si le CSV utilise le code INSEE
            if infos_csv[csv][2]['insee'] == 1 :
                res = fichier[fichier[liste_provisoire[0]] == self.code_insee] 
            # Si le CSV n'a pas de code INSEE (on regarde le nom de la ville)
            else :
                res = fichier[fichier[liste_provisoire[0]] == self.commune]
            
            if recursivite :
                self.commune = ancien_nom_ville
            
            
            # Là on récupère seulement le nombre de lignes qui restent pour compter les éléments
            df = p.DataFrame(res)
            rep = len(df)
            
            # Extention pour les CSV de type oui_non
            if infos_csv[csv][2]['type'] == 'oui_non':
                if rep > 0 :
                    return 100
                else:
                    return 0
            
            
            
            # On récupère les habitants si c'est pas déjà fait, basé sur mon autre fonction recup_donnees_par_population
            if self.habitants is None :
                self.habitant = int(self.recup_donnees_simple('population')[0])
            
            # On divise si un CSV repertorie plusieurs années
            diviseur = infos_csv[csv][2].get('diviseur')
            if diviseur != None :
                rep = rep / diviseur
                
            
            note = rep / self.habitant

            
            #On récupère directement la note en utilisant la fonction affine
            a = infos_csv[csv][2]['moyenne']
            b = infos_csv[csv][2]['max']   
            return calculer_fonction_sigmoide(a, b, note)
                
        except : #Si pas de données
            
            if recursivite :
                self.commune = ancien_nom_ville
               
            elif infos_csv[csv][2]['insee'] == 0 :
        
                ancien_nom = self.commune
                self.commune = re.split(" ", self.commune)[0]
                self.recup_donnees_compter_par_habitant(csv, True, ancien_nom)
                

            return 0





    '''
    METHODE QUI RECUPERE AUTOMATIQUEMENT LES DONNEES D'UN CSV (par habaitant)
    
    Pensé et réalisé par Nathan
    
    '''
    def recup_donnees_par_population(self, csv) :
        
        if self.habitants is None :
            self.habitant = int(self.recuperation_donnees('population')[0])
        
        # On utilise recup_donnees_simple pour éviter de faire la même chose dans un autre endroit
        nombre = self.recup_donnees_simple(csv)
        
        try :
            nombre = int(nombre[0])
            if nombre is None :
                nombre = 0
        except :
            return None
        
        # On divise par le nombre d'habitants et on utilise la fonction affine
        note = nombre / self.habitant
        # On récupère directement la note
        a = infos_csv[csv][2]['moyenne']
        b = infos_csv[csv][2]['max']
        
        return calculer_fonction_sigmoide(a, b, note)
        
        
        


    '''
    METHODE QUI RECUPERE AUTOMATIQUEMENT LES DONNEES D'UN CSV (simple juste en utilisant l'affine)
    
    Pensé et réalisé par Nathan, basé par la fonction recup_donnees_simple et recup_donnees_population
    
    '''
    def recup_donnees_simple_sigmoide(self, csv):
    
        try :
            nombre = self.recup_donnees_simple(csv)
            moyenne = infos_csv[csv][2]['moyenne']
            maximum = infos_csv[csv][2]['max']
            
            nombre = int(str(nombre[0]).split(',')[0])
            return calculer_fonction_sigmoide(moyenne, maximum, nombre)
        
        except :
            return None





    '''
    METHODE QUI RECUPERE AUTOMATIQUEMENT LES DONNEES D'UN CSV
    
    HUB où on fait le pont entre les autres fonctions par rapport au type de CSV 
    Pensé et réalisé par Nathan
    
    '''
    def recuperation_donnees(self, csv) :
        type_recuperation = infos_csv[csv][2]['type']
        
        if type_recuperation == 'simple' :
            return self.recup_donnees_simple(csv)
        
        elif type_recuperation  == 'par_population' :
            return self.recup_donnees_par_population(csv)
        
        elif type_recuperation == 'compter_par_population' or type_recuperation == 'oui_non':
            return self.recup_donnees_compter_par_habitant(csv)
        
        elif type_recuperation == 'simple_affine' :
            return self.recup_donnees_simple_sigmoide(csv)
        


        
        
        
    """
    VERIFIE SI LA COMMUNE EST FRANCAISE ET DONNE SON CODE INSEE
    
    Fait par Raphaël
    
    """
    def est_commune_france(self,msg):

        if str(self.commune) == '':
            msg.configure(text = "Veuillez saisir le nom d'une commune :") 
            return False


        self.commune = self.commune.strip() # Enlève les espaces en trop
        
        
        temp = str(self.commune).upper()
        if temp in ['PARIS','MARSEILLE','LYON']:
            msg.configure(text = "Pour les villes possédant des arrondissements,\nréférez vous à l'aide (bouton en haut à droite).")
            return False
            
        if "-" in self.commune or ' ' in self.commune:
            liste_ville = re.split("-| ",self.commune)# Sépare avec espace, - et '
            for i in range(len(liste_ville)):
                if liste_ville[i] not in ['lès','l','d','en','de','des','les','à']:
                    if liste_ville[i][:2] in ["d'","l'"] : # Si on a "d'hérault"
                        liste_ville[i] = liste_ville[i][:2] + liste_ville[i][2].upper() + liste_ville[i][3:]
                    else: 
                        liste_ville[i] = liste_ville[i].capitalize()
            self.commune = " ".join(liste_ville)

        fichier = open(self.repertoire + '/donnees/csv/communes.csv',"r",encoding='utf-8')
        cr = p.read_csv(fichier,delimiter=",",usecols=['NCC','NCCENR','LIBELLE','COM'],encoding='utf-8',low_memory=False) # Encoding pour pouvoir avoir les accents 

        fichier.close()

        # Recup ligne de ville pour code insee
        row = cr[(cr['NCCENR'] == str(self.commune)) | (cr['LIBELLE'] == str(self.commune)) | (cr['NCC'] == str(self.commune).upper())]
        if not row.empty:
            self.code_insee = row.values[0][0]
            self.commune = row.values[0][3]
            
            with open(self.repertoire + '/donnees/csv/population.csv',"r") as fichier : 
                infos = p.read_csv(fichier,delimiter=",",usecols=['com_code','popleg_tot'],encoding='utf-8',low_memory=False)
                rangee = infos[infos['com_code'] == self.code_insee]

            if not rangee.empty :
                self.population = int(rangee.values[0][1])
                
            else:
                msg.configure(text = "Nous n'avons pas de données sur cette ville.")
                return False
            
            return True
        
        else:
            self.commune = self.commune.strip('-')        
            liste = list(self.commune)
            dico_carac_spéciaux = {"é":"e", "è":"e", "ê":"e", "ë":"e", "û":"u", "à":"a", "â":"a", "ÿ":"y", "ï":"i", 
                                    "î":"i", "ô":"o","-":" ","'":" "}
            # Remplacer les accents par leur lettres (pas ouf mais marche)
            for i in range(len(liste)):
                if liste[i] in dico_carac_spéciaux:
                    liste[i] = dico_carac_spéciaux[liste[i]]
            self.commune = ''.join(liste) #Redonne la ville sans accents
            row = cr[(cr['NCC'] == str(self.commune).upper())] 

            if not row.empty:
                self.code_insee = row.values[0][0]
                self.commune = row.values[0][3]
                
                with open(self.repertoire + '/donnees/csv/population.csv',"r") as fichier : 
                    infos = p.read_csv(fichier,delimiter=",",usecols=['com_code','popleg_tot'],encoding='utf-8',low_memory=False)
                    rangee = infos[infos['com_code'] == self.code_insee]

                if not rangee.empty :
                    self.population = int(rangee.values[0][1])
                    
                else:
                    msg.configure(text = "Nous n'avons pas de données sur cette ville.")
                    return False
                return True
            else :
                # EASTER EGG
                if self.commune == "Hello There" :
                    msg.configure(text = "General Kenobi !")
                elif random.randint(0,100000) == 14924:
                    msg.configure(text = "Gustavo Fring n'autorise pas la sortie d'information sur cette ville.")
                else :
                    msg.configure(text = "Ville incorrecte, veuillez réessayer.")
                return False
        
        
        
    def k_plus_proches_voisins(self,k,msg=None,win=None):
        '''
        Fonction qui récupère toutes les villes du département 
        avec leurs coordonnées et trouve les k plus proches

        idee du cours sur les k plus proches voisins de Thor et Raphaël
        '''
        fichier = open(self.repertoire + '/donnees/csv/coordonnees.csv',"r",encoding='utf-8')
        cr = p.read_csv(fichier,delimiter=",",usecols=['latitude','longitude','nom_commune_complet','code_commune_INSEE'],encoding='utf-8',low_memory=False)
        fichier.close()
        
        rangee_unique = cr[(cr['code_commune_INSEE'] == self.code_insee) | (cr['code_commune_INSEE'] == self.code_insee[1:])]
        if len(rangee_unique) > 1: # Gère le cas où on récupère par exemple la ville de code 34459 et 4459

            if self.code_insee[0] == '0':
                rangee_unique = rangee_unique.iloc[0]
            else:
                rangee_unique = rangee_unique.iloc[-1]
        coordonnees0 = (float(rangee_unique['latitude']),float(rangee_unique['longitude']))

                       

        # On prend ceux compris entre par exemple 34000 et 34999 
        row = cr[(cr['code_commune_INSEE'] >= self.code_insee[:-3]+'000') &
                ( cr['code_commune_INSEE'] <= self.code_insee[:-3]+'999') &
                ( cr['code_commune_INSEE'] != str(self.code_insee))]
        
        
        dico = {}
        for index, r in row.iterrows():
            dico[r['nom_commune_complet']] = (r['latitude'],r['longitude'],r['code_commune_INSEE'])
        # Partie k plus proches voisins
        liste_k_proches = kppv(dico,coordonnees0,k)
        liste_notes = []
        
        dico_fichier_tempo = lire_fichier_dico(fichier = "donnees/cache.txt")

        for nom,insee in liste_k_proches:
            if msg != None:
                msg.configure(text = f'Calcul de {nom}...')
                win.update()
            if nom in dico_fichier_tempo : # Si on a déjà récupéré ces données là
                liste_notes.append((nom,dico_fichier_tempo[nom]))
            else:
                ville = Donnees(nom,insee)
                note = ville.note_finale(meteo = False)
                liste_notes.append((nom,note))
                dico_fichier_tempo[nom] = note

        # On écrit tout ça dans le fichier temporaire de données
        with open(os.path.join(nom_du_repertoire, "donnees/cache.txt"),'w',encoding = 'utf-8') as tempo :
            tempo.write(str(dico_fichier_tempo))

        
        liste_notes.sort(key=lambda x: x[-1], reverse=True)

        return liste_notes
        


    def notes_meteo_ville(self, ville: str) -> dict:
        """
        Determiner des notes sur les donnees meteorologique/climatique de 2022 d'une ville par rapport a des valeurs ideals
        
        Renvoi un `dict` avec les notes ou `None` si on n'a pas pue recuperer les donnes pour calculer des notes

        - Idée de tout le Groupe (idée initial du projet) & Implementé par Thor

        ---

        Sources:
        - [API Geolocation](https://open-meteo.com/en/docs/geocoding-api) pour les coordonees des villes.
        - [API Meteo Historique](https://open-meteo.com/en/docs/historical-weather-api) pour les donnees de meteo d'une vile.
        - [API Qualité D'Air](https://open-meteo.com/en/docs/air-quality-api) pour la qualité de l'aire d'une ville (Utilise pas des donnees historiques, mais des previsons du present a +4jours).

        """
        assert type(ville) == str, "L'argument de ville doit etre de type string"
        
        for char in ville: # pour gerer les arrondissements d'un ville
            if est_nombre(char): # on recherche un nombre pour separer le nom du ville
                
                ville = ville.split(char)[0]
                
                if ville != 'Marseille ' : # l'API n'a pas d'arrondissements pour Marseille
                    ville += f"{int(char):02d}" # d'appres l'API geoloc, les arrondissement sont comme "Paris 03" pour 3 arrondisssmenet
                break # pas ideal, mais on veut pas iterer le rest.

        tout_les_donnees = [] # contient les donnes de meteo et d'air
        geoloc_ville = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={ville}") # pour recuperer longitude et latitude du ville

        # recuperation de tout les donnees
        if geoloc_ville.status_code == 200:
            geoloc_ville = geoloc_ville.json()["results"][0] # on recupere les donnes qui nous interess dans la reponse

            # on demande tout les donnees meteogologique et de qualité d'air des APIs
            ville_meteo = requests.get(f"https://archive-api.open-meteo.com/v1/archive?latitude={geoloc_ville['latitude']}&longitude={geoloc_ville['longitude']}&start_date=2022-01-01&end_date=2023-01-01&hourly=relativehumidity_2m,surface_pressure,cloudcover,windspeed_10m&daily=temperature_2m_mean&timezone=Europe%2FBerlin")
            ville_air = requests.get(f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={geoloc_ville['latitude']}&longitude={geoloc_ville['longitude']}&hourly=uv_index,european_aqi_pm2_5,european_aqi_pm10,european_aqi_no2,european_aqi_o3,european_aqi_so2")

            if ville_meteo.status_code == 200: # si on recoi les données meteorologique de la ville
                ville_meteo = ville_meteo.json() # on prend le json du reponse

                # on supprime les timestamps pour pouvoir iterer les donnees plus facilement sans problem de type
                del ville_meteo["daily"]["time"]
                del ville_meteo["hourly"]["time"]

                tout_les_donnees += list(ville_meteo["hourly"].items()) + list(ville_meteo["daily"].items())  # on ajoute tout ces donnes a la liste de donnes 
            
            if ville_air.status_code == 200: # si on recoi les données de qualité d'air de la ville
                ville_air = ville_air.json() # on prend le json du reponse

                del ville_air["hourly"]["time"] # pour iterer plus facilement les valeurs

                tout_les_donnees += list(ville_air["hourly"].items()) # on ajoute tout ces donnes a la liste de donnees

        if len(tout_les_donnees) == 0: # si vide (aucun des liens ont connecté), il y a pas de notes a faire
            return {} 

        donnees_moy = {} # va contenir les donnees moyennes de chaque critere

        
        for key, values in tout_les_donnees: # on calcule la moyenne annuelle de chaque critere
            values = [value for value in values if value] # enleve le risque d'un erreur avec l'apparition d'un "None" dans la liste de donnees (ça arrive dependent du ville)
            if len(values) > 1: # au cas ou que tout les valeurs sont des None (improbable mais possible)
                keymoy = sum(values)/len(values) # calcule moyenne
                if key == "surface_pressure": keymoy = keymoy*0.00098692 # transforme hPa -> atm
                elif key == "windspeed_10m": keymoy = keymoy/3.6 # transforme km/h -> m/s
                donnees_moy[key] = round(keymoy, 2) # on sauvegarde cette moyenne dans le dictionaire


        valeursIdeales = { # le criteres qu'on va utiliser pour determiner des notes
            "relativehumidity_2m": (0, 40, 100), # en % | moyenne de 30%-50% (https://humiditycheck.com/comfortable-humidity-level-outside)
            "temperature_2m_mean": (0, 27.5, 46), # en Celcius | Le temperature maximum est le temperature record de France (https://fr.wikipedia.org/wiki/Records_de_temp%C3%A9rature_en_France_m%C3%A9tropolitaine)
            "cloudcover": (0, 20, 100), # en %
            "surface_pressure": (0.967, 1, 1.035), # en atm | (les plus haut est bas pressions en france par: https://en.wikipedia.org/wiki/List_of_atmospheric_pressure_records_in_Europe#France)
            "windspeed_10m": (0, 7, 17.5), # en m/s | (0, table 1 pieton, moyenne table 2) du source: https://cppwind.com/outdoor-comfort-criteria/

            "uv_index": (0,0,7.5), # en UVI (Index Ultra Violet) | valeurs par rapport aux recommendations de WHO (https://www.who.int/news-room/questions-and-answers/item/radiation-the-ultraviolet-(uv)-index)
            "european_aqi_pm2_5": (0, 0, 50), # en AQI (Index de Qualité d'Aire) | Source des valleurs vien du documentation du API (voir haut du fonctino)
            "european_aqi_pm10": (0, 0, 100), # meme que precedent pour le rest 
            "european_aqi_no2": (0, 0, 230),
            "european_aqi_o3": (0, 0, 240),
            "european_aqi_so2": (0, 0, 500),
            
        }

        nom_EN_FR = { # sert pour remplaccer les cles des criteres pour les afficher dans les advantages et les inconveniants
            "relativehumidity_2m": "Humidité",
            "temperature_2m_mean": "Température",
            "cloudcover": "Couverture nuageuse",
            "surface_pressure": "Pression de Surface",
            "windspeed_10m": "Vitesse du Vent",
            "uv_index": "Rayonnement Ultra-Violet",
            "european_aqi_pm2_5": "Dose de petit polluants",
            "european_aqi_pm10": "Dose de gros polluants",
            "european_aqi_no2": "Dose de NO2",
            "european_aqi_o3": "Dose de O3",
            "european_aqi_so2": "Dose de S=O2"
        }

        # calcule du note de chaque critere present dans valeursIdeales et donnees_moy
        notes = calcul_note_ideale(valeursIdeales, donnees_moy)
        notes = {nom_EN_FR[clef]:valeur for clef, valeur in notes.items()} # change les noms des clefs en Français lisible

        return notes


    """
    ITER LES NOTES ET APPLIQUE LES REPONSES AUX DIFFERENTS CRITERES PAR RAPPORT AU QCM
    
    Idée par le group, fait par Thor
    """
    def applique_coefs_QCM(self, qcm_reponses: dict, notes: dict) -> list:
        """
        Applique les coefs des choix du QCM aux notes pour que les notes en question 
        sont compté plus ou moins dans la note finale.
        
        - idee du Groupe, fait par Thor.
        """
        assert type(qcm_reponses) == type(notes) == dict, "Les arguments doivent etre des dictionaires"
        notes = notes.copy() # Permet d'éviter de modifier le dictionnaire original

        if self.population: # si la population n'est pas vide
            # note si on aime ville ou campagne (ne sera pas present dans details ou avantages/inconveniants, que note finale)
            notes["population"] = 50 
            est_ville = self.population > 5000 # un commune est un ville a partire de 2k, mais entre 2k et 5k beaucoup resemble a des villages. Donc on prend 5k.

            # determiner si note est 0 ou 100 par rapport au qcm
            if est_ville: notes["population"] = 100 if qcm_reponses["Citadin"] else 0
            else: notes["population"] = 0 if qcm_reponses["Citadin"] else 100

        qcm_to_criteres = { # Chaque reponse du QCM et ses notes qui sont en relation

            # ex: si Activite est 0 dans le QCM, la note 'Les festivales' aura un moindre coefficent dans la note final
            "Scolarite": ["Les écoles","Les collèges", "Les lycées"],
            "Enseignement_Superieur" : ["Possibilité d'études"],
            "Citadin" : ["population"] if self.population else [],            
            "Culture": ["Les musées","Les monuments historiques"],
            "Activite": ['Les festivals'],
            "Precarite" : ["Le prix des maisons","Le prix des appartements"]
        }

        liste_moyenne = [0, 0] # (numerateur,  denumerateur) d'un moyenne


        for reponse, valeur in qcm_reponses.items(): # pour chaque reponse du qcm
            coef = 3 if valeur else 0.5 # coef de 3 si oui, sinon de 0.5

            criteres = qcm_to_criteres[reponse] # recup liste de criteres pour cette reponse
            
            for critere in criteres: # pour chaque critere impacté par cette reponse
                if critere in notes.keys(): # Verifie que le critere est bien present 
                    liste_moyenne[0] += notes[critere]*coef # on calcule la note avec son coef (le numerateur)
                    liste_moyenne[1] += coef # on ajoute son coef au somme denumerateur
                    del notes[critere]

        # on rajoute les notes qui sont de coef 1 (seux qui restent)
        liste_moyenne[0] += sum(list(notes.values())) 
        liste_moyenne[1] += len(notes.keys())

        return liste_moyenne # renvoi la note coefficientée
            



    '''
    METHODE POUR DONNER LE SCORE FINALE DE LA VILLE
    
    Fait par Raphaël et Nathan
    
    '''
    def note_finale(self,meteo=True):


        '''
        Ici on  récupère chaque données pour chaque CSV, si elle sont utilisables on rajoute ça dans la note finale
        (meteo est un booléen qui décide si on souhaite avoir les notes de meteo)
        Pensé et réalisé par Nathan, à l'aide des fonctions au dessus
        '''

        
        # Pour chaque CSV
        for id in infos_csv :
            if id != "communes" :
                self.prepa_recup_donnees(id)
        
        if meteo and est_connecte("https://open-meteo.com/") : # ajoute a notes_finales des notes de la meteo du ville
            notes_meteo = self.notes_meteo_ville(self.commune) # recup notes meteo 
            Donnees.dico_meteo = notes_meteo
            self.notes_finales.update(notes_meteo) # met a jour la dictionaire de notes
            self.liste_notes += list(notes_meteo.values()) # ajout ces notes au liste de notes #? es que liste_notes est necessaire?

        if not meteo : # utilisé quand on calcule note de ville voisins
            self.notes_finales.update(Donnees.dico_meteo) # met a jour la dictionaire de notes

        # Applique les coefs aux notes par rapport au choix du QCM
        note_moyenne_avec_coef = self.applique_coefs_QCM(lire_fichier_dico("REPONSE_QCM"), self.notes_finales)

        
        # Pour tester avant de tout envoyer




        '''
        Création de la note finale
        Fait par Raphaël
        '''
        # calcule du note finale avec les valeurs donnees de applique_coefs_QCM()
        note_finale = int(note_moyenne_avec_coef[0] / note_moyenne_avec_coef[1])
        
        if len(self.liste_notes) == 0: # Si on n'a pas de données
            return 'N/A'
        return round(fonction_sigmoide(note_finale))



    '''
    Gérér les notes avant de faire la note finale
    
    Fait par Raphaël et Nathan
    
    '''
    def prepa_recup_donnees(self, id):
        if infos_csv[id][2]['insee'] >= 0 :
            resultat = self.recuperation_donnees(id)
                    
                # Le code marche, mais la base de données renseigne seulement la moyenne pour les types de CSV par habitant
            if (resultat is not None) and (type(resultat) != list):
                # Si le résultat est trop faible ou trop élevée (ce qui arrive), on met en place un max et un min
                if resultat < 0 :
                    resultat = 0
                elif resultat > 100 :
                    resultat = 100
                self.liste_notes.append(resultat)
                self.notes_finales[infos_csv[id][2]['nom']] =  resultat# Le nom formel


    '''
    POUR REDONNER UN STR DE LA VILLE
    
    Fait par Raphaël
    '''
    def __str__(self) :
        if self.commune != '' :
            return str(self.commune)



# Fin du code !