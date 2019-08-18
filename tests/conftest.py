"""pytest config"""

import os
from datetime import datetime
from uuid import uuid4

import pytest
from botocore.exceptions import ClientError
from flask import url_for
from webtest import TestApp

from bmarks import create_app, dynamo, TABLE_NAME


@pytest.fixture
def app(dynamodb):  # pylint: disable=unused-argument
    """yield application as pytest fixture"""

    os.environ['DYNAMO_ENABLE_LOCAL'] = 'True'
    os.environ['DYNAMO_LOCAL_HOST'] = '127.0.0.1'
    os.environ['DYNAMO_LOCAL_PORT'] = '64222'
    os.environ['PASSWORD'] = 'atestpassword'

    _app = create_app()
    with _app.test_request_context():
        # dynamodb fixture should cleanup all tables automatically, but it does not
        try:
            dynamo.destroy_all()
        except ClientError:
            pass
        dynamo.create_all()
        yield _app


@pytest.fixture
def client(app):  # pylint: disable=redefined-outer-name
    """yield client test context"""
    yield TestApp(app)


@pytest.fixture
def cl_user(client):  # pylint: disable=redefined-outer-name
    """yield logged in app client"""

    form = client.get(url_for('app.login_route')).form
    form['password'] = os.environ['PASSWORD']
    form.submit()
    yield client


@pytest.fixture
def test_link(app):  # pylint: disable=unused-argument,redefined-outer-name
    """database persisted test link"""

    link = {'id': str(uuid4()), 'link': 'https://example.org/linkx', 'tags': ['test'], 'created': datetime.utcnow().isoformat()}
    dynamo.tables[TABLE_NAME].put_item(Item=link)
    yield link
