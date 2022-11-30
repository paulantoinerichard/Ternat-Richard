import os,fitz,tarfile,sys
import aspose.words as aw
import py3langid as langid

class Livre():
    def __init__(self,file):  #recuperation des informations
        tdm=file.get_toc()
        lang=[]
        for page in file:
            text = page.get_text()
            lang.append(text)
        self.nom=file.name
        if file.metadata['title']!='':
            self.titre=file.metadata['title']
        else:
            self.titre='inconnu'
        if file.metadata['author']!=[]:
            self.auteur=file.metadata['author']
        else:
            self.auteur='inconnu'
        if tdm!=[]:
            self.tdm=tdm
        else:
            self.tdm=['inconnu']
        self.langue=langid.classify(str(lang))[0]
        self.list_rapports=[]


    def rapports_tdm(self):    #creation de la tdm aux 3 formats
        if self.nom[-3:]=="pdf":
            nv_nom=self.nom[0:-3]
        else:
            nv_nom=self.nom[0:-4]
        nom_txt=f"{nv_nom}.txt"
        self.list_rapports.append(nom_txt)
        txt=open(nom_txt,'w',encoding="utf-8")
        for ligne in self.tdm:
            txt.write(f"{ligne}\n")
        txt.close()

        doc=aw.Document(nom_txt)
        doc.save(f"{nv_nom}.pdf")
        doc.save(f"{nv_nom}.epub")



class Bibliotheque():
    def __init__(self):  #raccourcis des paths 
        os.mkdir('rapportstdm')
        self.mainfile=os.getcwd()
        self.pathlivres=self.mainfile+"/livres"
        self.pathrapportstdm=self.mainfile+"/rapportstdm"
        self.biblio=[]

        file_noms=open("noms.txt", "w",encoding="utf=8")  #création d'une liste de noms pour la fonction add_file
        file_noms.close()

        log=open("log.txt",'w',encoding="utf-8")   #création du log
        log.close()


    def complete(self):    #creation des livres et des rapports tdm
        os.chdir(self.pathlivres)
        for filename in os.listdir():
            if (filename[-3:]=='pdf') or (filename[-4:]=='epub'):
                file=fitz.open(filename)
                nv_livre=Livre(file)
                print(nv_livre.nom)
                os.chdir(self.pathrapportstdm)
                nv_livre.rapports_tdm()
                os.chdir(self.pathlivres)
                self.biblio.append(nv_livre)
                os.chdir(self.mainfile)
                file_noms=open("noms.txt", "a",encoding="utf=8")
                file_noms.write(f"{filename}\n")
                file_noms.close()
                os.chdir(self.pathlivres)

            else:   #ouverture du log
                log=open("log.txt",'a',encoding="utf-8")
                log.write(f"le fichier {filename} n'est pas traité\n")
                log.close()


    def rapport_titres(self):   #creation du rapport titre txt
        os.chdir(self.mainfile)
        file = open(f"rapport_titres.txt", "w",encoding="utf=8")
        for livre in self.biblio:
            file.write(f"Titre = {livre.titre}\n")
            file.write(f"Auteur = {livre.auteur}\n")
            file.write(f"Langue = {livre.langue}\n")
            file.write(f"Nom du fichier = {livre.nom}\n\n")
        file.close()

        doc=aw.Document("rapport_titres.txt")   #conversion du txt en pdf et epub
        doc.save("rapport_titres.pdf")
        doc.save("rapport_titres.epub")


    def rapport_auteurs(self):   #creation du rapport auteur txt
        listeauteurs=[]
        listetitre=[]
        for livre in self.biblio:
            if isinstance(livre.auteur, str)==True:   #cas ou il n'y a qu'un seul auteur (stocké en str)
                if livre.auteur not in listeauteurs:
                    listeauteurs.append(livre.auteur)
                    listetitre.append([f"Titre = {livre.titre} / Nom du fichier = {livre.nom}"])
                else:
                    for i in range (len(listeauteurs)):
                        if livre.auteur == listeauteurs[i]:
                            listetitre[i].append(f" Titre = {livre.titre} / Nom du fichier = {livre.nom}")

            else:  #cas de co-auteurs (stockés en liste)
                for aut in livre.auteur:
                    if aut not in listeauteurs:
                        listeauteurs.append(aut)
                        listetitre.append([f"Titre = {livre.titre} / Nom du fichier = {livre.nom}"])
                    else:
                        for i in range (len(listeauteurs)):
                            if aut == listeauteurs[i]:
                                listetitre[i].append(f" Titre = {livre.titre} / Nom du fichier = {livre.nom}")

        file=open(f"rapport_auteurs.txt","w", encoding='utf-8')
        for i in range (len(listeauteurs)):
            file.write(f"Auteur : {listeauteurs[i]}\n")
            file.write(f"{str(listetitre[i])}\n\n")
        file.close()

        doc=aw.Document("rapport_auteurs.txt")   #conversion du txt en pdf et epub
        doc.save("rapport_auteurs.pdf")
        doc.save("rapport_auteurs.epub")


    def add_file(self):   #premiere methode du update (ajout d'un livre dans le dossier)
        os.chdir(self.mainfile)
        for filename in os.listdir(self.pathlivres):
            a=0
            file_noms=open("noms.txt", "r",encoding="utf=8")
            ligne = file_noms.readlines()
            file_noms.close()
            for i in ligne:
                if filename==str(i):
                    a+=1
            if a!=1:
                file=fitz.open(filename)
                livre=Livre(file)
                rapport_titres=open("rapport_titres.txt",'a',encoding="utf-8")   #ajout dans le rapport titre
                rapport_titres.write(f"Titre = {livre.titre}\n")
                rapport_titres.write(f"Auteur = {livre.auteur}\n")
                rapport_titres.write(f"Langue = {livre.langue}\n")
                rapport_titres.write(f"Nom du fichier = {livre.nom}\n\n")
                rapport_titres.close()
                
                rapport_auteurs=open(f"rapport_auteurs.txt","a", encoding='utf-8')  #ajout dans le rapport auteur
                if livre.auteur not in rapport_auteurs :
                    rapport_auteurs.write(f'Auteur = {livre.auteur}\n')
                    rapport_auteurs.write([f"Titre = {livre.titre} / Nom du fichier = {livre.nom}\n\n"])
                else:
                    lines= rapport_auteurs.readlines()
                    j=0
                    for k in lines:
                        j+=1
                        if k.find(livre.auteur) ==0 :
                            texte=rapport_auteurs.readlines()
                            rapport_auteurs.close()
                            texte.insert(j+1, f"Titre = {livre.titre} / Nom du fichier = {livre.nom}" )
                            rapport_auteurs=open(f"rapport_auteurs.txt","w", encoding='utf-8')
                            rapport_auteurs.write(texte)
                            rapport_auteurs.close()

        

"""
#on unzip le fichier livres.tgz dans un fichier 'livres' que l'on met dans le repertoire courant
file = tarfile.open("livres.tgz")
file.extractall()
file.close()
"""

if sys.argv[1]=="init":
    file = tarfile.open("livres.tgz")
    file.extractall()
    file.close()
    bibliotheque=Bibliotheque()
    bibliotheque.complete()
    bibliotheque.rapport_titres()
    bibliotheque.rapport_auteurs()

if sys.argv[1]=="update":
    bibliotheque.add_file()