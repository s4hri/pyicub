import os
import yaml

from pykron.core import Pykron


class AppConfigurator:

    _instance = None
    pykron = None

    @staticmethod
    def getInstance():
        if AppConfigurator._instance == None:
            AppConfigurator()
        return AppConfigurator._instance

    def __init__(self, logging_level=Pykron.LOGGING_LEVEL,
                       logging_format=Pykron.FORMAT,
                       logging_file=False,
                       logging_path=Pykron.LOGGING_PATH,
                       save_csv=False,
                       profiling=False):

        if AppConfigurator._instance != None:
            raise Exception("This class is a singleton!")
        else:
            AppConfigurator._instance = self
            AppConfigurator.pykron = Pykron(logging_level, logging_format, logging_file, logging_path, save_csv, profiling)
