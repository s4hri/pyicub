from pyicub.rest import iCubRESTApp
from pyicub.utils import getPublicMethods
import time
import inspect

app = iCubRESTApp()
app.rest_manager.run_forever()