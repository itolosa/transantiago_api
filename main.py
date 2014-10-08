#!/usr/bin/env python

import datetime
import logging
import os
import os.path
import urlparse
import sys
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

from libs import scraper
from libs import daemon

def touch(path):
  with open(path, 'a'):
    os.utime(path, None)

class Daemon(daemon.MasterDaemon):
  def run(self):
    try:
      HOST = ''
      PORT = 6969
      server = ThreadedHTTPServer((HOST, PORT), Handler)
      global s
      s = scraper.Scraper()
      server.serve_forever()
      raise Exception
    except (KeyboardInterrupt, Exception):
      self.logger.exception('Excepcion en run. Exiting...')
      self.stop()

class Handler(BaseHTTPRequestHandler):
  def log_message(self, sformat, *args):
    self.server.logger.info(sformat % args)
      
  def do_GET(self):
    p = urlparse.urlparse(self.path)
    if p.path == '/transantiago/api':
      self.server.logger.debug('query aceptada')
      self.send_response(200)
      self.end_headers()
      self.server.logger.debug('headers enviados')
      param = dict(urlparse.parse_qsl(p.query))
      self.server.logger.info('Agregando query a consulta')
      init_time = datetime.datetime.now()
      response = s.scrap(param['pid'])
      end_time = datetime.datetime.now()
      totdur = end_time - init_time
      self.wfile.write(response)
      self.server.logger.info('%s [OK] Completado en %f segundos' % \
              (param['pid'], totdur.total_seconds()))
    else:
      self.send_response(404)
      self.end_headers()
      self.wfile.write('0')

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('server.handler')
        HTTPServer.__init__(self, *args, **kwargs)

if __name__ == '__main__':
  devnull = os.devnull
  daemon = Daemon(devnull, 'log/stdout.log', 'log/stderr.log')
  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      paths = ['log/service.log', 'log/stdout.log', 'log/stderr.log']
      for p in paths:
        if not os.path.isfile('log/service.log'):
          touch('log/service.log')
      #set conf here because os.chdir generates an error
      logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M',
        filename='log/service.log',
        filemode='a')
      daemon.start()
    elif 'stop' == sys.argv[1]:
      daemon.stop()
    elif 'restart' == sys.argv[1]:
      daemon.restart()
    else:
      print "Unknown command"
      sys.exit(2)
    sys.exit(0)
  else:
    print "usage: %s start|stop|restart" % sys.argv[0]
    sys.exit(2)
