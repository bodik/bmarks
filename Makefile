venv:
	sudo apt-get -y install python-virtualenv python3-virtualenv
	virtualenv -p python3 venv

install-deps:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

lint:
	python3 -m flake8 bmarks
	python3 -m pylint bmarks

deploy:
	zappa deploy dev
