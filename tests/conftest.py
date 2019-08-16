"""pytest config"""

import os
from datetime import datetime
from uuid import uuid4

import pytest
from botocore.exceptions import ClientError
from webtest import TestApp

from bmarks import create_app, dynamo


@pytest.fixture
def app(dynamodb):  # pylint: disable=unused-argument
    """yield application as pytest fixture"""

    os.environ['DYNAMO_ENABLE_LOCAL'] = 'True'
    os.environ['DYNAMO_LOCAL_HOST'] = '127.0.0.1'
    os.environ['DYNAMO_LOCAL_PORT'] = '64222'
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
def test_link(app):  # pylint: disable=unused-argument,redefined-outer-name
    """database persisted test link"""

    link = {'id': str(uuid4()), 'link': 'https://example.org/linkx', 'tags': ['test'], 'created': datetime.utcnow().isoformat()}
    dynamo.tables['links'].put_item(Item=link)
    yield link
