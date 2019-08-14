#!/usr/bin/env python3
"""bmarks, bookmarking app"""

from datetime import datetime
from os import urandom
from uuid import uuid4

from flask import flash, Flask, redirect, render_template, url_for
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
# least intrusive way to pass token into every view without enforcing csrf on all routes
app.add_template_global(name='csrf_token', f=generate_csrf)

dynamo = Dynamo(app)  # pylint: disable=invalid-name
table_links = dynamo.tables['links']  # pylint: disable=invalid-name


class ButtonForm(FlaskForm):
    """simple button form for csrf handling on non-data forms"""


class LinkForm(FlaskForm):
    """link form"""

    link = StringField('Link', [InputRequired()])
    tags = StringField('Tags')
    submit = SubmitField('Save')


@app.route('/', methods=['GET'])
def index_route():
    """main index"""

    links = [x for x in table_links.scan()['Items']]
    tags = []
    for link in links:
        tags += link['tags']
    tags = list(set(tags))
    return render_template('index.html', links=links, tags=tags)


@app.route('/add', methods=['GET', 'POST'])
def add_route():
    """add link"""

    form = LinkForm()

    if form.validate_on_submit():
        # pull data from form
        link = form.link.data.strip()
        tags = [x.strip() for x in form.tags.data.split(',')]

        table_links.put_item(Item={'id': str(uuid4()), 'link': link, 'tags': tags, 'created': datetime.utcnow().isoformat()})
        return redirect(url_for('index_route'))

    return render_template('addedit.html', form=form)


@app.route('/edit/<link_id>', methods=['GET', 'POST'])
def edit_route(link_id):
    """edit link"""

    link = table_links.get_item(Key={'id': link_id})['Item']
    form = LinkForm(link=link['link'], tags=','.join(link['tags']))

    if form.validate_on_submit():
        # pull data from from
        link = form.link.data.strip()
        tags = [x.strip() for x in form.tags.data.split(',')]

        table_links.update_item(
            Key={'id': link_id},
            UpdateExpression='set link = :link, tags = :tags',
            ExpressionAttributeValues={':link': link, ':tags': tags},
            ReturnValues='UPDATED_NEW'
        )
        return redirect(url_for('index_route'))

    return render_template('addedit.html', form=form)


@app.route('/delete/<link_id>', methods=['POST'])
def delete_route(link_id):
    """delete item"""

    form = ButtonForm()

    if form.validate_on_submit():
        table_links.delete_item(Key={'id': link_id})
        return redirect(url_for('index_route'))

    return render_template('button-delete.html', form=form)


@app.route('/add_tag/<link_id>/<tag>', methods=['GET', 'POST'])
def add_tag_route(link_id, tag):
    """add tag to link"""

    form = ButtonForm()

    if form.validate_on_submit():
        link = table_links.get_item(Key={'id': link_id})['Item']
        if not link:
            flash('No such link', 'error')
            return redirect(url_for('index_route'))

        table_links.update_item(
            Key={'id': link_id},
            UpdateExpression='set tags = :tags',
            ExpressionAttributeValues={':tags': list(set(link['tags'] + [tag]))},
            ReturnValues='UPDATED_NEW')

    return redirect(url_for('index_route'))


@app.route('/delete_tag/<link_id>/<tag>', methods=['GET', 'POST'])
def delete_tag_route(link_id, tag):
    """delete tag to link"""

    form = ButtonForm()

    if form.validate_on_submit():
        link = table_links.get_item(Key={'id': link_id})['Item']
        if not link:
            flash('No such link', 'error')
            return redirect(url_for('index_route'))

        try:
            tags = link['tags']
            tags.remove(tag)
            table_links.update_item(
                Key={'id': link_id},
                UpdateExpression='set tags = :tags',
                ExpressionAttributeValues={':tags': tags},
                ReturnValues='UPDATED_NEW')
        except ValueError:
            flash('No such tag', 'error')

    return redirect(url_for('index_route'))
