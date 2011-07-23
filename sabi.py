#!/usr/bin/env python
# -*- coding: utf8 -*-

"""Python client library for sabi.ufrgs.br

Esta biblioteca visa oferecer acesso a recursos do Sistema de Automação de 
Bibliotecas da UFRGS (SABi) através de uma API simples em Python, e é 
baseado em uma técnica chamada "web scraping", que consiste em puxar
informações interessantes de páginas web.
	
Uso:
	s = SABi(123456, 112233)
	
"""

from random import randint
from BeautifulSoup import BeautifulSoup
from urllib import urlencode
import urllib2
import re

class SABiRequester: 
	def __init__(self, username, password):
		"""Construtor

		Tanto username quanto password devem ser valores numéricos,
		O sistema do SABi é baseado no sistema de matrículas da UFRGS, e 
		portanto o username é o número da matrícula (8 dígitos, zero-fill)
		e a senha é outro número de 6 dígitos.
		"""
		self.res = "http://sabi.ufrgs.br/F/"
		self.session = None
		self.username = "%08d" % username  # zerofill
		self.password = password
		self.__auth()

	def __auth(self):
		"""Autenticação do Usuário

		É necessário um acesso a página para puxar uma variável de sessão.
		A esta variável é usada na montagem dos links, em um formato +- assim:
			res + '/'' + session + '-' + randomnum(5) + '?func=' + funcao
		Onde função é o que realmente orienta o sistema. Agumas delas abaixo:
			- bor-info
			- bor-loan
			- bor-cash
			- bor-history-loan
			- ...
		"""
		if (self.session is not None): return
		page = self.getpage()
		m = re.search('\/([A-Z0-9]+)-[0-9]{5}\?.*?login-session', page)
		self.session = m.group(1)
		data = {
			'func': 'login-session',
			'login_source': 'bor-info',
			'bor_library': 'URS50',
			'bor_id': self.username,
			'bor_verification': self.password,
			'x': 0,
			'y': 0,
		}
		# loga via POST
		self.getpage(self.__mklink(), urlencode(data))
		return True

	def __mklink(self, func = None):
		"""Gerador de links"""
		if self.session is not None:
			query = '?adm_library=URS50&func=bor-' + func if func else ''
			link = self.res + self.session + '-' + str(randint(10000,99999)) 
			link = link + query
		else:
			link = self.res
		return link

	def getpage(self, func = None, param = None):
		link = self.__mklink(func)
		page = urllib2.urlopen(link, param).read()
		# remoção de comentários e novas-linhas
		page = re.sub('<!--.*?-->', '', page.replace('\n', ''))
		return page

	def getsoup(self, func = None, param = None):
		"""Busca uma pagina e retorna um soup"""
		page = self.getpage(func, param)
		return BeautifulSoup(page, convertEntities=BeautifulSoup.HTML_ENTITIES)
	
	def getlist(self, func):
		soup = self.getsoup(func)

		table = soup.find('table', cellspacing=2)
		trs = table.findAll('tr')

		itens = []
		headers = [th.text for th in trs[0].findAll('th')]
		for tr in trs[1:]:
			data = [
				(td.text, td.a.get('href')) if td.a else td.text
				for td 
				in tr.findAll('td')
			]
			data = dict(zip(headers, data))
			itens.append(data)

		return itens

class SABi:
	def __init__(self, username, password):
		self.r = SABiRequester(username, password)
	
	def loanList(self):
		return self.r.getlist('loan')