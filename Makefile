install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

setup:
	apt-get install python3-venv
	python3 -m venv ~/env


test:
	#python -m pytest -vv test_hello.py

format:
	#black *.py


lint:
	#pylint --disable=R,C hello.py

All: install lint test
