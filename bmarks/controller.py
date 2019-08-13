"""controller module"""

from collections import namedtuple
from random import choice

from flask import Blueprint, jsonify, render_template


blueprint = Blueprint('main', __name__)

Quote = namedtuple('Quote', ('text', 'author'))
QUOTES = [
    Quote('Talk is cheap. Show me the code.', 'Linus Torvalds'),
    Quote(
        'Programs must be written for people to read,'
        ' and only incidentally for machines to execute.', 'Harold Abelson'),
    Quote(
        'Always code as if the guy who ends up maintaining your '
        'code will be a violent psychopath who knows where you live', 'John Woods'),
    Quote(
        'Give a man a program, frustrate him for a day. Teach '
        ' a man to program, frustrate him for a lifetime.', 'Muhammad Waseem'),
    Quote(
        'Progress is possible only if we train ourselves to think about '
        ' programs without thinking of them as pieces of executable code.', 'Edsger W. Dijkstra')
]


@blueprint.route('/', methods=['GET'])
def index_route():  # pylint: disable=unused-variable
    return render_template('index.html', quote=choice(QUOTES)._asdict())
