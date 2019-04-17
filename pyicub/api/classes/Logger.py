#   Copyright (C) 2019  Davide De Tommaso
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>

import sys
import yarp

class YarpLogger:

    DEBUG = "DEBUG"
    ERROR = "ERROR"
    NONE = "NONE"

    def __init__(self, logtype=NONE):
        self.__logtype__ = logtype
        if not self.__logtype__ is YarpLogger.NONE:
            self.__yarp_logger__ = yarp.Log()

    def error(self, msg):
        if self.__logtype__ is YarpLogger.DEBUG or self.__logtype__ is YarpLogger.ERROR:
            self.__yarp_logger__.info(msg)

    def warning(self, msg):
        if self.__logtype__ is YarpLogger.DEBUG:
            self.__yarp_logger__.warning(msg)

    def debug(self, msg):
        if self.__logtype__ is YarpLogger.DEBUG:
            self.__yarp_logger__.debug(msg)
