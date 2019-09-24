__all__ = ['RPMPackage']

import git
import string
import os.path,os
from shutil import copyfile
import sys
from glob import glob

from .utils import digestFile

makefileTemplate = string.Template("""SHELL=/bin/bash

SPECFILE = $spec
MOCK_CHROOT = $distribution-lcfg-$$(MOCK_ARCH)

SCRIPTS_DIR = ..
include $$(SCRIPTS_DIR)/make.rules
""")

def copyFile(cfg,fname):
    f=os.path.join(os.path.dirname(sys.argv[0]),'..','share','package-recipes',fname)
    o=os.path.join(cfg['local_path'],fname)
    if not os.path.isfile(f):
        raise RuntimeError('could not find file %s'%f)
    if not os.path.exists(o):
        copyfile(f,o)
    else:
        if digestFile(f) != digestFile(o):
            print('Warning, files differ: %s %s'%(f,o))
 

class RPMPackage:
    def __init__(self,cfg,packageName):
        self._cfg = cfg
        self._name = packageName
        self._repo = None
        
    @property
    def cfg(self):
        return self._cfg
    @property
    def name(self):
        return self._name
    def get_pkgname(self):
        return self.name
    @property
    def specname(self):
        return self.get_pkgname()+'.spec'
    @property
    def project_url(self):
        return self.cfg['project_url'] + '/' + self.get_pkgname() + '.git'
    @property
    def local_repo_path(self):
        return os.path.join(self.cfg['local_path'],self.get_pkgname())
    @property
    def local_branch_name(self):
        return self.cfg['unit']+'_'+ self.cfg['distribution']
    
    @property
    def repo(self):
        if self._repo is None:
            if not os.path.exists(self.local_repo_path):
                # create a local repo
                self._repo = git.Repo.init(self.local_repo_path)
                # create our remote
                new_remote = git.Remote.add(self._repo,'origin',self.project_url)
                origin = self._repo.remotes.origin
            else:
                self._repo = git.Repo(self.local_repo_path)
        return self._repo
    
    def create_Makefile(self):
        copyFile(self.cfg,'make.rules')

        mname = os.path.join(self.local_repo_path,'Makefile')
        try:
            sname = glob(os.path.join(self.local_repo_path,'*.spec'))[0]
        except:
            print ('could not find any spec file')
            return
            
        if not os.path.exists(mname):
            open(mname,'w').write(makefileTemplate.substitute(
                spec=os.path.basename(sname),
                distribution = self.cfg['distribution']))
            self.repo.index.add([os.path.basename(mname)])
                    
    def commit(self,msg):
        self.repo.index.commit(msg)

    def push(self):
        self.repo.remotes.origin.push(self.local_branch_name)
