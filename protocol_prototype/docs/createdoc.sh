export PYTHONPATH="$PYTHONPATH:../env/lib/python3.8/site-packages"
sphinx-apidoc --force -o . ../src
make clean
make html
