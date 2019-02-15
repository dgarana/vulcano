echo "1. Removing old distributables ..."
rm dist/*
echo "2. Creating python packages ..."
python3 setup.py sdist bdist_wheel
echo "3. Uploading to pip repository ..."
python3 -m twine upload dist/*
echo "Finished"
