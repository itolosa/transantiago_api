#!/usr/bin/env python
# encoding: utf-8

import datetime
from urllib2 import build_opener, HTTPCookieProcessor
import urllib
from cookielib import MozillaCookieJar
from lxml import etree
import socket
import requests

# TODO:
#  - sacar la salida en un arbol lxml usando newTree
#  - usar keep-alive en las conexiones
#  - posiblemente usar gevent que permite sockets no bloqueantes
#  - opcion de pasar el trafico por un servidor proxy
#  - cambiar el user-agent automaticamente
#  - estados de conexion (suggest-retry, no-response, etc)
#  - normalizar la sintaxis <<

class WebBrowser(object):
    '''mantiene en memoria las cookies, emulando un navegador
       *actualmente no ejecuta javascript'''
    def __init__(self, uAgent=None, headers=None):
        '''uAgent es el agente de usuario'''
        self.cookie_j = MozillaCookieJar()
        if uAgent is None:
            uAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36'
        self.opener = build_opener(HTTPCookieProcessor(self.cookie_j))
        self.user_agent = uAgent
        self.opener.addheaders = [('User-Agent', self.user_agent)]
        # self.session = requests.Session()
        # self.session.headers.update({ 'User-Agent': uAgent })
        # self.session.max_redirects = 20
        self.timeout = 25
        socket.setdefaulttimeout(self.timeout)

    def newtree(f):
        return lambda *a, **k: etree.parse(f(*a, **k), parser=etree.HTMLParser())

    @newtree
    def fetch(self, url, data=None, headers=None, method='POST'):
        '''obtiene los datos de una pagina web, ingresada en url
           para enviar datos por post, pasar codificados por data'''
        if headers:
            self.opener.addheaders = headers

        if not (data == None or type(data) == str):
            data = urllib.urlencode(data)

        if method == 'POST':
            # self.last_seen = self.session.post(url, data=data)
            self.last_seen = self.opener.open(url, data)
        elif method == 'GET':
            #self.last_seen = self.session.get(url + '?' + data)
            if data is None:
                self.last_seen = self.opener.open(url)
            else:
                self.last_seen = self.opener.open(url + '?' + data)
        else:
            raise Exception
        return self.last_seen

    def geturl(self):
        return self.last_seen.geturl()

    def save_cookies(self, path):
        '''guarda los cookies en memoria al disco'''
        '''path es el directorio'''
        self.cookie_j.save(path, ignore_discard=True, ignore_expires=True)

    def load_cookies(self, path):
        '''carga cookies del disco a la memoria'''
        '''path es el directorio'''
        self.cookie_j.load(path, ignore_discard=True, ignore_expires=True)

    def print_cookies(self):
        for cookie in self.cookie_j:
            print cookie.name, cookie.value

class ReqBrowser (object):

    def __init__(self, ua=None):
        if ua is None:
            ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36'
        self.sess = requests.Session()
        self.sess.headers.update({ 'User-Agent': ua })
        self.sess.max_redirects = 25
        # self.sess.stream = True
        self.default_timeout = 5
        self.allowredir = True
        self.last_seen = None

    def fetch(self, method, url, params=None, data=None, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        r = self.sess.request(method=method,
                url=url,
                params=params,
                data=data,
                allow_redirects=self.allowredir,
                timeout=timeout)
        self.last_seen = r
        return r

    def geturl(self, r=None):
        if r is None:
            r = self.last_seen
        return r.url


