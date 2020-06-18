# -*- coding: utf-8 -*-

from time import time as now
import re

from formats_common import *

enable = True
format = "WikipediaDump"
description = "Wikipedia Dump (.xml)"
extensions = [".xml"]
optionsProp = {
	"encoding": EncodingOption(),
	"pageCount": IntOption(),
}
depends = {
#	"pijnu": "pijnu>=20160727",  # dependency of mediawiki-parser
#	"mediawiki_parser": "mediawiki-parser",
}



"""
BeautifulSoup = None

def loadBeautifulSoup():
	global BeautifulSoup
	try:
		import bs4 as BeautifulSoup
	except:
		import BeautifulSoup
	if int(BeautifulSoup.__version__.split(".")[0]) < 4:
		raise ImportError(
			"BeautifulSoup is too old, required at least version 4, "
			f"{BeautifulSoup.__version__ !r} found.\n"
			"Please run `sudo pip3 install lxml beautifulsoup4 html5lib`"
		)
"""

class Reader(object):
	def __init__(self, glos):
		self._glos = glos
		self._buff = b""
		self._filename = ""
		self._file = None
		self._len = 0
		# self._alts = {}
		# { word => alts }
		# where alts is str (one word), or list of strs
		# we can't recognize alternates unless we keep all data in memory
		# or scan the whole directiry and read all files twice

	def _readUntil(self, sub: bytes) -> bytes:
		for line in self._file:
			if sub in line:
				return line
			self._buff += line

	def _readSiteInfo(self) -> bytes:
		self._buff = self._readUntil(b"<siteinfo>")
		self._buff += self._readUntil(b"</siteinfo>")
		siteinfoBytes = self._buff
		self._buff = b""
		return siteinfoBytes

	def open(self, filename, pageCount=0):
		try:
			from lxml import etree
		except ModuleNotFoundError as e:
			e.msg += ", run `sudo pip3 install lxml` to install"
			raise e
		#try:
		#	from mediawiki_parser.preprocessor import make_parser as make_preprocessor
		#	from mediawiki_parser.html import make_parser
		#except ModuleNotFoundError as e:
		#	e.msg += ", run `sudo pip3 install mediawiki-parser` to install"
		#	raise e

		self._len = pageCount
		self._filename = filename
		self._file = open(filename, mode="rb")
		
		siteinfoBytes = self._readSiteInfo()
		# TODO: parse siteinfoBytes

		"""
		templates = {}
		allowed_tags = []
		allowed_self_closing_tags = []
		allowed_attributes = []
		interwiki = {}
		namespaces = {}

		self._preprocessor = make_preprocessor(templates)
		self._parser = make_parser(
			allowed_tags,
			allowed_self_closing_tags,
			allowed_attributes,
			interwiki,
			namespaces,
		)
		"""

	def close(self):
		self._filename = ""
		self._file.close()
		self._len = 0
		# self._alts = {}

	def __len__(self):
		return self._len

	def _readPage(self) -> "lxml.etree.Element":
		from lxml import etree as ET
		pageEnd = self._readUntil(b"</page>")
		if pageEnd is None:
			return
		page = ET.fromstring(self._buff + pageEnd)
		self._buff = b""
		return page

	def __iter__(self) -> "Iterator[BaseEntry]":
		from lxml import etree as ET
		if not self._filename:
			log.error(
				"WikipediaDump: trying to iterate over reader"
				" while it's not open"
			)
			raise StopIteration
		while True:
			page = self._readPage()
			if page is None:
				break
			yield self._getEntryFromPage(page)


	def _getEntryFromPage(self, page: "lxml.etree.Element") -> "BaseEntry":
		# from wikimarkup.parser import parselite
		from plugin_lib.wikimarkup.parser import parselite
		titleElem = page.find(".//title")
		if titleElem is None:
			return
		title = titleElem.text
		if not title:
			return
		textElem = page.find(".//text")
		if textElem is None:
			return
		text = textElem.text
		if not text:
			return
		# ptext = self._preprocessor.parse(text)
		# log.info(f"type(ptext) = {type(ptext)}")
		# arg to self._parser.parse must be a Node obj, not str
		# text = str(self._parser.parse(ptext))
		text = parselite(text)
		return self._glos.newEntry(title, text)
