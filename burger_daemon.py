import os, sys, time, atexit
from signal import SIGTERM

class BurgerDaemon:
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.pidfile = pidfile
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def daemonize(self):
        self.create_child()
        self.decouple()

        # Do a second fork in order to avoid the daemon to reacquire
        # a controlling terminal.
        self.create_child()

        self.redirect_file_descriptors()
        self.create_pidfile()

    def create_child(self):
        try:
            pid = os.fork()

            if pid > 0:
                sys.exit(0)
        except OSError, err:
            sys.stderr.write("Fork failed: %d (%s)\n" % (err.errno, err.strerror))
            sys.exit(1)

    def decouple(self):
        os.chdir('/')
        os.setsid()
        os.umask(0)

    def redirect_file_descriptors(self):
        self.flush_file_descriptors()

        stdin_f = file(self.stdin, 'r')
        stdout_f = file(self.stdout, 'a+')
        stderr_f = file(self.stderr, 'a+', 0)

        os.dup2(stdin_f.fileno(), sys.stdin.fileno())
        os.dup2(stdout_f.fileno(), sys.stdout.fileno())
        os.dup2(stderr_f.fileno(), sys.stderr.fileno())

    def flush_file_descriptors(self):
        sys.stdout.flush()
        sys.stderr.flush()

    def create_pidfile(self):
        atexit.register(self.delete_pidfile)
        file(self.pidfile, 'w+').write("%s\n" % str(os.getpid()))

    def delete_pidfile(self):
        os.remove(self.pidfile)

    def start(self):
        if self.retrieve_pid():
            sys.stderr.write('Daemon is already running.')
            sys.exit(1)

        self.daemonize()
        self.run()

    def stop(self):
        pid = self.retrieve_pid()

        if not pid:
            sys.stderr.write('Daemon is not running.')
            return

        self.kill_process(pid)

    def restart(self):
        self.stop()
        self.start()

    def retrieve_pid(self):
        try:
            pfile = file(self.pidfile, 'r')
            pid = int(pfile.read().strip())
            pfile.close()
        except IOError:
            pid = None

        return pid

    def kill_process(self, pid):
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)

            if err.find('No such process') > 0:
                self.delete_pidfile()
            else:
                print str(err)
                sys.exit(1)

    def run(self):
        """
        Override this method when subclassing the BurgerDaemon.
        It's called during a start() and a restart().
        """
