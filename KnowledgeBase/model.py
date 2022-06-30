#!/usr/bin/env python3
# coding: utf-8

import os, re, sys, json, uuid

from sqlalchemy import Column, Index, Integer, LargeBinary, Table, Text, ForeignKey
from sqlalchemy.schema import Sequence
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, joinedload

from jsonpickle import encode, decode

Base = declarative_base()
metadata = Base.metadata


#_________________________________________________
class BigBlob(Base):
	__tablename__ = 'BigBlob'

	BigBlobID = Column(
		Integer,
		Sequence('sqlite_sequence'),
		primary_key=True,
	)
	Data = Column(
		LargeBinary
	)


#_________________________________________________
class BigText(Base):
	__tablename__ = 'BigText'

	BigTextID = Column(
		Integer,
		Sequence('sqlite_sequence'),
		primary_key=True,
	)
	Data = Column(
		Text
	)

	
#_________________________________________________
@property
def t_DiagramProperties():
	return Table(
		'DiagramProperties', metadata,
		Column(
			'Name',
			Text,
			index=True
		),
		Column(
			'Value',
			Text
		)
	)


#_________________________________________________
class ItemAttachment(Base):
	__tablename__ = 'ItemAttachments'

	AttachmentID = Column(
		Integer,
		ForeignKey("BigText.BigTextID"),
	)
	attachment = relationship(
		'BigText',
		foreign_keys=[AttachmentID],
	)
	ItemID = Column(
		Integer,
		ForeignKey("Items.ItemID"),
	)
	item = relationship(
		'Item',
		foreign_keys=[ItemID]
	)
	RecordID = Column(
		Integer,
		Sequence('sqlite_sequence'),
		primary_key=True,
	)
	Sequence = Column(
		Integer
	)
	URI = Column(
		Text,
		index=True,
	)
	Properties = Column(
		Text
	)


#_________________________________________________
class ItemTemplate(Base):
	__tablename__ = 'ItemTemplates'

	ItemTemplateID = Column(
		Integer,
		Sequence('sqlite_sequence'),
		primary_key=True,
	)
	TemplateName = Column(
		Text,
		index=True,
	)
	Name = Column(
		Text
	)
	Description = Column(
		Text
	)
	DirectLinkURL = Column(
		Text
	)
	URI = Column(
		Text,
		index=True,
	)
	Properties = Column(
		Text
	)

	def __js__(self):
		return dict(
			id=self.ItemTemplateID,
			name=self.TemplateName,
			description=self.Description,
		)
	
	def __str__(self):
		#return self.TemplateName
		return json.dumps(self.__js__())
	

#_________________________________________________
class Item(Base):
	__tablename__ = 'Items'

	ItemID = Column(
		Integer,
		Sequence('sqlite_sequence'),
		primary_key=True,
	)
	ItemTemplateID = Column(
		Integer,
		ForeignKey("ItemTemplates.ItemTemplateID"),
	)
	category = relationship(
		"ItemTemplate",
		foreign_keys=[ItemTemplateID],
	)
	Name = Column(
		Text
	)
	Description = Column(
		Text
	)
	DirectLinkURL = Column(
		Text
	)
	URI = Column(
		Text,
		index=True,
	)
	Properties = Column(
		Text
	)
	outbound = relationship(
		"Relation",
		collection_class=list,
		foreign_keys='Relation.IDFrom',
		back_populates='_outbound',
	)
	inbound = relationship(
		"Relation",
		collection_class=list,
		foreign_keys='Relation.IDTo',
		back_populates='_inbound',
	)
	attachments = relationship(
		"ItemAttachment",
		collection_class=list,
		back_populates='item',
	)

	def __init__(self):
		self.URI = str(uuid.uuid4()).upper()
		self.ItemTemplateID = -1
		self.Properties = '{}'
		self.DirectLinkURL = ''
		self.Name = ''
		self.Description = ''
		
	def __js__(self):
		return dict(
			URI=self.URI,
			id=self.ItemID,
			name=self.Name,
			description=self.Description,
			category=self.category.TemplateName if self.category else None,
			URL=self.DirectLinkURL,
			properties=self.Properties,
			inbound=map(Relation.__js__, self.inbound),
			outbound=map(Relation.__js__, self.outbound),
		)
	
	def __str__(self):
		return json.dumps(self.__js__())
	

