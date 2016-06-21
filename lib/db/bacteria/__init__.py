__author__ = 'hudaiber'

import sys
import os
sys.path.append('../')
from .. import DbClass

if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')
import global_variables as gv

def neighborhoods_path():

    _path = os.path.join(gv.project_data_path, 'Bacteria/genes_and_flanks/win_10/raw_nbr_files/')
    if os.path.exists(_path):
        return _path
    else:
        raise IOError("The neighborhoods path doesn't exist. Check the project data paths.")


def map_file_id2name():
    _db = DbClass()
    _db.cmd = """select id, name from bacteria_win10_files"""

    return {str(l[0]): l[1] for l in _db.retrieve()}


def map_name2file_id():
    _db = DbClass()
    _db.cmd = """select name, id from bacteria_win10_files"""

    return {str(l[0]): l[1] for l in _db.retrieve()}
