#!/usr/bin/env python3
"""bmarks, an aws bookmarking app"""

import os
from datetime import datetime
from uuid import uuid4

from flask import Blueprint, current_app, Flask, jsonify, redirect, render_template, request, url_for
from flask_dynamo import Dynamo
from flask_login import login_required, login_user, logout_user, LoginManager, UserMixin
from flask_wtf import FlaskForm
from flask_wtf.csrf import generate_csrf
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired


#
# application objects and factory
#

blueprint = Blueprint('app', __name__)  # pylint: disable=invalid-name
dynamo = Dynamo()  # pylint: disable=invalid-name
login_manager = LoginManager()  # pylint: disable=invalid-name

def create_app():
    """application factory"""

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(32)
    app.config['DYNAMO_TABLES'] = [{
        'TableName': 'links',
        'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
        'AttributeDefinitions': [{'AttributeName': 'id', 'AttributeType': 'S'}],
        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    }]

    dynamo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'app.login_route'
    login_manager.login_message = 'Not logged in'
    login_manager.login_message_category = 'error'
    app.register_blueprint(blueprint, url_prefix='/')
    # least intrusive way to pass token into every view without enforcing csrf on all routes
    app.add_template_global(name='csrf_token', f=generate_csrf)
    return app


#
# forms
#

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


class LoginForm(FlaskForm):
    """login form"""

    password = PasswordField('Password', [InputRequired()])
    submit = SubmitField('Login')


#
# authentication
#

class User(UserMixin):
    """dead simple user class"""

    def __init__(self):
        self.id = 1  # pylint: disable=invalid-name
        self.password = os.environ.get('PASSWORD')


@login_manager.user_loader
def load_user(user_id):  # pylint: disable=unused-argument
    """user loader"""
    return User()


@blueprint.route('/login', methods=['GET', 'POST'])
def login_route():
    """login route"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User()
        if user.password and (user.password == form.password.data):
            login_user(user)

            # redirect after login
            if request.args.get('next'):
                for rule in current_app.url_map.iter_rules():
                    if rule.rule.startswith(request.args.get('next')):
                        return redirect(request.args.get('next'))
            return redirect(url_for('app.index_route'))

    return render_template('login.html', form=form)


@blueprint.route('/logout')
@login_required
def logout_route():
    """logout route"""

    logout_user()
    return redirect(url_for('app.index_route'))


#
# controller
#

@blueprint.route('/', methods=['GET'])
def index_route():
    """main index"""
    return render_template('index.html')


@blueprint.route('/json', methods=['GET'])
def index_json_route():
    """datatable data endpoint"""
    return jsonify({'data': dynamo.tables['links'].scan()['Items']})


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_route():
    """add link"""

    form = LinkForm()

    if form.validate_on_submit():
        link, tags = form.parsed_data()
        dynamo.tables['links'].put_item(Item={'id': str(uuid4()), 'link': link, 'tags': tags, 'created': datetime.utcnow().isoformat()})
        return redirect(url_for('app.index_route'))

    return render_template('addedit.html', form=form)


@blueprint.route('/edit/<link_id>', methods=['GET', 'POST'])
@login_required
def edit_route(link_id):
    """edit link"""

    link = dynamo.tables['links'].get_item(Key={'id': link_id})['Item']
    form = LinkForm(link=link['link'], tags=','.join(link['tags']))

    if form.validate_on_submit():
        link, tags = form.parsed_data()
        dynamo.tables['links'].update_item(
            Key={'id': link_id},
            UpdateExpression='set link = :link, tags = :tags',
            ExpressionAttributeValues={':link': link, ':tags': tags},
            ReturnValues='UPDATED_NEW')
        return redirect(url_for('app.index_route'))

    return render_template('addedit.html', form=form)


@blueprint.route('/toggleread/<link_id>', methods=['POST'])
@login_required
def toggleread_route(link_id):
    """toggles read tag on link"""

    form = ButtonForm()

    if form.validate_on_submit():
        link = dynamo.tables['links'].get_item(Key={'id': link_id})['Item']

        if 'read' in link['tags']:
            link['tags'].remove('read')
        else:
            link['tags'].append('read')

        dynamo.tables['links'].update_item(
            Key={'id': link_id},
            UpdateExpression='set tags = :tags',
            ExpressionAttributeValues={':tags': link['tags']},
            ReturnValues='UPDATED_NEW')

    return redirect(url_for('app.index_route'))


@blueprint.route('/delete/<link_id>', methods=['POST'])
@login_required
def delete_route(link_id):
    """delete item"""

    form = ButtonForm()

    if form.validate_on_submit():
        dynamo.tables['links'].delete_item(Key={'id': link_id})

    return redirect(url_for('app.index_route'))
