venv:
	sudo apt-get -y install python-virtualenv python3-virtualenv
	virtualenv -p python3 venv

install-deps:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

lint:
	python3 -m flake8 bmarks
	python3 -m pylint bmarks


zappa_settings:
	mkdir -p build
	extra/compile_template.py extra/zappa_settings.json.j2 aws_account_id=${AWS_ACCOUNT_ID} > build/zappa_settings.json

deploy:
	zappa deploy dev
