export PYTHONPATH="$PYTHONPATH:../env/lib/python3.8/site-packages" # Change to the location where you have your packages installed
sphinx-apidoc --force -o . ../src
make clean
make html
