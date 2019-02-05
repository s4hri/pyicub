# Run all the unit tests
#
# $ sh run_all_unittests.sh

cd unit
python -m unittest discover . -v
cd ..