#!/usr/bin/env python3

#                               #
# Developed by James Dunbar     #
# Maintained by members of OPIG #
#                               #

import importlib
import os
import shutil
import subprocess
import sys

# Clean this out if it exists
if os.path.isdir("build"):
    shutil.rmtree("build/")

from distutils.core import setup

from setuptools.command.install import install

__version__ = '1.3.10'

def download_files() -> None:
    try:
        # setuptools will install lib directly into final location before finishing build
        # so we need to take path, where anarci was already moved
        ANARCI_LOC = os.path.dirname(importlib.util.find_spec("anarci").origin)
    except Exception as e:
        sys.stderr.write(f"Non setup.py install detected. Setting anarci loc to {os.getcwd()}")
        # sys.exit(1)
        # if using setuptools meta build, then before moving anarci, it will be installed into a temp dir.
        # All data will be copied into final destination after full build is performed. 
        # Here we are setting it to our temporary build dir
        ANARCI_LOC = os.getcwd()

    try:
        # shutil.rmtree("curated_alignments/")
        # shutil.rmtree("muscle_alignments/")
        shutil.rmtree("HMMs/")
        # shutil.rmtree("IMGT_sequence_files/")
        os.mkdir(os.path.join(ANARCI_LOC, "dat"))
    except OSError:
        pass

    print('Downloading germlines from IMGT and building HMMs...')
    proc = subprocess.Popen(["bash", "RUN_pipeline.sh"], stdout = subprocess.PIPE, stderr = subprocess.PIPE, cwd="build_pipeline")
    out, err = proc.communicate()

    print(out.decode())
    if proc.returncode != 0:
        raise RuntimeError(err.decode())
    else:
        print(err.decode())

    shutil.copy( "build_pipeline/curated_alignments/germlines.py", ANARCI_LOC )
    hmms_loc = os.path.join(ANARCI_LOC, "dat/HMMs/")
    if os.path.exists(hmms_loc):
        shutil.rmtree(hmms_loc)
    shutil.copytree("build_pipeline/HMMs", hmms_loc)

def link_muscle(bin_path: str) -> None:
    filename = 'muscle_macOS' if sys.platform == 'darwin' else 'muscle_linux'
    bin_path = os.path.join(bin_path, 'bin')
    print('linking muscle for your platform', os.path.join(bin_path, filename), '->', os.path.join(bin_path, 'muscle'))
    os.symlink(os.path.join(bin_path, filename), os.path.join(bin_path, 'muscle'), False)
class Install(install):

    def run(self):
        # link muscle for current platform.
        # setuptools then will copy correct file using data_files attribute
        link_muscle(os.getcwd())
        super().run()
        download_files()


setup(name='anarci',
      version=__version__,
      description='Antibody Numbering and Receptor ClassIfication',
      author='James Dunbar',
      author_email='opig@stats.ox.ac.uk',
      url='http://opig.stats.ox.ac.uk/webapps/ANARCI',
      packages=['anarci'], 
      package_dir={'anarci': 'lib/python/anarci'},
      package_data={'anarci': ['dat/HMMs/ALL.hmm',
                              'dat/HMMs/ALL.hmm.h3f',
                              'dat/HMMs/ALL.hmm.h3i',
                              'dat/HMMs/ALL.hmm.h3m',
                              'dat/HMMs/ALL.hmm.h3p']},
      scripts=['bin/ANARCI'],
      install_requires=['biopython>=1.78'],
      data_files = [ ('bin', ['bin/muscle_linux', 'bin/muscle_macOS', 'bin/muscle']) ],
      cmdclass={'install': Install}
     )


