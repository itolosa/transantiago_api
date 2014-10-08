import basebrowser
import datetime
import json

class Scraper(object):
  def __init__(self):
    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:31.0) Gecko/20100101 Firefox/31.0'
    self.reqheaders = [
      ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
      ('Accept-Encoding', 'gzip, deflate'),
      ('Accept-Language', 'en-US,en;q=0.5'),
      ('Connection', 'keep-alive'),
      ('Host', 'web.smsbus.cl'),
      ('Referer', 'http://web.smsbus.cl/web/buscarAction.do?d=cargarServicios'),
      ('User-Agent', ua)
    ]
    self.browser = basebrowser.WebBrowser(uAgent=ua)
    self.last_reload = datetime.datetime.now()
    self.reload_cookies()
    self.reload_quantum = 300

  def reload_cookies(self):
    return self.browser.fetch('http://web.smsbus.cl/web/buscarAction.do?d=cargarServicios', method='GET')
  
  def _parse(self, parse_tree):
    out = list()
    aux_k = ['service', 'bus','eta', 'dist']
    for div in parse_tree.find('//div[@id="contenido_respuesta_2"]').xpath('//div[@id="siguiente_respuesta"] | //div[@id="proximo_solo_paradero"]'):
      pt = filter(lambda x: len(x), [e.strip() for e in div.itertext()])
      out.append(dict(zip(aux_k, pt)))
    return out

  def json_output(f):
    return lambda *a, **k: json.dumps(f(*a, **k))

  @json_output
  def scrap(self, pid):
    #pid = 'PC616'
    deltatime = self.last_reload - datetime.datetime.now()
    if deltatime.total_seconds() > self.reload_quantum:
      self.reload_cookies()
      self.last_reload = datetime.datetime.now()

    params = (
      ('d', 'busquedaParadero'),
      ('destino_nombre', 'rrrrr'),
      ('servicio', '-1'),
      ('destino', '-1'),
      ('paradero', '-1'),
      ('busqueda_rapida', 'PC616 C08'),
      ('ingresar_paradero', pid)
    )
    response = self.browser.fetch('http://web.smsbus.cl/web/buscarAction.do', data=params, headers=self.reqheaders)
    return self._parse(response)