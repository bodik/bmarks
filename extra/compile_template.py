#!/usr/bin/env python3

from argparse import ArgumentParser
from jinja2 import Template


parser = ArgumentParser()
parser.add_argument('template')
parser.add_argument('vars', nargs='*')
args = parser.parse_args()

template_vars = {}
if args.vars:
    for k,v in [x.split('=') for x in args.vars]:
        template_vars[k] = v

with open(args.template, 'r') as ftmp:
	print(Template(ftmp.read()).render(template_vars))
