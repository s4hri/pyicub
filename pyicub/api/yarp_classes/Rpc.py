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

import yarp
import logging

class RpcClient:

    def __init__(self, rpc_server_name):
        self.__rpc_client__ = yarp.RpcClient()
        self.__rpc_client_port_name__ = rpc_server_name + "/rpc_client/commands"
        self.__rpc_client__.open(self.__rpc_client_port_name__)
        logging.debug("Connecting %s with %s" % (self.__rpc_client_port_name__, rpc_server_name))
        res = self.__rpc_client__.addOutput(rpc_server_name)
        logging.debug("Result: %s" % res)


    def execute(self, cmd):
        ans = yarp.Bottle()
        logging.debug("Executing RPC command %s" % cmd.toString())
        res = self.__rpc_client__.write(cmd, ans)
        logging.debug("Result: %s" % ans.toString())
        return ans


    def __del__(self):
        self.__rpc_client__.interrupt()
        self.__rpc_client__.close()
