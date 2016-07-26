"""Exposes UDP/TCP servers that can handle requests and
can be stopped gracefully or reloaded.
"""

from __future__ import absolute_import

import os
import errno
import socket
import signal
import logging
import threading
try:
    import socketserver
except ImportError:
    import SocketServer as socketserver


def _eintr_retry(func, *args):
    """restart a system call interrupted by EINTR"""
    while True:
        try:
            return func(*args)
        except OSError as e:
            if e.args[0] != errno.EINTR:
                raise


class Gulp(socketserver.StreamRequestHandler):
    """Handle a single request."""

    def handle(self):
        """Get the command from the client and pass it to the
        correct handler.
        """
        raise NotImplementedError()


class _TCPServer(socketserver.TCPServer, object):
    """Converted to newstyle class."""


class _UDPServer(socketserver.UDPServer, object):
    """Converted to newstyle class."""


class _SpoonMixIn(object):
    """A server that consumes Gulps in a single thread and
    single process.
    """
    server_logger = "spoon-server"
    handler_klass = Gulp
    # Custom signal handling
    signal_reload = signal.SIGUSR1
    signal_shutdown = signal.SIGTERM
    # Socket options.
    ipv6_only = False
    allow_reuse_address = True

    def __init__(self, address):
        self.log = logging.getLogger(self.server_logger)
        self.socket = None
        if ":" in address[0]:
            self.address_family = socket.AF_INET6
        else:
            self.address_family = socket.AF_INET
        self.log.debug("Listening on %s", address)

        super(_SpoonMixIn, self).__init__(address, self.handler_klass,
                                          bind_and_activate=False)
        if self.allow_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if not self.ipv6_only:
            try:
                self.socket.setsockopt(socket.IPPROTO_IPV6,
                                       socket.IPV6_V6ONLY, 0)
            except (AttributeError, socket.error) as e:
                self.log.debug("Unable to set IPV6_V6ONLY to false %s", e)
        self.load_config()
        self.server_bind()
        self.server_activate()

        # Finally, set signals
        if self.signal_reload is not None:
            signal.signal(self.signal_reload, self.reload_handler)
        if self.signal_shutdown is not None:
            signal.signal(self.signal_shutdown, self.shutdown_handler)

    def load_config(self):
        """Reads the configuration files, this is called when
        the reload handler is received.

        Can be reimplemented.
        """

    def shutdown_handler(self, *args, **kwargs):
        """Handler for the SIGTERM signal. This should be used to kill the
        daemon and ensure proper clean-up.
        """
        self.log.info("SIGTERM received. Shutting down.")
        t = threading.Thread(target=self.shutdown)
        t.start()

    def reload_handler(self, *args, **kwargs):
        """Handler for the SIGUSR1 signal. This should be used to reload
        the configuration files.
        """
        self.log.info("SIGUSR1 received. Reloading configuration.")
        t = threading.Thread(target=self.load_config)
        t.start()

    def handle_error(self, request, client_address):
        self.log.error("Error while processing request from: %s",
                       client_address, exc_info=True)


class _SporkMixIn(_SpoonMixIn):
    """The same as Spoon, but allows consuming Gulps with more than
    one spoon by pre-forking when starting the server.

    The parent Spoon process will then wait for all his child
    process to complete.
    """

    def __init__(self, address, prefork=4):
        """The same as Server.__init__ but requires a list of databases
        instead of a single database connection.
        """
        self.pids = None
        self._prefork = prefork
        _SpoonMixIn.__init__(self, address)

    def serve_forever(self, poll_interval=0.5):
        """Fork the current process and wait for all children to finish."""
        pids = []
        for dummy in range(self._prefork):
            pid = os.fork()
            if not pid:
                super(_SporkMixIn, self).serve_forever(
                    poll_interval=poll_interval)
                os._exit(0)
            else:
                self.log.info("Forked worker %s", pid)
                pids.append(pid)
        self.pids = pids
        for pid in self.pids:
            _eintr_retry(os.waitpid, pid, 0)

    def shutdown(self):
        """If this is the parent process send the TERM signal to all children,
        else call the super method.
        """
        for pid in self.pids or ():
            os.kill(pid, signal.SIGTERM)
        if self.pids is None:
            super(_SporkMixIn, self).shutdown()

    def load_config(self):
        """If this is the parent process send the USR1 signal to all children,
        else call the super method.
        """
        for pid in self.pids or ():
            os.kill(pid, signal.SIGUSR1)
        if self.pids is None:
            super(_SporkMixIn, self).load_config()


class TCPSpoon(_SpoonMixIn, _TCPServer):
    """A TCP Socket server that handles everything in a
    single process.
    """


class TCPSpork(_SporkMixIn, _TCPServer):
    """A TCP Socket server that pre-forks a number of child
    processes.
    """


class UDPSpoon(_SpoonMixIn, _UDPServer):
    """A UDP Socket server that handles everything in a
    single process.
    """


class UDPSpork(_SporkMixIn, _UDPServer):
    """A UDP Socket server that pre-forks a number of child
    processes.
    """
