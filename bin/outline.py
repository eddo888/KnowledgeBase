#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import sys, os, json, logging, arrow, codecs, xmltodict

from uuid import uuid4
from collections import OrderedDict

logging.getLogger('pyxb.binding.content').setLevel(logging.ERROR)

#_________________________________________________
def sample():
	outline="""\
	Category1::Name 1(Description 1)
		Category2::Name 2(Description 2)
			Line Category::Linie 1>>Category2::Name 3
		Category2::Name 3(Description 3)
			Line Category::Linie 2>>Category2::Name 4
		Category2::Name 4(Description 4)
			Line Category::Linie 3>>Category2::Name 5
		Category2::Name 5(Description 5)
			Line Category::Linie 4>>Category2::Name 6
		Category2::Name 6(Description 6)
			Line Category::Linie 5>>Category2::Name 2
	"""
	print(outline)


#_________________________________________________
def clean(text):
	replacements = {
		'\n': ';',
		'(': '{',
		')': '}',
	}
	for f,t in replacements.items():
		text = text.replace(f,t)
	return text
			

#_________________________________________________
def listify(node):
	if type(node) != list:
		return [node]
	return node
			

#_________________________________________________
class COD2KDB(object):
	
	#.............................................
	def __init__(self):
		self.cache = set()


	#.............................................
	def __cod_node(self, children, output, parent, indent='\t'):
		'''
		show a single item
		'''
		name = clean(children.title[0].value())
		
		if name in self.cache:
			name = '%s -> %s'%(parent, name)
		self.cache.add(name)

		if children.notes:
			text = clean(children.notes[0].value()) 
		else:
			text = ''

		output.write('%s%s(%s)\n'%(indent, name, text))

		for child in children.ChildItem:
			self.__cod_node(child, output, name, indent='%s\t'%indent)


	#.............................................
	def __cod_root(self, file, cod, output):
		'''
		show the cod file
		'''
		m = cod.Properties[0].lastModificationTime[0].value()
		u = arrow.get(m)
		a = u.to('local').format('YYYY-MM-DD HH:mm:ss SSS Z')
		t = cod.Properties[0].title[0].value()
		output.write('%s(%s @ %s)\n'%(file, t, a))
		children = cod.Properties[0].context[0].ChildItem
		for child in children:
			self.__cod_node(child, output, file)


	#.............................................
	def cod2kdb(self, file, output=None):
		'''
		load a cod file and display
		'''
		if output:
			_output = codecs.open(output, 'w', encoding='utf8')
		else:
			_output = sys.stdout
		with open(file) as input:
			cod = CreateFromDocument(input.read())
			self.__cod_root(file, cod, _output)
		if output:
			_output.close()
		return
			

	#.............................................
	def __opml_node(self, outline, output, parent, indent='\t'):
		'''
		show a single item
		'''
		name = clean(outline['@text'])
		
		if name in self.cache:
			name = '%s -> %s'%(parent, name)
		self.cache.add(name)

		if '@_note' in outline.keys():
			text = clean(outline['@_note'])
		else:
			text = ''

		output.write('%s%s(%s)\n'%(indent, name, text))

		if 'outline' not in outline.keys():
			return
			
		for child in listify(outline['outline']):
			self.__opml_node(child, output, name, indent='%s\t'%indent)


	#.............................................
	def __opml_root(self, file, opml, output):
		'''
		show the opml file
		'''
		output.write('%s\n'%file)
		children = opml['opml']['body']
		
		for child in listify(children['outline']):
			self.__opml_node(child, output, file)


	#.............................................
	def opml2kdb(self, file, output=None):
		'''
		load a cod file and display
		'''
		if output:
			_output = codecs.open(output, 'w', encoding='utf8')
		else:
			_output = sys.stdout
		with open(file) as input:
			opml = xmltodict.parse(input.read())
			self.__opml_root(file, opml, _output)
		if output:
			_output.close()
		return


#_________________________________________________
def main():
	COD2KDB().opml2kdb(sys.argv[1])
	
#_________________________________________________
if __name__ == '__main__': main()
