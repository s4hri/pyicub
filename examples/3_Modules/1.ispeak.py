# BSD 2-Clause License
#
# Copyright (c) 2022, Social Cognition in Human-Robot Interaction,
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



"""
1.ispeak.py
==================

This script contains examples for speech module of PyiCub.

Usage:
------
Run this script to make iCub speak from a string, a text file, and a file chosen at random from a folder. 

Before running this script, it is necessary to run the required YARP modules in separated terminals:
>>> iSpeak

>>> yarpdev --device speech --lingware-context speech --default-language en-US --pitch 120 --speed 100 --robot icubSim

>>> yarp connect /iSpeak/speech-dev/rpc /icubSim/speech:rpc

"""

from pyicub.helper import iCub
from pyicub.core.logger import YarpLogger
import os

def example_speech_say(icub):
    return icub.speech.say("Hi, I'm iCub! I'm reading from a string.")

def example_speech_say_from_file(icub):
    # create text file to read
    filename = "__tmp_example_speech_say_from_file.txt"
    with open(filename, 'w') as f:
        f.write("Hi, I'm iCub! I'm reading from a text file.")
    abs_file_path = os.path.abspath(filename)

    # read the file
    res = icub.speech.say_from_file(abs_file_path, wait_action_done=True)

    # clean
    os.remove(abs_file_path)
    return res





def example_speech_say_from_folder_rnd(icub):
    # create the folder to read from
    folder = "__tmp_folder_example_speech_say_from_folder_rnd"

    os.makedirs(folder)
    abs_folder_path = os.path.abspath(folder)

    tmp_abs_file_paths = [] 
    for i in range(5):
        filename = f"{str(i).zfill(2)}.txt"
        
        abs_file_path = os.path.join(abs_folder_path, filename)
        with open(abs_file_path, 'w') as f:
            f.write(f"Hi, I'm iCub! I'm reading from {filename} file chosen at random from a folder.")
            
        tmp_abs_file_paths.append(abs_file_path)
    
    # read a file chosen at random from a folder
    res = icub.speech.say_from_folder_rnd(abs_folder_path, random_seed=0, wait_action_done=True)

    # clean
    for abs_file_path in tmp_abs_file_paths:
        os.remove(abs_file_path)
    
    os.rmdir(abs_folder_path)

    return res




if __name__ == "__main__":
    logger = YarpLogger.getLogger()
    icub = iCub()

    logger.info(f"Running example icub.speech.say()")
    res = example_speech_say(icub)
    logger.info(f"End example icub.speech.say(). {res=}")

    logger.info(f"Running example icub.speech.say_from_file()")
    res = example_speech_say_from_file(icub)
    logger.info(f"End example icub.speech.say_from_file(). {res=}")

    logger.info(f"Running example icub.speech.say_from_folder_rnd()")
    res = example_speech_say_from_folder_rnd(icub)
    logger.info(f"End example icub.speech.say_from_folder_rnd(). {res=}")

    

