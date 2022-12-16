#!/usr/bin/python


from .utils import text_to_pdf

import os
from PyPDF2 import PdfFileReader
import epub
from pathlib import Path
import ebooklib.epub as ebl
import json
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from ebooklib.utils import debug
import ebooklib

from bs4 import BeautifulSoup as bs

import pypandoc
import logging


logger = logging.getLogger()

class Livre():
    def __init__(self, auteur=None, titre=None, path=None, lang="fr", open=True) -> None:
        """
            Crée un livre à partir d'un fichier
            :auteur est l'auteur du livre
            :titre est le titre du livre
            :path est le chemin du fichier du livre
            :lang est la langue du livre
            :open True pour récupérer directement les infos depuis le fichier spécifié en :path, False sinon
        """
        self.toc = None
        if path != None:
            if isinstance(path, Path):
                self.path = path
            else:
                self.path = Path(path)

            
            if isinstance(path, Path):
                self.file_name = path.name
            else:
                self.file_name = Path(path).name
            self.auteur = auteur
            self.titre = titre
            self.lang = lang

            if open:
                self.recuperer_info_fichier()

        else:
            self.auteur = auteur
            self.titre = titre

        if self.auteur == None:
            self.auteur = "Sans Auteur"

        # if self.titre == None:
        #     raise ValueError(f"Impossible de récupérer le titre du livre, {titre}")

    def recuperer_info_fichier(self):
        """
            Choisit la bonne fonction de récupération des données en fonction du type de fichier
        """
        if self.path.suffix == ".pdf":
            self._open_pdf()
        elif self.path.suffix == ".epub":
            self._open_epub()

    def __repr__(self) -> str:
        return f"{self.titre} par {self.auteur}"

    def _open_pdf(self):
        """
            Ouvre un fichier pdf et extrait le titre, l'auteur, la langue et la table des matières si elle existe
        """
        with self.path.open(mode='rb') as f:
            pdf = PdfFileReader(f, strict=False)
            information = pdf.metadata
            self.auteur = information.author
            self.titre = information.title
            parser = PDFParser(f)
            document = PDFDocument(parser)

            # Recupère la TOC du document
            try:
                outlines = document.get_outlines()

                content = []
                for (level,title,dest,a,se) in outlines:
                    content.append(f"{title}")
                self.toc = bytes("\n".join(content), encoding='utf-8')
            except :
                logger.debug(f"Pas de table des matières pour {self.titre}")
                self.toc = None
                

    def _open_epub(self):
        """
            Ouvre un fichier epub et extrait le titre, l'auteur, la langue et la table des matières
        """
        with epub.open_epub(f'{self.path}') as book:
            metadata = book.opf.metadata
            auteur = metadata.creators[0][0]
            titre = metadata.titles[0][0]
            self.auteur = auteur
            self.titre = titre
            self.lang = metadata.languages[0]

        b = ebl.read_epub(self.path)


        toc_xml = b.get_item_with_href("toc.ncx").get_content()
        toc_parsed = bs(toc_xml, features="xml").find_all("navPoint")
        toc_parsed = list(map(  lambda x: x.find("text").text,toc_parsed))

        toc_pretty = bytes("\n".join(toc_parsed), "utf-8")
        self.toc = toc_pretty

    def save_toc(self, path):
        """
            Enregistre la table des matières en epub,txt et pdf dans le dossier spécifier en :path
        """
        if self.toc != None:
            with open(f"{path}/{self.titre}_toc.txt", "wb") as f:
                f.write(self.toc)
            
            text_to_pdf(self.toc.decode("utf-8"), f"{path}/{self.titre}_toc.pdf")

            md = self.toc.decode("utf-8").replace("\n", "<br />").replace("À propos de cette édition électronique", "")
            pypandoc.convert_text(md, format="md", to="epub",extra_args=[f"--metadata=title:{self.titre}",f"--metadata=author:{self.auteur}",f"--metadata=language:{self.lang}"] ,outputfile=f"{path}/{self.titre}_toc.epub")

    def del_toc(self, dossier_rapports):
        """
            Supprime les tables des matières et l'objet
        """
        if os.path.isfile(f"{dossier_rapports}/{self.titre}_toc.txt"):
            Path(f"{dossier_rapports}/{self.titre}_toc.txt").unlink()

        if os.path.isfile(f"{dossier_rapports}/{self.titre}_toc.epub"):
            Path(f"{dossier_rapports}/{self.titre}_toc.epub").unlink()

        if os.path.isfile(f"{dossier_rapports}/{self.titre}_toc.pdf"):
            Path(f"{dossier_rapports}/{self.titre}_toc.pdf").unlink()
        del self

    def force_del(self):
        """
            Supprime le fichier originel du livre
        """
        self.path.unlink()
        del self

    def __hash__(self) -> int:
        return hash((self.auteur, self.titre, self.lang))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Livre):
            return (self.auteur == __o.auteur and self.titre == __o.titre and self.lang == __o.lang)
        else:
            raise ValueError(f"Can't compare Livre to {type(__o)}")