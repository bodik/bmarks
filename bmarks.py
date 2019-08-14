#!/usr/bin/env python3
"""bmarks, an aws bookmarking app"""

from datetime import datetime
from os import urandom
from uuid import uuid4

from flask import flash, Flask, jsonify, redirect, render_template, url_for
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
    tags = StringField('Tags', description='Multiple tags separated by comma (,).')
    submit = SubmitField('Save')

    def parsed_data(self):
        """parse data from form"""

        link = self.link.data.strip()
        tags = list(filter(bool, [x.strip() for x in self.tags.data.split(',')]))
        return link, tags


@app.route('/', methods=['GET'])
def index_route():
    """main index"""
    return render_template('index.html')


@app.route('/json', methods=['GET'])
def index_json_route():
    """datatable data endpoint"""
    return jsonify({'data': table_links.scan()['Items']})


@app.route('/add', methods=['GET', 'POST'])
def add_route():
    """add link"""

    form = LinkForm()

    if form.validate_on_submit():
        link, tags = form.parsed_data()
        table_links.put_item(Item={'id': str(uuid4()), 'link': link, 'tags': tags, 'created': datetime.utcnow().isoformat()})
        return redirect(url_for('index_route'))

    return render_template('addedit.html', form=form)


@app.route('/edit/<link_id>', methods=['GET', 'POST'])
def edit_route(link_id):
    """edit link"""

    link = table_links.get_item(Key={'id': link_id})['Item']
    form = LinkForm(link=link['link'], tags=','.join(link['tags']))

    if form.validate_on_submit():
        link, tags = form.parsed_data()
        table_links.update_item(
            Key={'id': link_id},
            UpdateExpression='set link = :link, tags = :tags',
            ExpressionAttributeValues={':link': link, ':tags': tags},
            ReturnValues='UPDATED_NEW')
        return redirect(url_for('index_route'))

    return render_template('addedit.html', form=form)


@app.route('/toggleread/<link_id>', methods=['POST'])
def toggleread_route(link_id):
    """toggles read tag on link"""

    form = ButtonForm()

    if form.validate_on_submit():
        link = table_links.get_item(Key={'id': link_id})['Item']
        if not link:
            flash('No such link', 'error')
            return redirect(url_for('index_route'))

        if 'read' in link['tags']:
            link['tags'].remove('read')
        else:
            link['tags'].append('read')

        table_links.update_item(
            Key={'id': link_id},
            UpdateExpression='set tags = :tags',
            ExpressionAttributeValues={':tags': link['tags']},
            ReturnValues='UPDATED_NEW')

    return redirect(url_for('index_route'))


@app.route('/delete/<link_id>', methods=['POST'])
def delete_route(link_id):
    """delete item"""

    form = ButtonForm()

    if form.validate_on_submit():
        table_links.delete_item(Key={'id': link_id})

    return redirect(url_for('index_route'))
