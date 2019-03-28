import configparser
from pathlib import Path
config = configparser.ConfigParser()
config['uoe-package-recipes'] = {}
config['uoe-package-recipes']['url'] = 'git@git.ecdf.ed.ac.uk:uoe-package-recipes'
config['uoe-package-recipes']['url_test'] = 'git@git.ecdf.ed.ac.uk:testClone'



defaultfile = "/.autocloner.cfg"
configfile_path = str(Path.home()) + defaultfile 


with open(configfile_path, 'w') as configfile:
    config.write(configfile)