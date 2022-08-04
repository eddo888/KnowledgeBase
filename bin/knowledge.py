#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import os, re, sys, json, codecs, logging, requests, arrow, shutil, inspect, sqlalchemy, unicodedata, uuid, base64, datetime, time, pytz, xmltodict

if os.path.dirname(sys.argv[0]) == '.':
	sys.path.insert(0, '..')

# https://github.com/serkanyersen/underscore.py/
# pip3 install underscore.py
from underscore import _

from time import mktime
from datetime import datetime
from io import StringIO

from xlrd import open_workbook

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, joinedload
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.engine import reflection

from jsonpickle import encode, decode

from collections import OrderedDict
from dotmap import DotMap
from jsonpath import jsonpath
from bs4 import BeautifulSoup as BS
from zipfile import ZipFile

from Argumental.Argue import Argue
from Perdy.pretty import prettyPrintLn
from Spanners.Squirrel import Squirrel
from Spanners.Treeify import Treeify
from Baubles.Logger import Logger
from Baubles.Colours import Colours
from GoldenChild.xpath import *

from sqlalchemy.engine import reflection
from sqlalchemy import not_

from KnowledgeBase.model import *

args = Argue()
squirrel = Squirrel()
logger = Logger()
colours = Colours()
treeify = Treeify(colour=True)

def quietly():
	for logger in [
		"sqlalchemy.engine.Engine",
		"sqlalchemy.orm.relationships.RelationshipProperty",
		"sqlalchemy.orm.strategies.LazyLoader", "sqlalchemy.orm.path_registry",
		"sqlalchemy.orm.mapper.Mapper", "sqlalchemy.engine.base.Engine",
		"sqlalchemy.pool.NullPool", "sqlalchemy.pool.impl.NullPool",
		"sqlalchemy.pool.SingletonThreadPool",
		"requests.packages.urllib3.connectionpool"
	]:
		logging.getLogger(logger).setLevel(logging.WARNING)


def clean(text):
	return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')


def public(node):
	tipe = type(node)
	if tipe is list:
		for n in range(len(node)):
			node[n] = public(node[n])
	if tipe in [OrderedDict, dict]:
		for key in node.keys():
			if key.startswith('_'):
				del node[key]
	return node
	

def uncomment(value):
	comment = re.compile('(\<\!\-\-|\-\-\>)')
	value = value.replace('\n', '%%%%%')
	keep = True
	output = StringIO()
	for element in comment.split(value):
		if element == '<!--':
			keep = False
		if keep:
			output.write(element)
		if element == '-->':
			keep = True
	return output.getvalue().replace('%%%%%', '\n')


class Empty(object):

	base64 = 'Empty.base64'
	
	def touch(self, file, adt=None):
		stat = os.stat(file)
		(st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime,
			st_mtime, st_ctime) = stat
		if adt:
			t = time.mktime(adt.timetuple())
			os.utime(file, (t, t))
		else:
			adt = datetime.fromtimestamp(st_mtime)
		return adt
		
	
	def toDB(self, b64, db):
		t = self.touch(b64)
		with open(b64, 'r') as fi:
			b = fi.read()
			fi.close()
			with open(db, 'wb') as fo:
				fo.write(base64.b64decode(b))
				fo.close()
				self.touch(db, t)
		return
	
	
	def fromDB(self, db, b64):
		t = self._touch(db)
		with open(db, 'rb') as fi:
			b = fi.read()
			fi.close()
			with open(b64, 'w') as fo:
				fo.write(base64.b64encode(b))
				fo.close()
				self.touch(b64, t)
		return
	
		
