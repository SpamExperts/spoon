import signal
import unittest

from mock import patch, call

import spoon.server


class TestSpoon(unittest.TestCase):

    def setUp(self):
        self.mock_socket = patch("spoon.server.socket", create=True).start()
        self.mock_sock = patch("spoon.server.TCPSpoon.socket",
                               create=True).start()
        self.mock_bind = patch(
            "spoon.server.TCPSpoon.server_bind").start()
        self.mock_active = patch(
            "spoon.server.TCPSpoon.server_activate").start()
        self.mock_signal = patch("spoon.server.signal.signal",
                                 create=True).start()
        self.mock_thread = patch("spoon.server.threading.Thread").start()

    def test_shutdown(self):
        server = spoon.server.TCPSpoon(("0.0.0.0", 783))
        server.shutdown_handler()
        self.mock_thread.assert_called_with(target=server.shutdown)

    def test_reload(self):
        server = spoon.server.TCPSpoon(("0.0.0.0", 783))
        server.reload_handler()
        self.mock_thread.assert_called_with(target=server.load_config)

    def test_server_signals(self):
        server = spoon.server.TCPSpoon(("0.0.0.0", 783))
        calls = [
            call(signal.SIGUSR1, server.reload_handler),
            call(signal.SIGTERM, server.shutdown_handler)
        ]
        self.mock_signal.assert_has_calls(calls)


class TestSpork(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mock_socket = patch("spoon.server.socket", create=True).start()
        self.mock_sock = patch("spoon.server.TCPSpork.socket",
                               create=True).start()
        # self.mock_forever = patch(
        #     "spoon.server.TCPSpork.serve_forever").start()
        self.mock_kill = patch("spoon.server.os.kill", create=True).start()
        patch("spoon.server.socketserver").start()
        patch("spoon.server._eintr_retry").start()
        self.mock_bind = patch("spoon.server.TCPSpork.server_bind").start()
        self.mock_active = patch(
            "spoon.server.TCPSpork.server_activate").start()
        self.mock_signal = patch("spoon.server.signal.signal",
                                 create=True).start()
        self.mock_thread = patch("spoon.server.threading.Thread").start()
        self.mock_fork = patch("spoon.server.os.fork", create=True).start()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        patch.stopall()

    def test_server_forever(self):
        server = spoon.server.TCPSpork(("0.0.0.0", 783))
        server.serve_forever()
        self.assertEqual(len(server.pids), 4)

    def test_master_shutdown(self):
        shutdown = patch("spoon.server.TCPSpoon.shutdown").start()
        server = spoon.server.TCPSpork(("0.0.0.0", 783))
        server.prefork = 2
        server.pids = [100, 101]
        server.shutdown()
        calls = [
            call(100, signal.SIGTERM),
            call(101, signal.SIGTERM),
        ]
        self.mock_kill.assert_has_calls(calls)

    def test_worker_shutdown(self):
        shutdown = patch("spoon.server._TCPServer.shutdown").start()
        server = spoon.server.TCPSpork(("0.0.0.0", 783))

        server.prefork = 2
        server.pids = None
        server.shutdown()
        shutdown.assert_called_with()

    def test_master_reload(self):
        server = spoon.server.TCPSpork(("0.0.0.0", 783))

        server.prefork = 2
        server.pids = [100, 101]
        server.load_config()
        calls = [
            call(100, signal.SIGUSR1),
            call(101, signal.SIGUSR1),
        ]
        self.mock_kill.assert_has_calls(calls)

    def test_worker_reload(self):
        load_config = patch("spoon.server._SpoonMixIn.load_config").start()
        server = spoon.server.TCPSpork(("0.0.0.0", 783))

        server.prefork = 2
        server.pids = None
        server.load_config()
        load_config.assert_called_with()

