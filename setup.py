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

__version__ = '1.3.10'

def download_files(libbase: str) -> None:
    try:
        ANARCI_LOC = os.path.dirname(importlib.util.find_spec("anarci").origin)
    except Exception as e:
        sys.stderr.write("Something isn't right. Aborting.")
        sys.stderr.write(str(e))
        # sys.exit(1)
        ANARCI_LOC = libbase

    # os.chdir("build_pipeline")

    print('anarci loc', os.listdir(ANARCI_LOC))

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
    try:
        os.symlink(os.path.join('bin', filename), os.path.join('bin', 'muscle'), False)
    except IOError:
        pass
class Install(install):

    def run(self):
        super().run()
        try:
            shutil.copy2('bin/muscle_linux', os.path.join(self.install_base, 'bin'))
            shutil.copy2('bin/muscle_macOS', os.path.join(self.install_base, 'bin'))
            link_muscle(self.install_base)
        except IOError:
            pass
        link_muscle(self.install_data)
        download_files(os.path.realpath(self.install_libbase))


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


