from pyicub.rest import iCubRESTServer
import sys
import os

def main():
    PYICUB_API_PROXY_HOST = os.getenv('PYICUB_API_PROXY_HOST')
    PYICUB_API_PROXY_PORT = os.getenv('PYICUB_API_PROXY_PORT')
    serv = iCubRESTServer(rule_prefix='pyicub', host=PYICUB_API_PROXY_HOST, port=PYICUB_API_PROXY_PORT)
    serv.run_forever()
    return 0

if __name__ == '__main__':
    try:
        ret = main()
    except (KeyboardInterrupt, EOFError):
        ret = 0
    sys.exit(ret)