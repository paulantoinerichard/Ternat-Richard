#!/usr/bin/python

###    PARTIE 1 : Simon RAVE    ###

from modules.bibliotheque import Bibliotheque
import sys
import os
import configparser
import logging


config = configparser.ConfigParser()
with open("bibli.conf", "r") as config_file:
    config.read_file(config_file)

if __name__ == "__main__":
    config_file_path =""
    log_file = "log.log"
    dossier_livre = "livres/"

    if sys.argv[-1]=="init":
            bibli = Bibliotheque(dossier_livre, config["CONFIG"]["dossier_rapports"])
            bibli.initialise()
            
    elif sys.argv[-1]=="update":
        bibli = Bibliotheque(dossier_livre, config["CONFIG"]["dossier_rapports"])
        bibli.update()

    elif len(sys.argv)>=2:
        if "-c" in sys.argv:
            rang=sys.argv.index("-c")
            try:
                with open(sys.argv[rang+1],"r") as config_file:
                    config.read_file(config_file)
                    log_file=config["CONFIG"]["fichier_log"]
                    dossier_livre=config["CONFIG"]["dossier_livres"]

            except:
                raise Exception("impossible d'ouvrir le fichier de configuration")
        logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s',encoding='utf-8', level=logging.DEBUG)