import configparser
import argparse
from pathlib import Path
import os



parser = argparse.ArgumentParser(description='')
parser.add_argument('-u','--url', dest='git_url', metavar='git url for user or a group account', nargs='?',
                    help='')
parser.add_argument('-p', '--path', dest='config_path', metavar='path to save your .autocloner.cfg (optional)', nargs='?', help='path to send your .autocloner.cfg at (by default it is save at $HOME/ .autocloner.cfg) ')

parser.add_argument('-rp', '--clonepath', dest='clone_path', metavar='local repo path to save cloned repos (optional)', nargs='?', help='optional ')


args = parser.parse_args()

git_url = args.git_url

# set up where you cloned repos will be saved
config_dir_path = args.config_path
defaultfile = "/.autocloner.cfg"
config_file_path =''
if config_dir_path is None:
    config_file_path = str(Path.home()) + defaultfile 
else:
    config_file_path = str(config_dir_path) + defaultfile

if git_url is None:
    #testClone
    #uoe-package-recipes
    git_url = 'git@git.ecdf.ed.ac.uk:testClone'


config = configparser.ConfigParser()
config['uoe-package-recipes'] = {}
config['config_file_path'] = {}
config['clone_dir'] = {}

config['config_file_path']['local_path'] = config_file_path
config['uoe-package-recipes']['url'] = git_url
config['clone_dir']['local_path'] ='temp' if args.clone_path is None else args.clone_path  # 'temp by default' if not specified

if config_dir_path is not None and  not os.path.exists(config_dir_path):
        os.mkdir(config_dir_path)

with open(config_file_path, 'w') as configfile:
    config.write(configfile)
print('.autocloner.cfg file is now saved at :', config_file_path)