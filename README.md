# kders Mail — College Mail + AI Collaboration Scaffold

This repository contains a full-stack scaffold for an SMTP & POP3 mail system with a React frontend, FastAPI backend, and AI-powered RAG assistant for group chats and mail summarization.

Services:
- frontend: React + Tailwind
- backend: FastAPI (async) + SQLAlchemy + PostgreSQL
- smtp_server: aiosmtpd-based receiver
- pop3_server: multithreaded POP3 server
- db: PostgreSQL
- nginx: reverse proxy (TLS / Let\'s Encrypt)

See `docker-compose.yml` for service wiring.

Quick start (development):
1. Copy `.env.example` to `.env` and edit values.
2. Start with Docker Compose:

   docker-compose up --build

3. Backend API: http://localhost:8000
4. Frontend: http://localhost:3000

Deployment notes:
- Target host: AWS EC2 (Ubuntu 22.04)
- Configure Cloudflare DNS for `kders.com` and mail subdomain records
- Set up SPF/DKIM/DMARC for sending mail
- Use Certbot to obtain TLS certificates and mount them into the nginx container

This scaffold provides minimal, documented implementations for each component. See each subdirectory for details.
