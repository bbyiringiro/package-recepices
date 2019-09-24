from setuptools import setup, find_packages

setup(
    name = "package-recipes",
    version = "0.1",
    packages = find_packages(),
    install_requires = [
        "gitpython",
    ],
    data_files=[
        ('share/package-recipes',["data/make.rules",]),
        ],
    entry_points={
        'console_scripts': [
            'pr-create = package_recipes:create_pkg',
            'pr-clone = package_recipes:cloneRepo',
            'pr-download = package_recipes:download_source',
            'pr-release = package_recipes:releasePkg',
            'pr-rpmfiles = package_recipes:get_rpmfiles',
        ],
    },

    # metadata for upload to PyPI
    author = "Magnus Hagdorn",
    description = "utility to clone fedora packages",
    license = "GPL",
    url = "https://git.ecdf.ed.ac.uk:uoe-package-recipes/package-recipes",
)
