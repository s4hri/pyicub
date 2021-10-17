from pyicub.iCubHelper import iCubHTTPRequestsManager
from pyicub.iCubHelper import iCub, JointPose, ICUB_PARTS

class WebApp:

    def __init__(self):
        self.icub = iCub()
        self.a = JointPose(ICUB_PARTS.HEAD, target_position=[-15.0, 20.0, 5.0, 0.0, 0.0, 5.0])
        self.b = JointPose(ICUB_PARTS.HEAD, target_position=[0.0, 0.0, 0.0, 0.0, 0.0, 5.0])
        self.webapp = iCubHTTPRequestsManager(rule_prefix="/mywebapp", port=1234)
        self.webapp.register(self.foo)


    def foo(self, req_time):
        self.icub.move(self.a, req_time=req_time)
        self.icub.move(self.b, req_time=req_time)
        return 1

WebApp()
