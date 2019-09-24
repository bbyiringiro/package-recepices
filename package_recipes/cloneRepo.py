__all__ = ['cloneRepo']


import argparse
import git
import os.path,os
import sys
from datetime import datetime
from glob import glob
from pprint import pprint
import string

from .utils import getConfig,configParser
from .FedoraPackage import RPMPackage

class FedoraPackage(RPMPackage):
    def __init__(self,cfg,packageName):
        self._url = ''
        if "git@" in packageName or "https://" in packageName:
            self._url = packageName
        elif len(packageName.split("/")) < 2:
            self._url = 'https://src.fedoraproject.org/rpms/'+packageName+'.git'
        else:
            self._url = 'https://src.fedoraproject.org/'+packageName +'.git'

        u = self.url[:-4].split('/')
        if u[-2] == 'rpms':
            name = u[-1]
        else:
            name = u[-2]+'_'+url[-1]
        super().__init__(cfg,name)

    @property
    def url(self):
        return self._url
        
    def clone(self):
        if len(glob(os.path.join(self.local_repo_path,'*.spec'))) == 0:
            # create upstream
            upstream = self.repo.create_remote('upstream',self.url)
            upstream.fetch()

            head = self.repo.create_head(
                self.local_branch_name,
                upstream.refs[self.cfg['upstream_branch']])
            head.checkout()
            
            self.commit('imported to package recipes')
            self.push()
            
    def update_spec(self):
        for sn in glob(os.path.join(self.local_repo_path,'*.spec')):
            self._update_spec_file(sn)
    
    def _update_spec_file(self,specname):
        with open(specname+'-new','w') as out:
            release = ''
            version = ''
            for line in open(specname,'r').readlines():
                if line.startswith('Release:'):
                    # modify release string and add extra metadata
                    idx = line.find('%')
                    if idx > 0:
                        line = line[:idx]
                    line += '_1.' + self.cfg['unit'] +'\n'
                    release = line.split(':')[-1].strip()
                    line += 'Packager: %s\n'%self.cfg['packager']
                    line += 'Distribution: %s\n'%self.cfg['distribution']
                elif line.startswith('Version:'):
                    version  = line.split(':')[-1].strip()
                elif line.startswith('%changelog'):
                    # insert into change log
                    line += '* %s %s - %s-%s\n'%(
                        datetime.now().strftime('%a %b %d %Y'),
                        self.cfg['packager'],
                        version,release)
                    line += '- imported to package recipes\n\n'
                        
                out.write(line)
        os.rename(specname+'-new',specname)
        self.repo.index.add([os.path.basename(specname)])

def cloneRepo():

    parser = argparse.ArgumentParser(parents=[configParser()])
    parser.add_argument('package',help='name of package to be cloned')
    parser.add_argument('-b','--branch',help='override which upstream branch to track, eg f19')
    args = parser.parse_args()

    cfg = getConfig(args,args.config)
    if args.branch is not None:
        cfg['upstream_branch'] = args.branch
    if args.print_config:
        pprint(cfg)
        sys.exit(0)
        
    
    package = FedoraPackage(cfg,args.package)
    package.clone()
    package.update_spec()
    package.create_Makefile()
    package.commit('create Makefile')

                
    
if __name__ == '__main__':
    cloneRepo()
