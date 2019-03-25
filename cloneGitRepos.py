import argparse
import git
import json
import os, shutil, time
try:
    import queue
except ImportError:
    import Queue as queue
import threading
import config




def cloneRepo(URL, cloningpath='temp'):
    """
    Clones a single GIT repository.
    Input:-
    URL: GIT repository URL.
    cloningPath: the directory that the repository will be cloned at. But the Default is temp
    """

    try:
        try:
            if not os.path.exists(cloningpath):
                os.mkdir(cloningpath)
        except Exception as err:
            print("Something went wrong while creating a dir, "+err)

        reponame = URL.split("/")[-2] + "_" + URL.split("/")[-1]
        # URL = URL.replace("git@", "https://")

        if reponame.endswith(".git"):
            reponame = reponame[:-4]
        if '@' in reponame:
            reponame = reponame.split('_')[-1]

        fullpath = cloningpath + "/" + reponame
        update=False
        if os.path.exists(fullpath):
            # git.Repo(fullpath).remote().pull() # update repo if it already exist
            repo = git.Repo(fullpath)
            origin = repo.remotes.origin
            origin.pull('master')
            print("Repo already exists, so only updated at", fullpath)
            update=True
        else:
            print('cloning from', URL)
            git.Repo.clone_from(URL, fullpath)
            print('repo clone to ', fullpath)
        pushLocalRepo(fullpath, reponame, update) # pushing it after cloning

        # deleting the local repo
        try:
            shutil.rmtree(fullpath)
            print(fullpath, "dir deleted")
        except Exception as err:
            print('something went wrong while deleting', fullpath)
    except Exception as err:
        print("Error: There was an error in cloning or pushing [{}]".format(URL), err)

def pushLocalRepo(repo_path, name, update=False):
    pushurl = config.GitGroupURL + name + '.git'

    print('Pushing it to', pushurl )
    try:
        repo = git.Repo(repo_path)
        origin=None
        if update:
            # repo.commit()
            # print()
            # origin = repo.remotes.origin.fetch()
            # need to update remote orgin then push
            pass
        else:
            origin = git.remote.Remote.create(repo, name, pushurl)
        origin.push('master')
        print('success')
    except Exception as err:
        print(err)
        # raise Exception('couldn\'t push')


def parseURL(packageName):
    url =''
    if "git@" in packageName or "https://" in packageName:
        url = packageName
    elif len(packageName.split("/")) < 2:
        url = 'https://src.fedoraproject.org/rpms/'+packageName+'.git';
    else:
        url = 'https://src.fedoraproject.org/'+packageName +'git';
    return url
    
   

def main():
    parser = argparse.ArgumentParser(description='-p for one or more packages separated by commas')
    parser.add_argument("-p",
                        dest="packageNames",
                        metavar='<package_1>,<package_2>',
                        help="package name or url you want to clone, separate them by a comma(,) if you want to clone more than one",
                        action="store")
    

    args = parser.parse_args()
    if not args.packageNames:
        print('At least one package name to be cloned is required, the format is -p <package_1>,<package_2> ...')
        exit(0)
    URLs = args.packageNames.split(',')
    threads_limit =5
    Q = queue.Queue()
    threads_state = []
    for URL in URLs:
        Q.put(parseURL(URL))
    while Q.empty() is False:
        cloneRepo(Q.get())



    

    
    

    
    # git remote add repo_name  https://git.ecdf.ed.ac.uk/testClone/test5.git
    # git push repo_name  master


if (__name__ == "__main__"):
    try:
        main()
    except KeyboardInterrupt:
            print('\nKeyboardInterrupt.')
            print('\nExiting...')
            exit(0)