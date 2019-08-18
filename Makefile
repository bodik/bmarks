.PHONY: all install-deps dynamo devserver lint test coverage zappa_settings deploy

all: lint coverage

# install
venv:
	sudo apt-get -y install python-virtualenv python3-virtualenv
	virtualenv -p python3 venv

install-deps:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

build/dynamodb/DynamoDBLocal.jar:
	rm -f /tmp/dynamodb_local_latest.tar.gz
	wget --no-verbose -O /tmp/dynamodb_local_latest.tar.gz https://s3.eu-central-1.amazonaws.com/dynamodb-local-frankfurt/dynamodb_local_latest.tar.gz
	mkdir -p build/dynamodb
	tar xzf /tmp/dynamodb_local_latest.tar.gz -C build/dynamodb

dynamo: build/dynamodb/DynamoDBLocal.jar
	cd build/dynamodb && screen -S dynamo -d -m java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar


# development
devserver:
	FLASK_APP=bmarks:create_app FLASK_DEBUG=1 flask run --host 0.0.0.0 --port 19000

lint:
	python3 -m flake8 bmarks tests/
	python3 -m pylint bmarks tests/

test:
	python3 -m pytest

coverage:
	coverage run --source bmarks -m pytest tests/ -x -vv
	coverage report --show-missing --fail-under 100


# deployment
zappa_settings:
	mkdir -p build
	extra/compile_template.py extra/zappa_settings.json.j2 aws_account_id=${AWS_ACCOUNT_ID} secret_key=${SECRET_KEY} password=${PASSWORD} > build/zappa_settings.json

deploy:
	zappa deploy dev
