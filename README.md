# To Clone package(s)

run

$ python cloneGitRepos.py  <package_name_1>,<package_name_2>  -c <confige_filePath> (optional) -s <cloned_dir_path>(optional)

<package_name> can either be a name of package as it appear on https://src.fedoraproject.org/ or any git link


# To create Config file

run

$ python createMyConfig.py -u <git_url>(optional) -p <config_file_path>(optional) -rp<repo_path>(optional)

- git_url : GitLab(Git) group or user url
- config_file_path : path to save your /.autocloner.cfg at but by default it put it in $Home directore##
- repo_path : path to be saving cloned repos. By default it saves them in ./temp/


- Better if you set up ssh on your pc and use git url other than https, to avoid login every time you need to push or pull to your accountsg






