"""
Python 3.7.0
-> Logging system with 3 levels (info, warning, error)
Written by: Edgar Araújo (edgararaj@gmail.com)
Date (start): 13/07/2019
Date (latest modification):
"""


def info(msg):
    print("[INFO]: " + str(msg))


def warn(msg):
    print("[WARNING]: " + str(msg))


def error(msg):
    print("[ERROR]: " + str(msg))
