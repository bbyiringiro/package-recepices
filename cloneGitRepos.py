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

threadLock = threading.Lock()

def loadConfiguration(config_dir_path=None):
    config = configparser.ConfigParser()
    defaultfile = "/.autocloner.cfg"
    if config_dir_path is None:
        config_file_path = str(Path.home()) + defaultfile 
    else:
        config_file_path = config_dir_path + defaultfile

    config.read(config_file_path)
    if len(config.sections()) ==0  or 'uoe-package-recipes' not in config:
        print("Please create your config file by createMyConfig.py with desired arguments or configuration file path as argument after -c or --config")
        raise ValueError('couldn\'t find config file')
    loca_dir_path = None 
    if 'local_path' in config['clone_dir'] and config['clone_dir']['local_path'] !='':
        loca_dir_path = config['clone_dir']['local_path']
        
    
    if 'url' in config['uoe-package-recipes']:
        return (str(config['uoe-package-recipes']['url']), loca_dir_path)
    else:
        raise ValueError('Couldn\'t find push url in the config file')




def cloneRepo(url, cloningpath='temp'):
   
    """
    Clones a single GIT repository.
    Input:-
    url: GIT repository url.
    cloningPath: the directory that the repository will be cloned at. But the Default is temp
    """

    threadLock.acquire()
    if cloningpath is None:
        cloningpath = 'temp'
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
       
        try:
            repo = git.Repo(fullpath)
            origin = repo.remotes.origin
            origin.pull()
            print("Repo already exists, so only updated at if any commited changes", fullpath)
        except:
            print('couldn\' pull new updates')
        
        update=True
    else:
        try:
            print('cloning from', url)
            git.Repo.clone_from(url, fullpath)
            print('the repo cloned to ', fullpath)
        except Exception as err:
            print('something went wrong while pulling from from ', url)
            print(err)
            exit(1)

    try:
        pushLocalRepo(fullpath, reponame, update) # pushing it after cloning
    except Exception as err:
        print("Somthing, went wrong while try to push", reponame, "package", err)
        exit(1)
    threadLock.release()

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
            origin = repo.remotes.upstream;
        else:
            # adds new remote upstream for specially for pushing
            new_remote = git.Remote.add(repo,'upstream', pushUrl);

            origin = repo.remotes.upstream;
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
    parser.add_argument('packages', metavar='package(s)', nargs='+',
                        help='packange(s)_name/git_url (if it more than one separate them by comma)')

    parser.add_argument('-c', '--config', dest='config_file', metavar='config-file-path(optional)', nargs='?', help='config-file-path (optional) by default it takes check at ~/.autocloner.cfg($HOME/.autocloner.cfg)  ')

    parser.add_argument('-s', '--save', dest = 'save_path',  metavar='save path(optional, saved at ./temp/ by default)', nargs='?', help='save-path(optional)')

    args = parser.parse_args()
    

    args = parser.parse_args()
    packageNames = args.packages[0]

    save_path = args.save_path

    

    try: 
        global GitGroupUrl 
        config = loadConfiguration(args.config_file)
        GitGroupUrl = config[0]
        if save_path is None:
            save_path = config[1] 
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
        # cloneRepo(cloningQueue.get(),save_path)

        t = threading.Thread(target=cloneRepo, args = (cloningQueue.get(),save_path))
        t.daemon = True
        # t.start()
        t.run()



    

if (__name__ == "__main__"):
    try:
        main()
    except KeyboardInterrupt:
            print('\nKeyboardInterrupt.')
            print('\nExiting...')
            exit(0)
