import os
import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import AsyncMessage
from email.message import EmailMessage
from datetime import datetime
from pathlib import Path
import httpx
from dotenv import load_dotenv

load_dotenv()
MAILDIR = os.getenv('MAILDIR', '/var/mail')
BACKEND_URL = os.getenv('BACKEND_URL')  # optional: http://backend:8000/mail/compose

Path(MAILDIR).mkdir(parents=True, exist_ok=True)

class MaildirHandler(AsyncMessage):
    async def handle_message(self, message: EmailMessage):
        recipients = message.get_all('To', []) or message.get_all('Delivered-To', []) or []
        sender = message.get('From', 'unknown')
        subject = message.get('Subject', '')
        payload = message.get_payload(decode=True)
        body = ''
        if payload:
            try:
                body = payload.decode('utf-8', errors='ignore')
            except Exception:
                body = str(payload)
        ts = datetime.utcnow().isoformat()

        for r in recipients:
            # sanitize recipient local part
            local = r.split('@')[0].strip().replace('"','').replace('<','').replace('>','')
            user_dir = Path(MAILDIR) / local
            user_dir.mkdir(parents=True, exist_ok=True)
            filename = user_dir / f"msg-{int(datetime.utcnow().timestamp())}-{os.getpid()}.eml"
            with open(filename, 'w', encoding='utf-8') as fh:
                fh.write(f"From: {sender}\nTo: {r}\nSubject: {subject}\n\n{body}")

        # optionally notify backend via HTTP
        if BACKEND_URL:
            async with httpx.AsyncClient() as client:
                for r in recipients:
                    try:
                        data = {
                            "subject": subject,
                            "body": body,
                            "recipient": r,
                        }
                        await client.post(BACKEND_URL, json=data, timeout=10.0)
                    except Exception as e:
                        print("Failed to notify backend:", e)

async def run():
    handler = MaildirHandler()
    controller = Controller(handler, hostname='0.0.0.0', port=25)
    controller.start()
    print('SMTP server started on port 25')
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        controller.stop()

if __name__ == '__main__':
    asyncio.run(run())
