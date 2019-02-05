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
