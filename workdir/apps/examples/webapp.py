from pyicub.iCubHelper import iCub, JointPose, ICUB_PARTS

class WebApp:

    def __init__(self):
        self.icub = iCub(http_server=True)
        self.a = JointPose(ICUB_PARTS.HEAD, target_position=[-15.0, 20.0, 5.0, 0.0, 0.0, 5.0])
        self.b = JointPose(ICUB_PARTS.HEAD, target_position=[0.0, 0.0, 0.0, 0.0, 0.0, 5.0])
        self.icub.http_manager.register(target=self.foo, rule_prefix="mywebapp")

    def foo(self, req_time):
        self.icub.move(self.a, req_time=req_time)
        self.icub.move(self.b, req_time=req_time)
        return 1

a = WebApp()
input()
