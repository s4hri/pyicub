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

from pyicub.actions import ActionsManager
from pyicub.helper import iCub

import argparse

def main():
    parser = argparse.ArgumentParser(description="PyiCub Actionizer")

    subparsers = parser.add_subparsers(dest="command", help="Choose 'build' or 'run'.")

    build_parser = subparsers.add_parser("build", help="Build process")
    build_parser.add_argument("--module", nargs="+", required=True, help="Module name")
    build_parser.add_argument("--target", nargs="+", required=True, help="Target path")

    execute_parser = subparsers.add_parser("run", help="Running process")
    execute_parser.add_argument("--actions", nargs="+", required=True, help="List of actions to process (action id)")
    execute_parser.add_argument("--source", nargs="+", required=True, help="Source path JSON repository")

    args = parser.parse_args()

    if args.command == "build":
        mgr = ActionsManager()
        mgr.importActionsFromModule(args.module[0])
        mgr.exportActions(args.target[0])
    elif args.command == "run":
        icub = iCub(action_repository_path=args.source[0])
        for action in args.actions:
            icub.playAction(action)
    else:
        print("Invalid command. Choose 'build' or 'run'.")
    

if __name__ == "__main__":
    main()