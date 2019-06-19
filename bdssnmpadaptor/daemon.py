# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#

import atexit
import os
import signal
import sys
import tempfile

from bdssnmpadaptor.error import BdsError


def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            os._exit(0)

    except OSError as exc:
        raise BdsError(f'Fork #1 failed: {exc}')

    # decouple from parent environment
    try:
        os.chdir('/')
        os.setsid()

    except OSError:
        pass

    os.umask(0)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent
            os._exit(0)

    except OSError as exc:
        raise BdsError(f'Fork #2 failed: {exc}')

    def signal_cb(s, f):
        raise KeyboardInterrupt

    for s in signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT:
        signal.signal(s, signal_cb)

    # redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = open(os.devnull, 'r')
    so = open(os.devnull, 'a+')
    se = open(os.devnull, 'a+')

    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


def pidfile(filename):

    def cbFun():
        try:
            if pidfile:
                os.remove(filename)

        except OSError:
            pass

    atexit.register(cbFun)

    try:
        if filename:
            try:
                with open(filename) as pf:
                    pid = int(pf.read())

                os.kill(pid, 0)

                raise BdsError(
                    f'Process {pid} still running (see {filename})')

            except (IOError, ProcessLookupError, ValueError):
                pass

            fd, nm = tempfile.mkstemp(dir=os.path.dirname(filename))
            os.write(fd, ('%d\n' % os.getpid()).encode('utf-8'))
            os.close(fd)
            os.rename(nm, filename)

    except Exception as exc:
        raise BdsError(
            f'Failed to create PID file {filename}: {exc}')
