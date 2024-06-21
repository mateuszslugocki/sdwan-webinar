import logging

from pyats.easypy import run


def main():
    logging.root.setLevel("INFO")
    testscript = {"testscript": "testscripts/bfd.py", "datafile": "datafiles/bfd.yaml"}

    run(**testscript)
