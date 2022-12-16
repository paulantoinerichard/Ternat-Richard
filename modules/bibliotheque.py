#!/usr/bin/python
from .livre import Livre
from .utils import combiner_paths

import os
from pathlib import Path
import json
from ebooklib.utils import debug

import logging

class Bibliotheque():
    def __init__(self, dossier_livre, dossier_rapports="rapports") -> None:
        """
            Initiliase une instance de Bibliothèque
            :dossier_livre est le dossier où se trouvent les fichiers des livres
            :dossier_rapports est le dossier d'enregistrement des rapports, par défauts on utilise de dossier 'rapports"
        """
        self.dossier_livre = dossier_livre
        self.livres = self._extraire_livres_depuis_fichier(self.dossier_livre)

        if not os.path.isdir(dossier_rapports):
            os.mkdir(dossier_rapports)
        self.dossier_rapports = dossier_rapports


    def initialise(self):
        """
            Initialise la bibliothèque à partir d'un dossier de livre
        """
        self.enregistrer_rapport_auteur( self._get_dict_livres_par_auteur(self.livres) )
        self.enregistrer_rapport_livres( self.livres )
        self.generer_toc()

    def update(self):
        """
            Met à jour la bibliothèque
        """
        logging.debug("Mise à jour des livres")
        self.rapport_saved = self._open_bibli()
        if self.rapport_saved != None:
            ajoute,retire = self._verif_changement(self.rapport_saved, self.livres)
            if len(ajoute) > 0 or len(retire) > 0:
                # print("Livres ajoutés", ajoute)
                # print("Livres retirés", retire)

                for l in retire:
                    logging.debug(f"{l} retiré")
                    l.del_toc(self.dossier_rapports)

                for l in ajoute:
                    logging.debug(f"{l} ajouté")
                    try:
                        l.save_toc(self.dossier_rapports)
                    except Exception as e:
                        logging.error(f"Impossible de sauvegarder la table des matières de {l.titre}, {e}")
                        continue

                self.enregistrer_rapport_auteur( self._get_dict_livres_par_auteur(self.livres) )
                self.enregistrer_rapport_livres( self.livres )

    def _open_bibli(self):
        """
            Récupère les livres déjà présent dans la bibliothèque sans ouvrir tous les fichiers à partir des rapports
        """
        if os.path.exists(f"{self.dossier_rapports}/rapport_livres.txt"):
            with open(f"{self.dossier_rapports}/rapport_livres.txt", "r", encoding="utf-8") as file:
                livres_json = json.load(file)
                livres = []
                for titre in livres_json:
                    try:
                        livre = Livre(auteur=livres_json[titre]["auteur"], titre=titre, path=livres_json[titre]["fichier"], lang=livres_json[titre]["langue"], open=False)
                        livres.append(livre)
                    except ValueError as e:
                        print(e)
                        continue           
                livres = set( livres )
                return livres
        else:
            logging.error(f"Le chemin d'accès n'existe pas, veuillez vérifier que le fichier: {self.dossier_rapports}/rapport_livres.txt, existe bien")
            raise Exception("Bibliothèque introuvable, vérifier le chemin d'accès aux rapports")

    def _extraire_livres_depuis_fichier(self, path):
        """
            Crée des Objets Livre à partir d'un dossier de fichier
        """
        paths = combiner_paths(path, ("*.pdf", "*.epub"))
        res = [Livre(path=path) for path in paths]
        for l in res:
            l.recuperer_info_fichier()
        livres = set(res)
            
        return livres

    def _get_auteurs_set(self, livres):
        """
            Renvoie un set contenant tous les auteurs uniques de la bibliothèque
        """
        return set(map(lambda x: getattr(x, "auteur"), livres))
        
    def _get_dict_livres_par_auteur(self, livres):
        """
            Renvoie un dictionnaire ayant pour clé un auteur et comme valeur la liste des livres de cet auteur
        """
        auteurs = self._get_auteurs_set(livres)
        return {auteur: {livre.titre: str(livre.path) for livre in livres if livre.auteur == auteur} for auteur in auteurs}

    def enregistrer_rapport_auteur(self, livres_par_auteur):
        """
            Enregistre le rapport contenant tous les auteurs et chacun de leurs livres
        """
        with open(f"{self.dossier_rapports}/rapport_auteurs.txt", "w", encoding="utf-8") as file:
            file.write( json.dumps(livres_par_auteur, indent=4, ensure_ascii=False) )

    def enregistrer_rapport_livres(self, livres):
        """
            Enregistre le rapport contenant tous les livres
        """
        dict_livres = {l.titre: {"auteur": l.auteur, "fichier": str(l.path), "langue": l.lang} for l in livres }
        with open(f"{self.dossier_rapports}/rapport_livres.txt", "w", encoding="utf-8") as file:
            file.write( json.dumps(dict_livres, indent=4, ensure_ascii=False) )

    def generer_toc(self):
        """
            Génère les fichiers contenant la table des matières de chaque livre
        """
        for l in self.livres:
            try:
                l.save_toc(self.dossier_rapports)
            except Exception as e:
                logging.error(f"Impossible de sauvegarder la table des matières de {l.titre}, {l.path} |  {e}")
                continue
        

    def _verif_changement(self, old, new):
        """
            Compare 2 set de livres et renvoie les livres ajoutés et retirés
        """
        livres_ajoutes = new.difference(old)
        livres_enleves = old.difference(new)

        return livres_ajoutes, livres_enleves