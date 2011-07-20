#!/usr/bin/env python
# -*- coding: utf8 -*-

"""Python client library for sabi.ufrgs.br

Esta biblioteca visa oferecer acesso a recursos do Sistema de Automação de 
Bibliotecas da UFRGS (SABi) através de uma API simples em Python, e é 
baseado em uma técnica chamada "web scraping", que consiste em puxar
informações interessantes de páginas web.
	
Uso:
	s = SABi(123456, 112233)
	print "Livros Emprestados: " + s.loan()
	print "Livros Reservados: " + s.hold()
	print "Dívida: " + s.cash()

"""

from random import randint
from urllib import urlencode
import urllib2
import re

class SABi:
	def __init__(self, username, password):
		"""Construtor

		Tanto username quanto password devem ser valores numéricos,
		O sistema do SABi é baseado no sistema de matrículas da UFRGS, e 
		portanto o username é o número da matrícula (8 dígitos, zero-fill)
		e a senha é outro número de 6 dígitos.
		"""
		self.res = "http://sabi.ufrgs.br/F/"
		self.data = {
			'loan': None,
			'hold': None,
			'cash': None,
		}
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
		page = urllib2.urlopen(self.res).read()
		m = re.search('\/([A-Z0-9]+)-[0-9]{5}\?.*?login-session', page)
		self.session = m.group(1)
		login_link = self.res + self.session + '-' + str(randint(10000,99999))
		data = {
			'func': 'login-session',
			'login_source': 'bor-info',
			'bor_library': 'URS50',
			'bor_id': self.username,
			'bor_verification': self.password,
			'x': 0,
			'y': 0,
		}
		# Aproveita para recuperar alguns dados úteis
		page = urllib2.urlopen(login_link, urlencode(data)).read()
		self.data['loan'] = re.search('bor-loan.*>([0-9\.-]+)', page).group(1)
		self.data['hold'] = re.search('bor-hold.*>([0-9\.-]+)', page).group(1)
		self.data['cash'] = re.search('bor-cash.*>([0-9\.-]+)', page).group(1)

	""" Exemplos """
	def loan(self):
		return self.data['loan']

	def hold(self):
		return self.data['hold']
	
	def cash(self):
		return self.data['cash']