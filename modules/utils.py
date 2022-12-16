#!/usr/bin/python
from pathlib import Path

from fpdf import FPDF
import fpdf
import textwrap


def combiner_paths(path, extensions):
    """
        Renvoie une liste de fichier finissant par les :extensions dans le dossier :path
        :path chemin du dossier où lister les fichiers
        :extensions extentions des fichiers à récupérer (pdf, epub, txt, etc...)
    """
    fichiers = []
    for e in extensions:
        fichiers.extend(Path(path).glob(e))
    return fichiers


def text_to_pdf(text, filename):
    """
        Converti une chaine de caractère en fichier pdf
        :text chaine de caractère à convertir
        :filename fichier où enregistrer le document pdf
    """

    #Paramètres arbitraires trouvés dans la documentation de FPDF
    a4_width_mm = 210
    fontsize_mm = 3.5
    margin_bottom_mm = 10
    width_text = a4_width_mm / 2.45

    pdf = FPDF(orientation='P', unit='mm', format='A4')

    #On utilise la police DejaVu pour avoir accès aux caractères unicodes et donc les accents
    pdf.add_font('DejaVu', '', 'fonts/DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)

    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    splitted = text.split('\n')

    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm+2, wrap, ln=1)

    pdf.output(filename, 'F')