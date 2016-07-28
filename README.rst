Spoon
=====

Simple to use pre-forking server interface.

.. image:: https://travis-ci.org/SpamExperts/spoon.svg?branch=master
  :target: https://travis-ci.org/SpamExperts/spoon
  
  
How to use a Spork
------------------

First create a handle class, that implements the code handling a single 
request. The class should inherit from ``spoon.server.Gulp`` and should 
implement the ``handle`` method. For example:


.. code-block::

  import spoon.server
  
  
  class RequestHandler(spoon.server.Gulp):
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
has a few tools. Simply call the `run_daemon` function with you 
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
server again. This can be achieved by addin a `load_config` method to 
the server class:

.. code-block::

  class MyEchoServer(spoon.server.TCPSpoon):
      server_logger = "my-echo-server"
      handler_klass = RequestHandler
  
      def load_config(self):
          # Load some configs for this server
          # These can be reloaded with SIGUSR1
          pass
          
After that the server can be signaled with the `send_action` function:

.. code-block::

  >>> import spoon.daemon
  >>> spoon.daemon.send_action("reload", "/var/tmp/my-echo-server.pid")
  >>> 