#_________________________________________________
@property
def t_Properties():
	return Table(
		'Properties', metadata,
		Column(
			'Name',
			Text,
			index=True,
		),
		Column(
			'Value',
			Text,
		)
	)


#_________________________________________________
@property
def t_RedoPos():
 return Table(
		'RedoPos', metadata,
		Column(
			'Pos',
			Integer,
		),
		Column(
			'UserID',
			Integer,
			index=True,
		)
	)


#_________________________________________________
@property
def t_RedoStack():
	return Table(
		'RedoStack', metadata,
		Column(
			'RedoStep',
			Integer,
		),
		Column(
			'UserID',
			Integer,
		),
		Column(
			'FirstStepID',
			Integer,
		),
		Column(
			'StepCount',
			Integer,
		),
		Column(
			'Description',
			Text,
		),
		Column(
			'Properties',
			Text,
		),
		Index(
			'RedoStack_RedoStep_IDX',
			'RedoStep',
			'UserID',
		)
	)


#_________________________________________________
class RelationAttachment(Base):
	__tablename__ = 'RelationAttachments'

	AttachmentID = Column(
		Integer,
		ForeignKey("BigText.BigTextID"),
	)
	attachment = relationship(
		'BigText',
		foreign_keys=[AttachmentID],
	)
	RelationID = Column(
		Integer,
		ForeignKey("Relations.RelationID"),
	)
	relation = relationship(
		'Relation',
		foreign_keys=[RelationID],
	)
	RecordID = Column(
		Integer,
		Sequence('sqlite_sequence'),
		primary_key=True,
	)
	Sequence = Column(
		Integer
	)
	URI = Column(
		Text,
		index=True,
	)
	Properties = Column(
		Text
	)


#_________________________________________________
class RelationTemplate(Base):
	__tablename__ = 'RelationTemplates'

	RelationTemplateID = Column(
		Integer,
		Sequence('sqlite_sequence'),
		primary_key=True,
	)
	VisibleUpToLevel = Column(
		Integer
	)
	TemplateName = Column(
		Text,
		index=True,
	)
	Name = Column(
		Text
	)
	BackRelName = Column(
		Text
	)
	Description = Column(
		Text
	)
	DirectLinkURL = Column(
		Text
	)
	URI = Column(
		Text,
		index=True,
	)
	Properties = Column(
		Text
	)

	def __js__(self):
		return dict(
			id=self.RelationTemplateID,
			name=self.TemplateName,
			description=self.Description,
		)
	
	def __str__(self):
		return json.dumps(self.__js__())
	

