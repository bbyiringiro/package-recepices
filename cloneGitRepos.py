import argparse
import git
import json
import os, time
from pathlib import Path
try:
    import queue
except ImportError:
    import Queue as queue
import threading
import configparser

def loadConfiguration(config_file_path=None):
    config = configparser.ConfigParser()
    defaultfile = "/.autocloner.cfg"
    if config_file_path is None:
        config_file_path = str(Path.home()) + defaultfile 
        config.read(config_file_path)
    else: 
        config.read(config_file_path)
    if len(config.sections()) ==0  or 'uoe-package-recipes' not in config:
        print("Please create your config file editing and running createMyConfig.py or pass your configuration file path as second argument")
        raise ValueError('couldn\'t find config file')
    
    key='url_test'
    if key in config['uoe-package-recipes']:
        return str(config['uoe-package-recipes'][key])
    else:
        raise ValueError('Couldn\'t find', key, 'in the config file')




def cloneRepo(url, cloningpath='temp'):
    """
    Clones a single GIT repository.
    Input:-
    url: GIT repository url.
    cloningPath: the directory that the repository will be cloned at. But the Default is temp
    """

    try:
        if not os.path.exists(cloningpath):
            os.mkdir(cloningpath)
    except Exception as err:
        print("Something went wrong while creating a dir, "+err)

    reponame = url.split("/")[-2] + "_" + url.split("/")[-1]
    # url = url.replace("git@", "https://")

    if reponame.endswith(".git"):
        reponame = reponame[:-4]
    if '@' in reponame:
        reponame = reponame.split('_')[-1]

    fullpath = cloningpath + "/" + reponame
    update=False
    if os.path.exists(fullpath):
        repo = git.Repo(fullpath)
        origin = repo.remotes.origin
        origin.pull()
        print("Repo already exists, so only updated at if any commited changes", fullpath)
        update=True
    else:
        try:
            print('cloning from', url)
            git.Repo.clone_from(url, fullpath)
            print('repo clone to ', fullpath)
        except:
            print('something went wrong while pulling from from ', url)
            exit(1)

    try:
        pushLocalRepo(fullpath, reponame, update) # pushing it after cloning
    except Exception as err:
        print("Somthing, went wrong while try to push", reponame, "package", err)
        exit(1)

def pushLocalRepo(repo_path, name, update=False):

    if len(GitGroupUrl) == 0:
        print ('the pushing URL is None provided, check your config file')
        exit(1)
    pushUrl = GitGroupUrl + "/" + name + '.git'

    print('Pushing it to', pushUrl )
    try:
        repo = git.Repo(repo_path)
        origin=None
        #if it already exists, only push some changes
        if update:
            repo.commit()
            origin = repo.remotes.origin
        else:
            remote = git.remote.Remote(repo, 'origin')
            remote.set_url(pushUrl)
            origin = repo.remotes.origin
        origin.push('master')
        print('success')
    except Exception as err:
        raise Exception(err)


def parseurl(packageName):
    url =''
    if "git@" in packageName or "https://" in packageName:
        url = packageName
    elif len(packageName.split("/")) < 2:
        url = 'https://src.fedoraproject.org/rpms/'+packageName+'.git';
    else:
        url = 'https://src.fedoraproject.org/'+packageName +'.git';
    return url
    
   

def main():

    parser = argparse.ArgumentParser(description='It allows you to clone any git repo, if you type packages name it try to find it from https://src.fedoraproject.org/ \
        otherwise it uses a repo link given, and then upload it to git group or account you configured in you config file')
    parser.add_argument('arguments', metavar='packages config-file-path(optional) save path(optional, saved at temp/ by default)', nargs='+',
                        help='packange(s)_name/git_url (if packages separate them by comma)  followed by config-file-path (optional) followed by save-path(optional)')

    args = parser.parse_args()
    

    args = parser.parse_args()
    packageNames = args.arguments[0]
    try: 
        global GitGroupUrl 
        if len(args.arguments)> 1:
            GitGroupUrl = loadConfiguration(args.arguments[1])
        else:
            GitGroupUrl = loadConfiguration(None)
    except Exception as err:
        print(err)
        exit(1)

    urls = packageNames.split(',')
    threads_limit =5
    cloningQueue = queue.Queue()
    threads_state = []
    for url in urls:
        cloningQueue.put(parseurl(url))
    while cloningQueue.empty() is False:
        cloneRepo(cloningQueue.get())



    

    
    

    
    # git remote add repo_name  https://git.ecdf.ed.ac.uk/testClone/test5.git
    # git push repo_name  master


if (__name__ == "__main__"):
    try:
        main()
    except KeyboardInterrupt:
            print('\nKeyboardInterrupt.')
            print('\nExiting...')
            exit(0)
