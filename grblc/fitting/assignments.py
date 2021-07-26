from convert import get_dir
from functools import reduce
import os, glob2
import numpy as np

assignments = {
    1: ["210411C", "210321A", "210210A", "210204A", "201024A", "201021C", "201020A", "201015A"],
    2: ["201014A", "200829A", "200613A", "200524A", "191019A", "191011A", "190627A", "190530A"],
    3: ["190114A", "181213A", "181201A", "181110A", "181020A", "181010A", "180728A", "180624A"],
    4: ["180404A", "180325A", "180205A", "180115A", "171010A", "170714A", "170607A", "170604A"],
    5: ["170405A", "170214A", "170113A", "161219B", "161129A", "161014A", "160804A", "160703A"],
    6: [
        "160623A",
        "160425A",
        "160314A",
        "160228A",
        "160227A",
        "160131A",
        "160121A",
        "151031A",
    ],
    7: [
        "151029A",
        "151027A",
        "150818A",
        "150727A",
        "150518A",
        "150514A",
        "150413A",
        "150323A",
    ],
    8: [
        "150206A",
        "141225A",
        "141220A",
        "141121A",
        "141028A",
        "141026A",
        "141004A",
        "140907A",
    ],
    9: [
        "140808A",
        "140801A",
        "140710A",
        "140703A",
        "130418A",
        "121229A",
        "121212A",
    ],
    10: [
        "140614A",
        "140518A",
        "140509A",
        "140508A",
        "140428A",
        "140423A",
        "140318A",
        "140304A",
        "140301A",
    ],
    11: [
        "140213A",
        "140206A",
        "131103A",
        "131011A",
        "131004A",
        "130518A",
        "130511A",
        "130420A",
    ],
    12: [
        "121209A",
        "121201A",
        "121128A",
        "121027A",
        "120907A",
    ],
    13: [
        "120811C",
        "120802A",
        "120724A",
        "120716A",
        "120712A",
        "120422A",
        "120327A",
        "120311A",
    ],
    14: [
        "120308A",
        "111229A",
        "111211A",
        "111129A",
        "111107A",
        "111008A",
        "110801A",
        "110503A",
    ],
    15: [
        "110422A",
        "110128A",
        "100802A",
        "100728A",
        "100724A",
        "100518A",
        "100513A",
        "100508A",
    ],
    16: [
        "100425A",
        "100302A",
        "091109",
        "091003",
        "090926",
        "090814",
        "090809",
        "090530",
    ],
    17: [
        "090529",
        "090516",
        "090205",
        "090113",
        "081230",
        "081203",
        "081109",
        "081028",
    ],
    18: [
        "080916",
        "080703",
        "080604",
        "080603",
        "080520",
        "080411",
        "080325",
        "080319B",
    ],
    19: [
        "080307",
        "080212",
        "080205",
        "080129",
        "070506",
        "060607",
        "060604",
        "060522",
    ],
    20: [
        "060502",
        "060223",
        "050820",
        "050713",
        "050525",
        "050502B",
        "050502",
        "041219",
    ],
    21: ["031203", "020305", "020124", "010921", "980326"],
}


def get_assignment(n):
    if n in assignments:
        # Look at LCs and go through outliers BEFORE cleaning
        assignment = assignments[n]
        glob_path = glob2.glob(reduce(os.path.join, [get_dir(), "*_flux", "*_converted_flux.txt"]))
        finals = []
        for filepath in glob_path:
            grb = os.path.split(filepath)[-1].rstrip("_converted_flux.txt")
            if grb in assignment:
                finals.append(filepath)
        return finals


def locate(grb):
    if isinstance(grb, (list, tuple)):
        paths = np.concatenate(
            [glob2.glob(reduce(os.path.join, [get_dir(), "*_flux", f"{name}_converted_flux.txt"])) for name in grb]
        )

    else:
        paths = glob2.glob(os.path.join, [get_dir(), "*_flux", f"{grb}_converted_flux.txt"])

    if isinstance(paths, list):
        return paths  # we want to return a list!
    else:
        raise ImportError(f"GRB {grb} not found.")
