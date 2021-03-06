""" TO USE:
Import this file into a directory to be used in your command line interfance (e.g., terminal on mac, cmd.exe on windows)
Make sure you are in the directory, and then start Jupyter notebook or Jupyter lab / any other Python instance from there
and import as any other module.
"""
from .convert import convert_all
from .convert import convertGRB
from .convert import get_dir
from .convert import set_dir
from .convert import toFlux
from .time import dec_to_UT
from .time import grb_to_date
from .time import UT_to_dec
