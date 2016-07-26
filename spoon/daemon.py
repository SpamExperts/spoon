"""Exposes tools for daemonizing."""

from __future__ import print_function

import os
import sys
import signal


def detach(stdout="/dev/null", stderr=None, stdin="/dev/null", pidfile=None):
    """This forks the current process into a daemon.

    The stdin, stdout, and stderr arguments are file names that
    will be opened and be used to replace the standard file descriptors
    in sys.stdin, sys.stdout, and sys.stderr.

    These arguments are optional and default to /dev/null.

    Note that stderr is opened unbuffered, so if it shares a file with
    stdout then interleaved output may not appear in the order that you
    expect."""
    # Do first fork.
    try:
        pid = os.fork()
        if pid > 0:
            # Exit first parent.
            sys.exit(0)
    except OSError as err:
        print("Fork #1 failed: (%d) %s" % (err.errno, err.strerror),
              file=sys.stderr)
        sys.exit(1)

    # Decouple from parent environment.
    os.chdir("/")
    os.umask(0)
    os.setsid()

    # Do second fork.
    try:
        pid = os.fork()
        if pid > 0:
            # Exit second parent.
            sys.exit(0)
    except OSError as err:
        print("Fork #2 failed: (%d) %s" % (err.errno, err.strerror),
              file=sys.stderr)
        sys.exit(1)

    # Open file descriptors and print start message.
    if not stderr:
        stderr = stdout
    stdi = open(stdin, "r")
    stdo = open(stdout, "a+")
    stde = open(stderr, "ab+", 0)
    pid = str(os.getpid())
    if pidfile:
        with open(pidfile, "w+") as pidf:
            pidf.write("%s\n" % pid)

    # Redirect standard file descriptors.
    os.dup2(stdi.fileno(), sys.stdin.fileno())
    os.dup2(stdo.fileno(), sys.stdout.fileno())
    os.dup2(stde.fileno(), sys.stderr.fileno())


def run_daemon(server, pidfile, daemonize=True):
    """Run the server as a daemon

    :param server: cutlery (a Spoon or Spork)
    :param pidfile: the file to keep the parent PID
    :param daemonize: if True fork the processes into
      a daemon.
    :return:
    """
    if daemonize:
        detach(pidfile=pidfile)
    elif pidfile:
        with open(pidfile, "w+") as pidf:
            pidf.write("%s\n" % os.getpid())
    try:
        server.serve_forever()
    finally:
        try:
            os.remove(pidfile)
        except OSError:
            pass


def send_action(action, pidfile):
    """Send a signal to an existing running daemon."""
    if not os.path.exists(pidfile):
        print("No pid file available: %s", pidfile, file=sys.stderr)
        return
    with open(pidfile) as pidf:
        pid = int(pidf.read())

    if action == "reload":
        os.kill(pid, signal.SIGUSR1)
    elif action == "stop":
        os.kill(pid, signal.SIGTERM)
