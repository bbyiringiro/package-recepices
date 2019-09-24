__all__ = ['create_pkg']

import argparse
import os.path,os
import sys
from pprint import pprint
import string
import datetime

from .FedoraPackage import RPMPackage
from .utils import getConfig,configParser

PACKAGE_TYPES = ['R','nodejs']

sourcesTemplate = string.Template("x    $srcpkgname  $srcpkgurl\n")

specfileDefaultTemplate = string.Template("""Summary: 
Name: $pkgname
Version: $version
Release: $release
Packager: $packager
Distribution: $distribution

License: 
Group: 
URL: 
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description

%prep
%setup -q

%build

%install
rm -rf $$RPM_BUILD_ROOT

%clean
rm -rf $$RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc


%changelog
* $date $packager - 
- Initial build.

""")

specfileRTemplate = string.Template("""%global packname  $rpkgname
%global packver   $version
$rreleaseMacro

Summary: 
Name: $pkgname
Version: $rpkgversion
Release: $release
Packager: $packager
Distribution: $distribution

License: 
Group: Applications/Engineering
URL:              http://cran.r-project.org/web/packages/%{packname}/index.html
%if 0%{?packrel:1}
Source0:          http://cran.r-project.org/src/contrib/%{packname}_%{packver}-%{packrel}.tar.gz
%else
Source0:          http://cran.r-project.org/src/contrib/%{packname}_%{packver}.tar.gz
%endif
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
#BuildArch:        noarch

Requires:         R-core >= $rversion
BuildRequires:    R-devel >= 2.0.0
Requires(post):   R, R-core
Requires(postun): R, R-core

%description

%ifarch noarch
%define rdir %{_datadir}
%else
%define rdir %{_libdir}
%endif

%prep
%setup -c -q -n %{packname}

%build

%install
%{__rm} -rf %{buildroot}

mkdir -p %{buildroot}%{rdir}/R/library
R CMD INSTALL %{packname} -l %{buildroot}%{rdir}/R/library 
# Clean up in advance of check
test -d %{packname}/src && (cd %{packname}/src; rm -f *.o *.so)
%{__rm} -rf %{buildroot}%{rdir}/R/library/R.css
%{__rm} -rf %{buildroot}%{rdir}/R/library/%{packname}/latex

%check
# you might need to comment out the next line to avoid circular dependencies
%{_bindir}/R CMD check %{packname}

%clean
%{__rm} -rf %{buildroot}

%post
if [ -x %{_R_make_search_index} ]; then %{_R_make_search_index}; fi

%postun
if [ -x %{_R_make_search_index} ]; then %{_R_make_search_index}; fi

%files
%defattr(-, root, root, -)
%dir %{rdir}/R/library/%{packname}
%doc %{rdir}/R/library/%{packname}/html
%doc %{rdir}/R/library/%{packname}/DESCRIPTION
%doc %{rdir}/R/library/%{packname}/CITATION
%{rdir}/R/library/%{packname}/NAMESPACE
%{rdir}/R/library/%{packname}/INDEX
%{rdir}/R/library/%{packname}/Meta
%{rdir}/R/library/%{packname}/R
%{rdir}/R/library/%{packname}/help
%{rdir}/R/library/%{packname}/libs
%{rdir}/R/library/%{packname}/data

%changelog
* $date $packager - 
- Initial build.
""")


class DefaultPackage(RPMPackage):
    template = specfileDefaultTemplate
    
    def __init__(self,cfg,packageName,version):
        self._version = version

        super().__init__(cfg,packageName)
        # make sure repo exists
        self.repo

    @property
    def version(self):
        return self._version
    def get_srcpkgurl(self):
        return ''
    def get_srcpkgname(self):
        name = self.name
        if self.version != '':
            name += '-' + self.version
        name += '.tar.gz'
        return name

    def get_substDict(self):
        substDict = {
            'pkgname' : self.get_pkgname(),
            'date' : datetime.date.strftime(datetime.date.today(),"%a %b %d %Y"),
            'distribution' : self.cfg['distribution'],
            'release' : '1.'+self.cfg['unit'],
            'packager' : self.cfg['packager'],
            'version' : self.version,
            }
        return substDict
    
    def create_spec(self):
        sname = os.path.join(self.local_repo_path,self.specname)
        if not os.path.exists(sname):
            open(sname,'w').write(self.template.substitute(self.get_substDict()))
            self.repo.index.add([os.path.basename(sname)])
            
    def create_sources(self):
        sname = os.path.join(self.local_repo_path,'sources')
        if not os.path.exists(sname):
            open(sname,'w').write(sourcesTemplate.substitute(
                srcpkgname=self.get_srcpkgname(),
                srcpkgurl=self.get_srcpkgurl()))
            self.repo.index.add([os.path.basename(sname)])

class NodeJSPackage(DefaultPackage):
    pass
    
class RPackage(DefaultPackage):
    template = specfileRTemplate
    
    def __init__(self,cfg,packageName,version,release):
        self._release = release
        super().__init__(cfg,packageName,version)

    @property
    def release(self):
        return self._release
    def get_pkgname(self):
        return 'R-'+self.name
    def get_srcpkgurl(self):
        return 'http://cran.r-project.org/src/contrib/'
    def get_srcpkgname(self):
        name = self.name
        if self.version != '':
            name += '_' + self.version
        if self.release != '':
            name += '-' + self.release
        name += '.tar.gz'
        return name
    def get_substDict(self):
        substDict = super().get_substDict()
        substDict['rrelease'] = self.release
        substDict['rpkgname'] = self.name
        substDict['rpkgversion'] = self.version
        substDict['rreleaseMacro'] = ''
        if self.release != '':
            substDict['rreleaseMacro'] = '%global packrel '+self.release
            substDict['rpkgversion'] += '.'+self.release
            
        substDict['rversion'] = self.cfg['R_version']
            
        return substDict
    
def create_pkg():
    parser = argparse.ArgumentParser(parents=[configParser()])
    parser.add_argument('package',help='name of package to be created')
    parser.add_argument("-p","--package-type",choices=PACKAGE_TYPES,
help="specify the type of package can be one of %s"%str(PACKAGE_TYPES))
    parser.add_argument("-v","--version",default="",help="specify the version of the package")
    parser.add_argument("-r","--r-release",default="",help="the R release number")

    args = parser.parse_args()

    cfg = getConfig(args,args.config)
    if args.print_config:
        pprint(cfg)
        sys.exit(0)
    
    if args.package_type is None:
        package = DefaultPackage(cfg,args.package,args.version)
    elif args.package_type == 'R':
        package = RPackage(cfg,args.package,args.version,args.r_release)
    elif args.package_type == 'nodejs':
        package = NodeJSPackage(cfg,args.package,args.version)

    package.create_sources()
    package.create_spec()
    package.create_Makefile()
    package.commit('created initial package')
    package.repo.heads.master.rename(package.local_branch_name)
    package.push()
    
if __name__ == '__main__':
    create_pkg()
