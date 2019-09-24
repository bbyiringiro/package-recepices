__all__ = ['releasePkg']

import argparse
import git
import os.path
from .utils import getSpecMeta


def releasePkg():
    parser = argparse.ArgumentParser()
    parser.add_argument('specfile',help='name of the specfile of the package to be released')
    args = parser.parse_args()

    spec = getSpecMeta(args.specfile)

    tagname = ''
    for k in ['Distribution','Version','Release']:
        if spec[k] is not None:
            if len(tagname) > 0:
                tagname += '_'
            tagname += spec[k]

    repo = git.Repo(os.path.abspath(os.path.dirname(args.specfile)))
    try:
        repo.create_tag(tagname,message='release package')
        print ('new tag: ',tagname)
    except Exception as e:
        print ('error: failed to create tag',tagname)
        print (e)
    
if __name__ == '__main__':
    releasePkg()
