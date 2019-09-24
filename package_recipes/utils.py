__all__ = ['digestFile','getSpecMeta','getConfig','configParser']

import hashlib
import argparse
import os, os.path
import getpass
import configparser
from pyrpm.spec import Spec, replace_macros

def digestFile(fname):
    BUF_SIZE = 65536
    md5 = hashlib.md5()
    with open(fname,'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

def getSpecMeta(fname):
    spec = Spec.from_file(fname)
    meta = {}
    meta['Name'] = replace_macros(spec.name,spec)
    meta['Version'] = replace_macros(spec.version,spec)
    meta['Release'] = replace_macros(spec.release,spec)
    
    
    keys = ['Distribution']
    for k in keys:
        meta[k] = None
    with open(fname,'r') as sfile:
        for line in sfile.readlines():
            line = line.split(':')
            k = line[0].strip()
            if k in keys:
                meta[k] = line[1].strip()
    return meta

def configParser(add_help=False):
    CFG = os.path.join(os.path.expanduser('~'),'.package-recipes.cfg')
    
    parser = argparse.ArgumentParser(add_help=add_help)
    group = parser.add_argument_group('configuration')
    group.add_argument('-c','--config',default=CFG,metavar='CFG',help='read configuration from file CFG, default=%s'%CFG)
    group.add_argument('-d','--distribution',help='override distribution, eg el7')
    group.add_argument('-C','--print-config',action='store_true',default=False,help='print config')
    return parser

def getConfig(args,cname):
    cfg = {
        'local_path' : os.getcwd(),
        'project_url' : 'git@git.ecdf.ed.ac.uk:uoe-package-recipes',
        'upstream_branch' : 'f19',
        'unit' : 'uoe',
        'packager' : getpass.getuser(),
        'distribution' : 'el7',
        'R_version' : '3.6.0',
        }

    if os.path.exists(cname):
        config = configparser.ConfigParser()
        config.read(cname)
        for k in cfg:
            if config.has_option('config',k):
                cfg[k] = config['config'][k]

    if args.distribution is not None:
        cfg['distribution'] = args.distribution
    
    return cfg
