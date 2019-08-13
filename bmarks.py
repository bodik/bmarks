#!/usr/bin/env python3
"""bmarks, bookmarking app"""

from datetime import datetime
from os import urandom
from uuid import uuid4

from flask import Flask, redirect, render_template, url_for
from flask_dynamo import Dynamo
from flask_wtf import FlaskForm
from flask_wtf.csrf import generate_csrf
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired

app = Flask(__name__)  # pylint: disable=invalid-name
app.config['SECRET_KEY'] = urandom(32)
app.config['DYNAMO_TABLES'] = [{
    'TableName': 'links',
    'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
    'AttributeDefinitions': [{'AttributeName': 'id', 'AttributeType': 'S'}],
    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
}]
# globaly enable flask_wtf csrf token helper
# least intrusive way to pass token into every view without enforcing csrf on all routes
app.add_template_global(name='csrf_token', f=generate_csrf)

dynamo = Dynamo(app)  # pylint: disable=invalid-name
table_links = dynamo.tables['links']


class ButtonForm(FlaskForm):
    """simple button form for csrf handling on non-data forms"""


class LinkForm(FlaskForm):
    """link form"""

    link = StringField('Link', [InputRequired()])
    submit = SubmitField('Save')


@app.route('/', methods=['GET'])
def index_route():
    """main index"""

    links = table_links.scan()['Items']
    return render_template('index.html', links=links)


@app.route('/add', methods=['GET', 'POST'])
def add_route():
    """add link"""

    form = LinkForm()

    if form.validate_on_submit():
        table_links.put_item(Item={'id': str(uuid4()), 'link': form.link.data, 'tags': ['a'], 'created': datetime.utcnow().isoformat()})
        return redirect(url_for('index_route'))

    return render_template('add.html', form=form)


@app.route('/delete/<id>', methods=['POST'])
def delete_route(id):
    """delete item"""

    form = ButtonForm()

    if form.validate_on_submit():
        table_links.delete_item(Key={'id': id})
        return redirect(url_for('index_route'))

    return render_template('button-delete.html', form=form)