#_________________________________________________
class Relation(Base):
	__tablename__ = 'Relations'

	RelationID = Column(
		Integer,
		Sequence('sqlite_sequence'),
		primary_key=True,
	)
	IDFrom = Column(
		Integer,
		ForeignKey("Items.ItemID"),
	)
	SequenceFrom = Column(
		Integer
	)
	IDTo = Column(
		Integer,
		ForeignKey("Items.ItemID"),
	)
	SequenceTo = Column(
		Integer
	)
	RelationTemplateID = Column(
		Integer,
		ForeignKey("RelationTemplates.RelationTemplateID"),
	)
	category = relationship(
		"RelationTemplate",
		foreign_keys=[RelationTemplateID],
	)
	VisibleUpToLevel = Column(
		Integer
	)
	Name = Column(
		Text
	)
	BackRelName = Column(
		Text
	)
	Description = Column(
		Text
	)
	DirectLinkURL = Column(
		Text
	)
	URI = Column(
		Text,
		index=True,
	)
	Properties = Column(
		Text
	)
	
	def __init__(self):
		self.SequenceFrom = 10
		self.SequenceTo = 10
		self.URI = str(uuid.uuid4()).upper()
		self.RelationTemplateID = -1
		self.Properties = '{}'
		self.DirectLinkURL = ''
		self.VisibleUpToLevel = 999999999
		self.Name = ''
		self.Description = ''
			
	_inbound = relationship(
		"Item",
		foreign_keys=[IDFrom],
		overlaps="outbound"
	)
	
	@property
	def inbound(self):
		return self._inbound

	@inbound.setter
	def inbound(self, value):
		if self not in value.inbound:
			value.inbound.append(self)
		self._inbound = value
		
	@inbound.deleter
	def inbound(self):
		if self in value.inbound:
			value.inbound.remove(self)
		del self._inbound

	_outbound = relationship(
		"Item",
		foreign_keys=[IDTo],
		overlaps="inbound"
	)
		
	@property
	def outbound(self):
		return self._outbound

	@outbound.setter
	def outbound(self, value):
		if self not in value.outbound:
			value.outbound.append(self)
		self._outbound = value
		
	@outbound.deleter
	def outbound(self):
		if self in value.outbound:
			value.outbound.remove(self)
		del self._outbound
		
	def __js__(self):
		return dict(
			URI=self.URI,
			id=self.RelationID,
			name=self.Name,
			description=self.Description,
			category=self.category.TemplateName if self.category else None,
			URL=self.DirectLinkURL,
			properties=self.Properties,
		)
	
	def __str__(self):
		return json.dumps(self.__js__())
	

#_________________________________________________
class Repository(Base):
	__tablename__ = 'Repository'

	RecordID = Column(
		Integer,
		Sequence('sqlite_sequence'),
		primary_key=True,
	)
	DataID = Column(
		Integer
	)
	ContentID = Column(
		Integer
	)
	SmallPreviewImgID = Column(
		Integer
	)
	LargePreviewImgID = Column(
		Integer
	)
	DataType = Column(
		Text
	)
	MimeType = Column(
		Text
	)
	Name = Column(
		Text
	)
	Description = Column(
		Text
	)
	URI = Column(
		Text,
		index=True,
	)
	Properties = Column(
		Text
	)


#_________________________________________________
@property
def t_SearchText(): 
	return Table(
		'SearchText', metadata,
		Column(
			'ItemID',
			Integer,
			index=True,
		),
		Column(
			'StartPos',
			Integer,
		),
		Column(
			'TextLC',
			Text,
			index=True,
		)
	)


#_________________________________________________
class UndoLog(Base):
	__tablename__ = 'UndoLog'

	StepID = Column(
		Integer,
		Sequence('sqlite_sequence'),
		primary_key=True,
	)
	UndoStatement = Column(
		Text
	)

	
#_________________________________________________
@property
def t_UndoPos():
	return Table(
		'UndoPos', metadata,
		Column(
			'Pos',
			Integer,
		),
		Column(
			'UserID',
			Integer,
			index=True,
		)
	)


#_________________________________________________
@property
def t_UndoStack():
	return Table(
		'UndoStack', metadata,
		Column(
			'UndoStep',
			Integer,
		),
		Column(
			'UserID',
			Integer,
		),
		Column(
			'FirstStepID',
			Integer,
		),
		Column(
			'StepCount',
			Integer,
		),
		Column(
			'Description',
			Text,
		),
		Column(
			'Properties',
			Text,
		),
		Index(
			'UndoStack_UndoStep_IDX',
			'UndoStep',
			'UserID',
		)
	)


#_________________________________________________
class User(Base):
	__tablename__ = 'Users'

	UserID = Column(
		Integer,
		Sequence('sqlite_sequence'),
		primary_key=True
	)
	UserName = Column(
		Text
	)
	UserNameLC = Column(
		Text,
		index=True
	)
	Password = Column(
		Text
	)
	WorkspaceProperties = Column(
		Text
	)
	UserProperties = Column(
		Text
	)


#_________________________________________________
@property
def t_sqlite_sequence():
	return Table(
		'sqlite_sequence', metadata,
		Column(
			'name',
			NullType,
		),
		Column(
			'seq',
			NullType,
		)
	)

