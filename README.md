As part of my Student Experience post in Information Services Group at the University of Edinburgh, I develop this tool which includes utilities to handle package-recipes rpm projects from Fedora (https://src.fedoraproject.org/). It helps develop make copies the Fedora projects(but can be configured to other git repos as well) projects and make contributions flow seamless by automating pushing and pulling to different git repos you configured.

Installation
============

Create Virtual Environment
```
virtualenv-3 --system-site-packages /some/dir
```
and activate it
```
. /some/dir/bin/activate
```
Download the package recipes sources by cloneing the repository
```
git clone git@github.com:billyjason/package-recepices.git
```

The package uses python3 and requires the gitpython package. Run
```
python setup.py install
```
to install the package.

Configuration
=============
Create a ~/.package-recipes.cfg file with the following content
```
[config]
local_path = /some/directory/where/the/local/repos/are
project_url = ${GIT_DIR_URL}
upstream_branch = f19
unit = ${BRANCH} # used for branch names and releases
packager = ${USER}
distribution = el7
```

Workflow
========
* identify a package you want to clone from Fedora (https://src.fedoraproject.org/)  and run
```
pr-clone package-name
```
   you might want to specify a particular Fedora branch you want to use as basis for your changes.
* change the sources file to include a URL where to download the source files and make any changes to the spec file
* run
```
make build
```
   to generate the source rpm and run mock to build the packge
* if everything works commit your changes
* run
```
make up
```
   to generate a file containing the list of rpms to be uploaded. In the case where some files did not get generated a warning is issues and you should check the rpm list.
* upload rpms
```
mdp-package-submit -b ... -d el7 @up
```
* create a release tag
```
make release
```
The tag gets printed. Make sure it is sensible.
* push changes to package recipe project. You need to push both the branch and tag, eg
```
git push origin geos_el7; git push origin el7_2.18.20_2_3.geos
```
* in project settings make project internal

Utilities
=========

pr-create
---------
Utiltiy to create a new rpm package.

pr-clone
---------
Utility used to clone package sources from the Fedora project. Run with the -h flag to get some help. Run pr-clone pkg, eg
```
pr-clone python-pillow
```
The utility will
* create an upstream remote
* modify the spec file to include extra UoE fields and update the changelog
* add a Makefile

It creates a unit specific branch and commits the changes. Finally, the changes are pushed to the gitlab project.

pr-download
-----------
download a source file and check md5 sum

pr-release
----------
create a release tag

pr-rpmfiles
-----------
query the spec file to figure out what files have been created and list them in a file. 
