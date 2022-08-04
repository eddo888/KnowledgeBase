#!/usr/bin/env python3

import codecs
from os import path
from setuptools import setup

pwd = path.abspath(path.dirname(__file__))
with codecs.open(path.join(pwd, 'README.md'), 'r', encoding='utf8') as input:
    long_description = input.read()

version='1.11'
name='KnowledgeBase'

setup(
	name=name,
	version=version,
	license='MIT',
    long_description=long_description,
	long_description_content_type="text/markdown",
	url='https://github.com/eddo888/%s'%name,
	download_url='https://github.com/eddo888/%s/archive/%s.tar.gz'%(name, version),
	author='David Edson',
	author_email='eddo888@tpg.com.au',
	packages=[
		name,
	],
	install_requires=[
		'jsonpickle',
		'underscore.py',
		'sqlalchemy',
		'xmltodict',
		'xlrd',
		'xlwt',
		'Baubles',
		'Perdy',
		'Argumental',
		'Swapsies',
	],
	scripts=[
		'bin/knowledge.py',
		'bin/outline.py',
	],
)
