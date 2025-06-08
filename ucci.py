import subprocess
import threading

class UCCIEngine:
    def __init__(self, engine_path):
        self.engine = subprocess.Popen(
            [engine_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        self.lock = threading.Lock()
        self._init_engine()

    def _init_engine(self):
        self._send("ucci")
        while True:
            line = self._read()
            if "ucciok" in line:
                break
        # self._send("setoption name EvalFile value G:/git/Pikafish/pica/pikafish.nnue")

    def _send(self, command):
        with self.lock:
            self.engine.stdin.write(command + "\n")
            self.engine.stdin.flush()

    def _read(self):
        return self.engine.stdout.readline().strip()

    def is_ready(self):
        self._send("isready")
        while True:
            line = self._read()
            if "readyok" in line:
                return True

    def set_position(self, fen):
        self._send(f"position fen {fen}")

    def go(self, time_limit_ms=3000):
        self._send(f"go time {time_limit_ms}")
        while True:
            line = self._read()
            if line.startswith("bestmove"):
                return line.split()[1]

    def quit(self):
        self._send("quit")
        self.engine.terminate()
