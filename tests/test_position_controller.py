# BSD 2-Clause License
#
# Copyright (c) 2025, Social Cognition in Human-Robot Interaction,
#                     Istituto Italiano di Tecnologia, Genova
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import pytest
import numpy as np
import time
from pyicub.helper import iCub, JointPose, LimbMotion, ICUB_HEAD, ICUB_EYES, ICUB_NECK
from pyicub.controllers.position import PositionController

class TestPositionController:
    """
    Integration tests for the general PositionController class.
    """

    @classmethod
    def setup_class(self):
        """Setup common resources for tests."""
        self.icub = iCub()

    @classmethod
    def teardown_class(self):
        """Cleanup resources."""
        self.icub.close()

    def verify_encoders(self, controller, pose, tolerance=5.0):
        """
        Verify that the controller's encoders match the expected pose.

        Parameters
        ----------
        controller : PositionController
            The controller instance to check.
        pose : JointPose
            The expected target joint pose.
        tolerance : float
            Acceptable difference between expected and actual joint values (in degrees).
        """

        mismatches = controller.verify_encoders(pose, tolerance)
        if mismatches:
            mismatch_str = "\n".join(
                f"Joint {j}: actual={a:.2f}, target={t:.2f}, diff={d:.2f}" 
                for j, a, t, d in mismatches
            )
            raise AssertionError(
                f"Joint position mismatch in {controller.__part__.name}:\n{mismatch_str}"
            )

    @pytest.mark.integration
    def test_move_to_pose_and_home(self):
        """Test moving the head to an up pose and back home using explicit move and verify steps."""
        up = JointPose(target_joints=[20.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        home = JointPose(target_joints=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        
        head_ctrl = self.icub.getPositionController(ICUB_HEAD)
        
        # Move to "up" pose
        success_up = head_ctrl.move(up)
        assert success_up, "Head failed to move to 'up' pose"
        self.verify_encoders(head_ctrl, up)

        # Move to "home" pose
        success_home = head_ctrl.move(home)
        assert success_home, "Head failed to move to 'home' pose"
        self.verify_encoders(head_ctrl, home)



    @pytest.mark.integration
    def test_move_part(self):
        """Test sequential movement of head and eyes using predefined trajectories."""
        
        neck_ctrl = self.icub.getPositionController(ICUB_NECK)
        eyes_ctrl = self.icub.getPositionController(ICUB_EYES)

        # Define head poses
        neck_up = JointPose(target_joints=[20.0, 0.0, 0.0])
        neck_down = JointPose(target_joints=[-20.0, 0.0, 0.0])
        neck_home = JointPose(target_joints=[0.0, 0.0, 0.0])

        # Define eyes poses
        eyes_left = JointPose(target_joints=[0.0, 20.0, 5.0])
        eyes_right = JointPose(target_joints=[0.0, -20.0, 5.0])
        eyes_home = JointPose(target_joints=[0.0, 0.0, 0.0])

        # Create motion sequences
        neck_motion = LimbMotion(ICUB_NECK)
        neck_motion.createJointsTrajectory(neck_up)
        neck_motion.createJointsTrajectory(neck_down)

        eyes_motion = LimbMotion(ICUB_EYES)
        eyes_motion.createJointsTrajectory(eyes_left)
        eyes_motion.createJointsTrajectory(eyes_right)

        # Execute motions
        self.icub.movePart(neck_motion)
        self.icub.movePart(eyes_motion)

        self.verify_encoders(neck_ctrl, neck_down)
        self.verify_encoders(eyes_ctrl, eyes_right)

        neck_ctrl.move(neck_home)
        self.verify_encoders(neck_ctrl, neck_home)

        eyes_ctrl.move(eyes_home)
        self.verify_encoders(eyes_ctrl, eyes_home)
