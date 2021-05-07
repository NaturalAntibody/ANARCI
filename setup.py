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
import traceback

# Clean this out if it exists
if os.path.isdir("build"):
    shutil.rmtree("build/")

from distutils.core import setup

from setuptools.command.install import install

__version__ = '1.3.9'

def download_files():
    try:
        ANARCI_LOC = os.path.dirname(importlib.util.find_spec("anarci").origin)
    except Exception as e:
        sys.stderr.write("Something isn't right. Aborting.")
        sys.stderr.write(str(e))
        sys.exit(1)

    os.chdir("build_pipeline")

    try:
        # shutil.rmtree("curated_alignments/")
        # shutil.rmtree("muscle_alignments/")
        shutil.rmtree("HMMs/")
        # shutil.rmtree("IMGT_sequence_files/")
        os.mkdir(os.path.join(ANARCI_LOC, "dat"))
    except OSError:
        pass

    print('Downloading germlines from IMGT and building HMMs...')
    proc = subprocess.Popen(["bash", "RUN_pipeline.sh"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = proc.communicate()

    print(out.decode())
    print(err.decode())

    shutil.copy( "curated_alignments/germlines.py", ANARCI_LOC )
    shutil.rmtree(os.path.join(ANARCI_LOC, "dat/HMMs/"))
    shutil.copytree( "HMMs", os.path.join(ANARCI_LOC, "dat/HMMs/") )

def link_muscle(base_path: str) -> None:
    filename = 'muscle_macOS' if sys.platform == 'darwin' else 'muscle_linux'
    bin_path = os.path.join(base_path, 'bin')
    print('linking muscle for your platform', os.path.join(bin_path, filename), '->', os.path.join(bin_path, 'muscle'))
    os.symlink(os.path.join(bin_path, filename), os.path.join(bin_path, 'muscle'), False)
class Install(install):

    def run(self):
        super().run()
        link_muscle(self.install_data)
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
      data_files = [ ('bin', ['bin/muscle_linux', 'bin/muscle_macOS']) ],
      cmdclass={'install': Install}
     )


