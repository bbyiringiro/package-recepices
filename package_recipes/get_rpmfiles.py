__all__ = ['get_rpmfiles']

import argparse
import subprocess
import sys, os.path
from .utils import getSpecMeta

def get_rpmfiles():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m','--mock-cfg',help='mock chroot configuration file')
    parser.add_argument('-o','--output',default='up',help='name of outputfile, default up')
    parser.add_argument('specfile',help='name of the specfile of the package to be released')
    args = parser.parse_args()

    resultdir = ''
    if args.mock_cfg is not None:
        for l in open(args.mock_cfg,'r').readlines():
            if "config_opts['resultdir']" in l:
                resultdir = l.split('=')[1].strip().replace("'",'')
    
    # query the spec file
    p = subprocess.Popen(['rpm','-q','--specfile',args.specfile],stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if p.wait() != 0:
        print ('Error, querying specfile %s'%args.specfile)
        print (p.stderr.read())
        sys.exit(1)

    foundAllFiles = True
    with open(args.output,'w') as out:
        
        for l in p.stdout.readlines():
            r = l.decode('utf-8').strip().replace("'",'')+'.rpm'
            r = os.path.join(resultdir,r)
            if not os.path.exists(r):
                foundAllFiles=False
                print('Warning: could not find file %s'%r, file=sys.stderr)

            out.write(r+'\n')

        meta = getSpecMeta(args.specfile)
        srpm = os.path.join(resultdir,'%s-%s-%s.src.rpm'%(meta['Name'],meta['Version'],meta['Release']))
        if not os.path.exists(srpm):
            foundAllFiles=False
            print('Warning: could not find file %s'%srpm, file=sys.stderr)
        out.write (srpm+'\n')

    if not foundAllFiles:
        print('Warning, did not find all rpm files. Check output file %s'%args.output)
        sys.exit(2)
