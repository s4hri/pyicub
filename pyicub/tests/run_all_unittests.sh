# Run all the unit tests
#
# $ sh run_all_unittests.sh

export YARP_FORWARD_LOG_ENABLE=1
cd unit
python -m unittest discover . -v
cd ..
