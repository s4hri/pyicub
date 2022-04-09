#!/bin/bash

source ${ROBOTOLOGY_SUPERBUILD_INSTALL_DIR}/share/robotology-superbuild/setup.sh

YARP_FORWARD_LOG_ENABLE=0 yarpserver --write --ip $ICUBSRV_IP &
sleep 1

if ! $ICUB_SIMULATION ; then
  sshpass -p $ICUB_PSW ssh -o StrictHostKeyChecking=no $ICUB_USER@$ICUB_IP "yarprun --server /"$ICUB_HOST" --log &" &
fi

yarprun --server /$ICUBSRV_HOST --log &

yarpmanager --apppath ${ICUB_APPS}

if ! $ICUB_SIMULATION ; then
  sshpass -p $ICUB_PSW ssh -o StrictHostKeyChecking=no $ICUB_USER@$ICUB_IP "killall -9 yarprun"
  sshpass -p $ICUB_PSW ssh -o StrictHostKeyChecking=no $ICUB_USER@$ICUB_IP "killall -9 yarpdev"
fi
