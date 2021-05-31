#!/bin/bash
export PATH=${PATH}:/home/docky/pyicub/apps/

# $1: simulation $2: icub user, $3: icub psw, $4: icub host, $5: yarpmanager apps folder

env_robot()
{
USER=$1
PASS=$2
HOST=$3
APPS=$4

SSH_ASKPASS_SCRIPT=/home/docky/ssh-pass.sh
cat > ${SSH_ASKPASS_SCRIPT} <<EOL
#!/bin/bash
echo "${PASS}"
EOL
chmod u+x ${SSH_ASKPASS_SCRIPT}
export SSH_ASKPASS=${SSH_ASKPASS_SCRIPT}

cat /dev/zero | ssh-keygen -t rsa

setsid ssh-copy-id -oStrictHostKeyChecking=no -f ${USER}@${HOST}
sleep 1

yarpserver --write &

sleep 3
SSH_ASKPASS=${SSH_ASKPASS_SCRIPT} setsid ssh -oStrictHostKeyChecking=no ${USER}@${HOST} "yarprun --server /pc104 --log &" &

yarprun --server /root --log &

yarpmanager --apppath ${APPS}/applications/ --from ${APPS}/cluster-config.xml

SSH_ASKPASS=${SSH_ASKPASS_SCRIPT} setsid ssh -oStrictHostKeyChecking=no ${USER}@${HOST} "kill -9 \$(ps -aux | grep yarprun | awk '{print \$2}')"
SSH_ASKPASS=${SSH_ASKPASS_SCRIPT} setsid ssh -oStrictHostKeyChecking=no ${USER}@${HOST} "kill -9 \$(ps -aux | grep yarpdev | awk '{print \$2}')"
}

env_sim()
{
APPS=$1

export YARP_FORWARD_LOG_ENABLE=1
yarpserver --write &
sleep 2
yarprun --server /root --log &

yarpmanager --apppath ${APPS}/applications/ --from ${APPS}/cluster-config.xml
}

if [ "$1" = true ]
then
  env_sim $5
else
  env_robot $2 $3 $4 $5
fi
exit