@args.command(single=True)
class Export(object):
	'''
	tool to inspect, query and edit Knowledge Base sqlite files
	'''
	
	@args.property(short='v', flag=True, help='verbose logging')
	def verbose(self):
		return False


	@args.property(short='e', default='export', help='output to export dir')
	def exportdir(self):
		return


	@args.property(short='D', default='Empty.kdb', help='Knowledge Base database')
	def database(self):
		return


	@args.property(short='k', flag=True, help='klobber db')
	def klobber(self):
		return


	def __init__(self, verbose=False):

		if self.klobber:
			os.unlink(self.database)
			Empty().toDB(Empty.base64, self.database) # create clean copy from empty.base64
			
		self._types = {
			'TINYINT': '%d',
			'MEDIUMINT': '%d',
			'INTEGER': '%d',
			'DOUBLE': '%f',
			'TEXT': '"%s"',
			#'LONGBLOB': '"%s"',
			'LONGTEXT': '"%s"',
			'MEDIUMTEXT': '"%s"',
			'SET': '"%s"',
			'ENUM': '"%s"',
			'YEAR': '%d',
		}
		self.verbose = verbose
		if not os.path.isdir(self.exportdir):
			os.makedirs(self.exportdir)
		self.errorlog = open('%s/error.log' % self.exportdir, 'w')
		self.__engine = None
		if self.verbose:
			logger.setLevel(logging.DEBUG)
		else:
			logger.setLevel(logging.INFO)
			
		Base.metadata.create_all(self.engine)
		self.__Session = sqlalchemy.orm.sessionmaker(
			autoflush=False, autocommit=False, bind=self.engine
		)
		self.__Session.configure(bind=self.engine)


	def __del__(self):
		self.errorlog.close()


	@property
	def engine(self):
		'''
		create or return existing engine as a property
		'''
		self.url = 'sqlite:///%s' % self.database

		if not self.__engine:
			self.__engine = sqlalchemy.create_engine(self.url)
			
		self.inspector = sqlalchemy.inspect(self.__engine)
		
		self.tables = dict() # table: [ column ]
		for table in self.inspector.get_table_names():
			self.tables[table] = set()
			for column in self.inspector.get_columns(table):
				self.tables[table].add(column['name'])
			
		return self.__engine


	def Session(self):
		'''
		return a new session object
		'''
		return self.__Session()


	def _topics(self, session, index, topics, parent, parent_id='-1', indent='\t'):
		items = {} # topic['@id'] : Item()
		other = []
		
		for topic in topics:
			if topic['@parent'] == parent_id:
				item = Item()
				item.Name = topic['@text']
				if 'note' in topic.keys():
					item.Description = topic['note']
				item.URI = topic['@id']
				session.add(item)

				relation = Relation()
				relation.inbound = item
				relation.outbound = parent
				session.add(relation)
				items[item.URI] = item
				index[item.URI] = item
			else:
				other.append(topic)

		for id, item in items.items():
			print(f'{indent}{item.Name}')
			self._topics(session, index, other, item, parent_id=id, indent=f'\t{indent}')
			

	@args.operation
	@args.parameter(name='klobber', short='k', flag=True, help='create from scratch')
	def load_smmx(self, file, klobber=False):
		'''
		read a Simple Mind xml smmx file and load it into the database
		'''
		
		if klobber:
			Empty().toDB(Empty.base64, self.database) # create clean copy from empty.base64

		session = self.Session()
		root = Item()
		session.add(root)

		root.Description = file

		with ZipFile(file) as zf:
			with zf.open('document/mindmap.xml') as xf:
				smmx = xmltodict.parse(xf.read().decode('UTF8'))

				with open(f'{file}.json','w') as jf:
					json.dump(smmx, jf, indent='\t')

				topics = smmx['simplemind-mindmaps']['mindmap']['topics']['topic']
				index = dict() # topic['@id'] : Item()
				self._topics(session, index, topics, root)

				relations = smmx['simplemind-mindmaps']['mindmap']['relations']['relation']
				for relation in relations:
					source = index[relation['@source']]
					target = index[relation['@target']]
					print(f'{source.Name} -> {target.Name}')
					_relation = Relation()
					_relation.inbound = target
					_relation.outbound = source
					session.add(_relation)
					
		session.commit()
		session.close()
		
		
	def _sequences(self, session):
		results = dict()
		for sequence in session.query(t_sqlite_sequence):
			results[sequence.name] = sequence.seq
		prettyPrintLn(results,align=True)	
			

	def _undone(self, session):
		rows = list()
		for undo in session.query(UndoLog):
			rows.append(dict(map(lambda x: (x,getattr(undo,x)), self.tables[UndoLog.__tablename__])))
		prettyPrintLn(rows)
		
	
	def _process(self, outlines, session=None, parent=None, indent=''):
		url_pattern=re.compile('.*(https*://\S+)\s*.*')
		if type(outlines) is not list:
			outlines = [outlines]
		for outline in outlines:
			item = Item()
			session.add(item)
			if '@text' in outline.keys():
				text = outline['@text']
				url_match = url_pattern.match(text)
				if url_match:
					url = url_match.group(1)
					item.DirectLinkURL = url
					text = text.replace(url,'')
				item.Name = text
				print('%s%s'%(indent, text))
			if '@_note' in outline.keys():
				item.Description = outline['@_note']
				print('  %s"%s"'%(indent, outline['@_note']))

			relation = Relation()
			session.add(relation)
			relation.outbound = parent
			relation.inbound = item
			
			if 'outline' in outline.keys():
				self._process(outline['outline'], session=session, parent=item, indent='  %s'%indent)
			
					
	@args.operation
	@args.parameter(name='klobber', short='k', flag=True, help='create from scratch')
	def load_opml(self, file, klobber=False):
		'''
		load OPML xml format into the KDB
		'''
		
		if klobber:
			Empty().toDB(Empty.base64, self.database) # create clean copy from empty.base64

		session = self.Session()
		root = Item()
		session.add(root)

		root.Description = file
		opml = xmltodict.parse(open(file,'rb').read().decode('UTF8'))
		root.Name = opml['opml']['head']['title']

		self._process(opml['opml']['body']['outline'], session=session, parent=root)

		session.commit()
		session.close()

		
	@args.operation
	def load_excel(self, file):
		'''
		load an excel sheet into the KDB file
		'''
		
		session = self.Session()
		
		school = session.query(Item).filter_by(Name="FSHS").first()
		print(school.Description)
		
		workbook = open_workbook(filename=file)
		sheet = workbook.sheets()[0]
		for row in range(sheet.nrows):
			
			teacher_name = sheet.cell(row, 0).value.strip()
			teacher_item = session.query(Item).filter_by(Name=teacher_name).first()
			if teacher_item:
				sys.stdout.write("%s%s"%(colours.Green, teacher_name))
			else:
				sys.stdout.write("%s%s"%(colours.Orange, teacher_name))
				teacher_item = Item()
				teacher_item.Name = teacher_name
				session.add(teacher_item)
				teacher_relation = Relation()
				teacher_relation.inbound = teacher_item
				teacher_relation.outbound = school
				session.add(teacher_relation)			
				
			teacher_code = sheet.cell(row, 3).value.strip()
			teacher_item.Description = teacher_code
			session.add(teacher_item)
			
			sys.stdout.write("%s"%(colours.Off))
										
			class_names = sheet.cell(row, 1).value.strip()
			
			for class_name in class_names.split(", "):
				class_item = session.query(Item).filter_by(Name=class_name).first()
				if class_item:
					sys.stdout.write(", %s%s"%(colours.Green, class_item.Name))

					if False:
						for r in session.query(Relation).filter_by(
							IDFrom=class_item.ItemID, 
							IDTo=teacher_item.ItemID,
						).all():
							session.delete(r)
					
					class_relation = session.query(Relation).filter_by(
						IDFrom=class_item.ItemID, 
						IDTo=teacher_item.ItemID,
					).first()
					
					if class_relation:
						sys.stdout.write(", %s%s"%(colours.Green, class_name))
					else:
						sys.stdout.write(", %s%s"%(colours.Orange, class_name))
						class_relation = Relation()
						class_relation.inbound = class_item
						class_relation.outbound = teacher_item
						session.add(class_relation)
				else:
					sys.stdout.write(", %s%s"%(colours.Red, class_name))
				
			sys.stdout.write("%s\n"%colours.Off)
			
		session.commit()
		session.close()			
		

	def _import_node(self, session, cod, childItem, parent, indent=''):
		'''
		load an item and iterate through children
		'''

		text = getElementText(cod.ctx, 'title', childItem)
		print(f'{indent}{text}')

		notes = getElement(cod.ctx, 'notes', childItem)
		note = None
		
		if notes:
			note = notes.content
			if note != '(null)':
				print(f'{indent}{indent}"{note}"')
				
		item = Item()
		session.add(item)
		item.Name = text
		item.Description = note

		relation = Relation()
		session.add(relation)
		#relation.Name = 'r1'
		#relation.Description = 'Relation One'
		relation.inbound = parent
		relation.outbound = item

		for grandChild in getElements(cod.ctx, 'ChildItem', childItem):
			self._import_node(session, cod, grandChild, item, indent=f'{indent}  ')
			
		
	@args.operation(name="import")
	@args.parameter(name='name', help='name of node to append to')
	@args.parameter(name='file', help='cloud outliner cod file')
	def importer(self, name, file):
		'''
		import cloud outliner cod file to a node parent
		'''
		
		session = self.Session()

		root = session.query(Item).filter_by(Name=name).first()

		if not root:
			root = Item()
			session.add(root)
			root.Name = file

		cod = XML(*getContextFromFile(os.path.expanduser(file)))
		
		for childItem in getElements(cod.ctx, '/Document/Properties/context/ChildItem'):
			self._import_node(session, cod, childItem, root, indent='')
		
		session.commit()
		session.close()


	@args.operation
	@args.parameter(name='references', short='r', flag=True, help='get the reference categories instead')
	def categories(self, references=False):
		'''
		inspect the structure for categories for the templates in the KDB
		'''
		
		session = self.Session()

		if references:
			query = session.query(RelationTemplate)
			for relation in query.all():
				print(relation.TemplateName)
					  
		else:
			query = session.query(ItemTemplate)
			for category in query.all():
				print(category.TemplateName)
		
		session.close()


	def _sort(self, session, item, depth=1, indent=''):
		sys.stdout.write('%s\n'%(item.Name))
		if depth > 0:
			children = dict(map(lambda x: (x.outbound.Name.lower(), x), item.outbound))
			sequence = 10
			for key in sorted(children.keys()):
				relation = children[key]
				sys.stdout.write('%s\t%03d -> '%(indent, relation.SequenceFrom))
				relation.SequenceFrom = sequence
				session.add(relation)
				sequence += 10
				self._sort(session, relation.outbound, depth-1, indent='%s\t'%indent)


	@args.operation
	@args.parameter(name='asis', help='empty string "" for None')
	@args.parameter(name='tobe', help='empty string "" for None')
	@args.parameter(name='name', short='n', help='match on name, %% for wildcard')
	@args.parameter(name='dryrun', short='d', flag=True, help='dry run, don\'t commit')
	def categorise(self, asis, tobe, name=None, dryrun=None):
		'''
		change the category from asis to tobe
		'''

		session = self.Session()

		if asis == '':
			_asis = None
			print('from: <None>')
		else:
			_asis = session.query(ItemTemplate).filter_by(TemplateName=asis).first()
			if _asis:
				print(f'from: {_asis.TemplateName}')
			else:
				sys.stderr.write(f'can\' find category {asis}\n')
				return

		if tobe == '':
			_tobe = None
			print('to: <None>')
		else:
			_tobe = session.query(ItemTemplate).filter_by(TemplateName=tobe).first()
			if _tobe:
				print(f'to:  -> {_tobe.TemplateName}')
			else:
				sys.stderr.write(f'can\'t find category {tobe}\n')
				return

		if _asis:
			query = session.query(Item).filter_by(ItemTemplateID=_asis.ItemTemplateID)
		else:
			query = session.query(Item).filter_by(ItemTemplateID=-1)

		if name:
			query = query.filter(Item.Name.like(name))
			
		for item in query.all():
			print(f'{item.Name} : <{item.ItemTemplateID}> ')
			if _tobe:
				item.category = _tobe
			else:
				item.ItemTemplateID = -1

		if not dryrun:
			session.commit()
			
		session.close()

		
	@args.operation
	@args.parameter(name='name', help='item name to sort')
	@args.parameter(name='depth', short='d', type=int, help='recursion depth')
	@args.parameter(name='noCommit', short='n', flag=True, help='no commit for changes')
	def sort(self, name, depth=1, noCommit=False):
		'''
		sort an items child items
		'''
		
		session = self.Session()

		for item in session.query(Item).filter_by(Name=name):
			self._sort(session, item, depth=depth)
						
		if not noCommit:
			session.commit()
		session.close()


	@args.operation
	@args.parameter(name='name', short='n', help='match on name, %% for wildcard')
	@args.parameter(name='description', short='d', flag=True, help='include description')
	@args.parameter(name='url', short='u', flag=True, help='include url')
	@args.parameter(name='attachments', short='a', flag=True, help='include attachments')
	@args.parameter(name='references', short='r', choices=['i','o','b'], help='include references, inbound/outbound/both')
	@args.parameter(name='categories', short='c', nargs='+',  help='restrict to categories')
	def query(self, name=None, description=None, url=None, attachments=None, references=None, categories=[]):
		'''
		query a value, and filter by category
		'''
		
		session = self.Session()
		
		query = session.query(Item)
		if name:
			query = query.filter(Item.Name.like(name))

		query = query.join(Item.category)

		for item in query.all():
			if categories:
				if item.category.TemplateName not in categories:
					continue

			text = f'{item.Name}'
			if item.category:
				text = f'{text} : <{item.category.TemplateName}>'
			print(text)
			
			if description:
				print(f'\t# {item.Description}')
				
			if url:
				print(f'\t@ {item.DirectLinkURL}')
				
			if attachments:
				for attachment in item.attachments:
					print(f'\t& {attachment.attachment.Data}')
					
			if references in ['i','b']:
				for reference in item.inbound:
					text = f'\t< {reference.inbound.Name}'
					if reference.category:
						text = f'{text} : <{reference.category.TemplateName}>'
					print(text)
					
			if references in ['o','b']:
				for reference in item.outbound:
					text = f'\t> {reference.outbound.Name}'
					if reference.category:
						text = f'{text} : <{reference.category.TemplateName}>'
					print(text)
				
		session.close()


	@args.operation
	def step_in(self):
		'''
		todo
		'''


	@args.operation
	def step_out(self):
		'''
		todo
		'''
		

	@args.operation
	@args.parameter(name='old', help='string to search in name for')
	@args.parameter(name='new', help='string to replace with')
	@args.parameter(name='description', short='d', flag=True, help='search in description as well')
	def replace(self, old, new, description=False):
		'''
		search and replace in item names
		'''
		
		session = self.Session()
		for item in session.query(Item):
			_name = item.Name
			if old in _name:
				_name = _name.replace(old,new)
				print(item.Name,_name)
				item.Name = _name
				session.add(item)
			if not description:
				continue
			_description = item.Description
			if old in _description:
				_description = _description.replace(old,new)
				print('\t%s'%(item.Description, _description))
				item.Description = _description
		session.commit()
		session.close()

		
	@args.operation
	def clean(self):
		'''
		remote html tags from descriptions
		'''
		
		session = self.Session()
		for item in session.query(Item):
			_name = item.Name
			if '<html>' in _name:
				_name = BS(_name,'lxml').text
			_name = _.escape(_name)
			_name = clean(_name)
			if _name != item.Name:
				print(item.Name, _name)
				item.Name = _name
				session.add(item)
		session.commit()
		session.close()


	@args.operation
	def to_csv(self):
		'''
		export data to directory as tables of raw KDB types
		'''
		
		shutil.copy2(self.database, '%s/.kdb'%self.exportdir)
		self.inspector =  sqlalchemy.inspect(self.__engine)
		for table in self.inspector.get_table_names():
			if table.startswith('general_db'):
				continue
			self._table(table)


	@args.operation
	def deArrow(self):
		'''
		remove -> arrows from descriptions
		'''
		
		session = self.Session()

		for item in session.query(Item).filter(Item.ItemID>0): 
			if '->' in item.Name:
				name = item.Name.split('-> ')[-1]
				print(item.Name, name)
				item.Name = name
				session.add(item)

		session.commit()
		session.close()


	def _column(self, column, value):
		if not value: return ''
		if not 'type' in column.keys(): return ''
		tipe = None
		if isinstance(value, str):
			sys_std_err = sys.stderr
			sys.stderr = self.errorlog
			bs = BS(value)  #,"lxml")
			sys.stderr = sys_std_err
			value = uncomment(bs.text)
			return '"%s"' % clean(value.replace('"', "'"))

		if column['name'] in ['When']:
			now = arrow.get(value, 'YYYY-MM-DD HH:mm:ss Z')
			then = now.shift(hours=1)
			appointment = " - ".join(
				map(lambda x: x.format('DD MMM YYYY HH:mm:ss'), [now, then]))
			return '"%s"' % appointment
		try:
			tipe = '%s' % column['type']
			if tipe in self._types.keys():
				return self._types[tipe] % value
			else:
				return '"<%s>"' % tipe
		except:
			pass
			#print('? %s=%s'%(tipe,value))
		return '"%s"' % value


	def _row(self, output, columns, row):
		values = []
		for c in range(len(row)):
			value = row[c]
			if isinstance(value, str):
				value = clean(value)
			column = columns[list(columns.keys())[c]]
			values.append(self._column(column, value))
		output.write('%s\n' % ('\t'.join(values)))


	def _header(self, table):
		columns = dict(
			map(lambda x: (x['name'], x), self.inspector.get_columns(table)))
		#print(columns)
		id = 'id'
		names = columns.keys()
		while id in names and names.index(id) > 0:
			names.remove(id)
			names.insert(0, 'id')
		header = OrderedDict(map(lambda x: (x, columns[x]), names))
		return header


	def _table(self, table):
		print(table)
		file = '%s/%s.csv' % (self.exportdir, table)
		with open(file, 'w') as output:
			columns = self._header(table)

			header = '\t'.join(map(lambda x: '"%s"' % x, columns.keys()))
			output.write('%s\n' % header)
			fields = ','.join(map(lambda x: '"%s"' % x, columns.keys()))

			sql = 'select %s from "%s"%s;' % (fields, table, ' order by "id"' if 'id' in columns.keys() else '')

			for row in self.engine.execute(sql):
				self._row(output, columns, row)
				#break # stop after one, remove for production

			# debug output
		if self.verbose:
			with open(file) as input:
				print(input.read())


def main():
	quietly()
	if False:
		args.parse([
			'-D',
			'libraries.kdb',
			'load_opml',
			'libraries.opml',
		])
	args.execute()

		
if __name__ == '__main__': main()
