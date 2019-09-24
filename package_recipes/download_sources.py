__all__ = ['download_source']
import sys
import os.path
import urllib.request
import shlex

from .utils import digestFile

def download_source():
    for line in open(sys.argv[1],'r').readlines():
        line = shlex.split(line)
        assert len(line)>1
        md5sum = line[0]
        fname = line[1]
        url = None
        if len(line)>2:
            url = line[2]

        # attempt to download file if it is not present
        if not os.path.exists(fname) and url != None:
            print ('Downloading %s/%s'%(url,fname))
            urllib.request.urlretrieve('%s/%s'%(url,fname),fname)

        print ('Checking md5sum %s'%fname,)
        md5Computed = digestFile(fname)
        if md5sum!=md5Computed:
            print ('no')
            print ('Error, md5sum %s for file %s does not match expected md5sum %s'%(md5Computed,fname,md5sum))
            sys.exit(1)
        print ('ok')

if __name__ == '__main__':
    download_source()
