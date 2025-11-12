import socket
import threading
import os
import httpx
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:8000')
HOST = '0.0.0.0'
PORT = 110

class POP3Session(threading.Thread):
    def __init__(self, conn, addr):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.user = None
        self.token = None
        self.messages = []  # cached messages list from backend
        self.marked_deleted = set()
        self.client = httpx.Client(timeout=10.0)

    def send(self, line: str):
        self.conn.sendall((line + "\r\n").encode())

    def readline(self):
        data = b''
        while True:
            ch = self.conn.recv(1)
            if not ch:
                return None
            data += ch
            if data.endswith(b"\r\n"):
                return data[:-2].decode()

    def run(self):
        try:
            self.send('+OK POP3 server ready')
            while True:
                line = self.readline()
                if line is None:
                    break
                parts = line.split()
                if not parts:
                    continue
                cmd = parts[0].upper()
                args = parts[1:] if len(parts) > 1 else []

                if cmd == 'USER':
                    self.user = args[0] if args else None
                    self.send('+OK user accepted')
                elif cmd == 'PASS':
                    password = args[0] if args else ''
                    # call backend login
                    try:
                        r = self.client.post(f"{BACKEND_URL}/auth/login", json={"email": self.user, "password": password})
                        if r.status_code == 200:
                            token = r.json().get('access_token')
                            self.token = token
                            self.send('+OK logged in')
                            # fetch inbox
                            hdr = {"Authorization": f"Bearer {self.token}"}
                            r2 = self.client.get(f"{BACKEND_URL}/mail/inbox?limit=100", headers=hdr)
                            if r2.status_code == 200:
                                self.messages = r2.json()
                            else:
                                self.messages = []
                        else:
                            self.send('-ERR invalid login')
                    except Exception as e:
                        self.send('-ERR backend error')
                elif cmd == 'STAT':
                    # count messages not deleted
                    msgs = [m for i,m in enumerate(self.messages) if i+1 not in self.marked_deleted]
                    count = len(msgs)
                    size = sum(len(m.get('body','')) for m in msgs)
                    self.send(f'+OK {count} {size}')
                elif cmd == 'LIST':
                    if len(args) == 1:
                        idx = int(args[0])
                        if idx <= 0 or idx > len(self.messages):
                            self.send('-ERR no such message')
                        elif idx in self.marked_deleted:
                            self.send('-ERR message deleted')
                        else:
                            size = len(self.messages[idx-1].get('body',''))
                            self.send(f'+OK {idx} {size}')
                    else:
                        self.send('+OK list follows')
                        for i,m in enumerate(self.messages):
                            if i+1 in self.marked_deleted:
                                continue
                            self.send(f"{i+1} {len(m.get('body',''))}")
                        self.send('.')
                elif cmd == 'RETR':
                    idx = int(args[0])
                    if idx <= 0 or idx > len(self.messages) or idx in self.marked_deleted:
                        self.send('-ERR no such message')
                    else:
                        m = self.messages[idx-1]
                        self.send('+OK message follows')
                        self.send(m.get('body',''))
                        self.send('.')
                elif cmd == 'DELE':
                    idx = int(args[0])
                    if idx <= 0 or idx > len(self.messages):
                        self.send('-ERR no such message')
                    else:
                        self.marked_deleted.add(idx)
                        self.send('+OK marked for deletion')
                elif cmd == 'QUIT':
                    # delete marked messages via backend
                    if self.token and self.marked_deleted:
                        hdr = {"Authorization": f"Bearer {self.token}"}
                        for idx in sorted(self.marked_deleted, reverse=True):
                            msg = self.messages[idx-1]
                            # attempt to delete by id
                            mid = msg.get('id')
                            if mid:
                                try:
                                    self.client.delete(f"{BACKEND_URL}/mail/delete/{mid}", headers=hdr)
                                except Exception:
                                    pass
                    self.send('+OK goodbye')
                    break
                else:
                    self.send('-ERR unsupported')
        finally:
            self.conn.close()

def serve():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f'POP3 server listening on {HOST}:{PORT}')
    try:
        while True:
            conn, addr = s.accept()
            t = POP3Session(conn, addr)
            t.daemon = True
            t.start()
    finally:
        s.close()

if __name__ == '__main__':
    serve()
