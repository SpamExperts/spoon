Spoon
=====

Simple to use pre-forking server interface.

.. image:: https://travis-ci.org/SpamExperts/spoon.svg?branch=master
  :target: https://travis-ci.org/SpamExperts/spoon

Installing
----------

Spoon can be installed via pip:

.. code-block::

  pip install spoon


Compatibility
-------------

Spoon is compatible with:

 - Python 2.7
 - Python 3.2+
 - PyPy
 - PyPy 3

Requirements
------------

No external dependecies

How to use a Spork
------------------

First create a handle class, that implements the code handling a single
request. The class should inherit from ``spoon.server.TCPGulp`` (for a
TCP server) or ``spoon.server.UDPGulp`` (for a UDP server) and should
implement the ``handle`` method. For example:


.. code-block::

  import spoon.server


  class RequestHandler(spoon.server.TCPGulp):
      def handle(self):
          request = self.rfile.readline().decode("utf8")
          response = request.lower().encode("utf8")
          self.wfile.write(response)


Then implement the server logic by creating a new class the inherits from
the ``Spoon`` or ``Spork``


.. code-block::

  class MyEchoServer(spoon.server.TCPSpoon):
      server_logger = "my-echo-server"
      handler_klass = RequestHandler

  class MyEchoServerForked(MyEchoServer, spoon.server.TCPSpork):
      prefork = 6


Then start the normal or forked server:

.. code-block::

  server = MyEchoServerForked(("::0", 30111))
  server.serve_forever()

Then you can send and receive data from that server

.. code-block::

  >>> import socket
  >>> connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  >>> connection.connect(("127.0.0.1", 30111))
  >>> connection.send("Test")
  4
  >>> connection.shutdown(socket.SHUT_WR)
  >>> connection.recv(1024)
  'test'


Daemonized Sporks
-----------------

It's usually convenient to run the server as a daemon for this spoon
has a few tools. Simply call the ``run_daemon`` function with you
server:

.. code-block::

  import spoon.daemon

  server = MyEchoServerForked(("::0", 30111))
  spoon.daemon.run_daemon(server, "/var/tmp/my-echo-server.pid")

To kill the server gracefully you can use the `send_action` function:

.. code-block::

  >>> import spoon.daemon
  >>> spoon.daemon.send_action("stop", "/var/tmp/my-echo-server.pid")
  >>>


Reloading Sporks
----------------

Another useful tool for a daemon is signaling it that the configuration
changed and it should be reloaded without the stopping and starting the
server again. This can be achieved by adding a ``load_config`` method to
the server class:

.. code-block::

  class MyEchoServer(spoon.server.TCPSpoon):
      server_logger = "my-echo-server"
      handler_klass = RequestHandler

      def load_config(self):
          # Load some configs for this server
          # These can be reloaded with SIGUSR1
          pass

After that the server can be signaled with the ``send_action`` function:

.. code-block::

  >>> import spoon.daemon
  >>> spoon.daemon.send_action("reload", "/var/tmp/my-echo-server.pid")
  >>>


Managing Daemons via command-line
---------------------------------

You can also manage Spork Daemons via the command line with the
``spoon.daemon`` module. First set your default command line options
in your Spork class. For example:

.. code-block::

  class MyEchoServer(spoon.server.TCPSpoon):
      server_logger = "my-echo-server"
      handler_klass = RequestHandler
      command_line_defaults = {
        "port": 30111,
        "interface": "::0",
        "pid_file": "/var/tmp/my-echo-server.pid",
        "log_file": "/var/log/my-echo-server.log",
        "sentry_dsn": None,
        "spork": 12,
      }

Then call the ``spoon.daemon`` via the command line to start/stop/reload
your Spork. Some examples:

.. code-block::

  $ python -m spoon.daemon echo.server.MyEchoServerForked start
  $ python -m spoon.daemon echo.server.MyEchoServerForked stop
  $ python -m spoon.daemon echo.server.MyEchoServerForked restart
  $ python -m spoon.daemon echo.server.MyEchoServerForked reload

This will automatically take care of:

 * Setting up the Spork to fork
 * Configuring the interface and port
 * Setting the pid file
 * Setting up logging
 * Starting and detaching the Spork server

License
-------

The project is licensed under the GNU GPLv2 license.
