"""bmarks basic tests"""

import json
import os
from http import HTTPStatus

from flask import url_for

from bmarks import dynamo


def get_csrf_token(client):
    """fetch index and parse csrf token"""

    response = client.get(url_for('app.index_route'))
    return response.lxml.xpath('//meta[@name="csrf-token"]/@content')[0]


def test_login_route(client):
    """login test"""

    form = client.get(url_for('app.login_route', next=url_for('app.index_route'))).form
    form['password'] = os.environ['PASSWORD']
    response = form.submit()
    assert response.status_code == HTTPStatus.FOUND
    response = response.follow()
    assert response.lxml.xpath('//a[text()="Logout"]')


def test_logout_route(cl_user):
    """logout test"""

    response = cl_user.get(url_for('app.logout_route'))
    assert response.status_code == HTTPStatus.FOUND
    response = response.follow()
    assert response.lxml.xpath('//a[text()="Login"]')


def test_index_route(client):
    """index test"""

    response = client.get(url_for('app.index_route'))
    assert response.status_code == HTTPStatus.OK


def test_index_json_route(client, test_link):
    """test index json"""

    response = client.get(url_for('app.index_json_route'))
    data = json.loads(response.body.decode('utf-8'))['data']
    assert len(data) == 1
    assert data[0]['id'] == test_link['id']


def test_add_route(cl_user):
    """test add route"""

    test_link = {'link': 'atestlink', 'tags': ['dev', 'aws']}

    form = cl_user.get(url_for('app.add_route')).form
    form['link'] = test_link['link']
    form['tags'] = ','.join(test_link['tags'])
    response = form.submit()
    assert response.status_code == HTTPStatus.FOUND

    data = dynamo.tables['links'].scan()['Items']
    assert len(data) == 1
    assert data[0]['link'] == test_link['link']
    assert sorted(data[0]['tags']) == sorted(test_link['tags'])


def test_edit_route(cl_user, test_link):
    """test edit route"""

    form = cl_user.get(url_for('app.edit_route', link_id=test_link['id'])).form
    form['link'] = form['link'].value + '_edited'
    form['tags'] = form['tags'].value + 'edited'
    response = form.submit()
    assert response.status_code == HTTPStatus.FOUND

    link = dynamo.tables['links'].get_item(Key={'id': test_link['id']})['Item']
    assert link['link'] == form['link'].value
    assert sorted(link['tags']) == sorted(form['tags'].value.split(','))


def test_toggleread_route(cl_user, test_link):
    """test toggleread route"""

    csrf_token = get_csrf_token(cl_user)

    response = cl_user.post(url_for('app.toggleread_route', link_id=test_link['id']), {'csrf_token': csrf_token})
    assert response.status_code == HTTPStatus.FOUND
    link = dynamo.tables['links'].get_item(Key={'id': test_link['id']})['Item']
    assert 'read' in link['tags']

    response = cl_user.post(url_for('app.toggleread_route', link_id=test_link['id']), {'csrf_token': csrf_token})
    assert response.status_code == HTTPStatus.FOUND
    link = dynamo.tables['links'].get_item(Key={'id': test_link['id']})['Item']
    assert 'read' not in link['tags']


def test_delete_route(cl_user, test_link):
    """test delete route"""

    csrf_token = get_csrf_token(cl_user)
    response = cl_user.post(url_for('app.delete_route', link_id=test_link['id']), {'csrf_token': csrf_token})
    assert response.status_code == HTTPStatus.FOUND
    assert not dynamo.tables['links'].scan()['Items']
