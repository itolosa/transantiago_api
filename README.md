transantiago_api
================

API para el transantiago. Te dice cuales son las micros que van a pasar según el paradero.
Es un scraper para http://web.simt.cl/web/

Requerimientos
==============
Python 2.x con lxml (http://lxml.de) instalado.
Máquina con un sistema unix-like. (linux, os x, etc).
No esta pensado para Windows pero podría funcionar.

Uso
===
Correr servidor: 
```
./main.py start
```

Detener servidor:
```
./main.py stop
```

Reiniciar servidor:
```
./main.py restart
```
(no siempre funciona, mejor hacer stop y start).

Nota: tambien puedes hacer los comandos con: python main.py xxxx

El servidor estara en http://127.0.0.1:6969/transantiago/api?pid=PC616
Donde pid es el id de paradero.

Contibuciones
=============
Estas invitado a hacer fork del proyecto y cooperar para mantener y mejorar el software :D
Hace pull-request o abre un issue cuando quieras.

Happy coding!
