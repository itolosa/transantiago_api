#!/usr/bin/env python
# encoding: utf-8
import os
import atexit
import sys
import signal
import time
import logging


class MasterDaemon (object):
    def __init__(self, infn, outfn, errfn):
        self.infn = infn
        self.outfn = outfn
        self.errfn = errfn
        self.pidfile = '/tmp/daemon.pid'
        self.wdir = '/'
        self.fmask = 0
        self.efail = 1
        self.eok = 0
        self.rstreams = True
        self.logger = logging.getLogger('daemon.MasterDaemon')

    def start(self):
        self.logger.info('starting daemon...')
        try:
            #check for a pid file
            self.logger.debug('checking for running instances')
            try:
                pf = file(self.pidfile, 'r', 0)
                pid = int(pf.read(100).strip())
                pf.close()
            except (AttributeError, TypeError, IOError):
                pid = None

            if pid:
                self.logger.info('daemon running: pid already exists!')
                #pid already exists
                sys.exit(self.efail)

            #create a child process and
            #exit master process inmediately
            self.logger.debug('doing first fork')
            try:
                pid = os.fork()
                if pid > 0:
                    sys.exit(self.eok)
                elif pid < 0:
                    raise OSError
            except OSError, e:
                self.logger.exception('Fallo primer fork')
                sys.exit(self.efail)

            #get the session leader flag
            self.logger.debug('trying to get sessid')
            try:
                sid = os.setsid()
                #if sid < 0:
                #    raise Exception
            except Exception:
                self.logger.exception('Fallo obtencion de session id')
                sys.exit(self.efail)

            #create a second, orphan, child
            #and exit the parent
            self.logger.debug('doing second fork')
            try:
                pid = os.fork()
                if pid > 0:
                    sys.exit(self.eok)
                elif pid < 0:
                    raise OSError
            except OSError, e:
                self.logger.exception('Fallo segundo fork')
                sys.exit(self.efail)


            #set file permissions mask (wx)
            #0 means all: (777)
            self.logger.debug('changing umask')
            os.umask(self.fmask)

            if self.rstreams:
                #create new fd's

                self.logger.debug("opening and redirecting standard fd's")
                errfd = os.open(os.path.abspath(self.errfn), os.O_WRONLY | os.O_CREAT | os.O_APPEND)
                infd = os.open(os.path.abspath(self.infn), os.O_RDONLY)
                outfd = os.open(os.path.abspath(self.outfn), os.O_WRONLY | os.O_CREAT | os.O_APPEND)
                
                
                # errfh = open(os.path.abspath(self.errfn), 'w+', buffering=0)
                # outfh = open(os.path.abspath(self.infn), 'w+')
                #infh = open(os.path.abspath(os.devnull), 'r')
                #close fdescriptors and file entry in unix file table
                #then redirect standard file descriptors

                os.dup2(errfd, sys.stderr.fileno())
                os.dup2(infd, sys.stdin.fileno())
                os.dup2(outfd, sys.stdout.fileno())
                
                #self.redir_stream(sys.stdin, None)
            else:
                #close standard file descriptors and handlers
                nullf = open(os.devnull, 'rw')
                sys.stderr.close()
                #sys.stdout.close()
                #sys.stdout = nullf
                sys.stdin.close()

                sys.stderr = nullf
                #sys.stdout = nullf
                sys.stdin = nullf

            self.logger.debug('changing working dir')
            os.chdir(self.wdir)

            #at exit delete pid lock file
            self.logger.debug('registering atexit functions')
            atexit.register(self.delpid)
            #atexit.register(lambda: self.exit(self.eok))

            #save actual pid as a lock file
            self.logger.debug('saving pid')
            pid = str(os.getpid())
            fp = file(self.pidfile, 'w+')
            fp.write("%s\n" % pid)
            fp.close()

            #run the main task
            self.logger.debug('running main task')
            self.run()

            sys.exit(self.eok)
        except (OSError):
            sys.stderr.write('!!! Ha ocurrido a una excepcion en el demonio!')
            sys.exit(self.efail)

    def redir_stream(self, sys_stream, target_fd):
        # if target_stream is None:
        #     target_fd = os.open(os.devnull, os.O_RDWR)
        # else:
        #     target_fd = target_stream.fileno()
        os.dup2(target_fd, sys_stream.fileno())

    def delpid(self):
        try:
            os.remove(self.pidfile)
        except OSError, e:
            pass

    def stop(self):
        self.logger.info('stopping daemon...')
        #get the pid from the pidfile
        try:
            pf = file(self.pidfile, 'r', 0)
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        #try killing the daemon process
        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.2)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                self.delpid()
            else:
                print err
                sys.exit(1)

    def restart(self):
        self.logger.info('restarting daemon...')
        self.stop()
        self.start()

    def run(self):
        pass
