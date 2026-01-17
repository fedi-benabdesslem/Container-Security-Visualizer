# 🛡️ Container Security Visualizer

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%7C%20Vite-61DAFB.svg?style=flat-square&logo=react&logoColor=black)](https://reactjs.org/)
[![eBPF](https://img.shields.io/badge/Observability-eBPF-FF5722.svg?style=flat-square&logo=linux&logoColor=white)](https://ebpf.io/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

**A production-grade, real-time security monitoring platform for Docker containers powered by eBPF.**

[Key Capabilities](#-key-capabilities) • [Architecture](#-technical-architecture) • [Getting Started](#-getting-started) • [Development](#-development-setup)

</div>

---

## 📖 Overview

The **Container Security Visualizer** provides deep visibility into the runtime behavior of your containerized infrastructure. By leveraging **eBPF (Extended Berkeley Packet Filter)**, it captures low-level system events directly from the Linux kernel. This approach offers unparalleled observability without the performance overhead or security risks associated with traditional sidecar proxies or invasive agents.

This platform bridges the gap between deep system-level events and actionable security insights, visualizing complex interactions in a modern, interactive dashboard.

## ✨ Key Capabilities

| Feature | Description |
| :--- | :--- |
| **🔍 System Call Monitoring** | Real-time capturing of `execve` system calls to track every process execution within your containers. |
| **🌐 Network Observability** | Visualizes TCP connection attempts to map container-to-container and container-to-external communication edges. |
| **🧠 Automated Enrichment** | Dynamically correlates kernel-level PIDs with high-level Docker metadata (Name, Image, Status). |
| **🛡️ Security Analytics** | Instant risk scoring and event categorization based on process intent and network destinations. |
| **📊 Live Visualization** | A premium, responsive React-based dashboard displaying live event streams and dynamic connection graphs via WebSockets. |

---

## 🏗️ Technical Architecture

The system is composed of four decoupled microservices:

- **🔌 Collector (eBPF + BCC)**: A high-performance, privileged agent that attaches probes to the kernel to ingest security events (Executions, Network connections).
- **⚙️ Backend (FastAPI)**: The central control plane that ingests enriched events, manages PostgreSQL storage, and broadcasts data to the frontend via WebSockets.
- **🎨 Frontend (React + Vite)**: A modern, aesthetically pleasing single-page application (SPA) for monitoring specific containers and exploring the network graph.
- **💾 Database (PostgreSQL)**: Persistent storage for historical event data and container metadata.

---

## 🚀 Getting Started

The quickest way to run the full stack is via Docker Compose.

### Prerequisites
- **Linux Environment** (Required for eBPF features; Kernel 5.4+ recommended).
- **Docker & Docker Compose**.
- **Root/Sudo Privileges** (To allow the collector to Attach kprobes).

### Quick Launch

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/fedi-benabdesslem/Container-Security-Visualizer.git
    cd Container-Security-Visualizer
    ```

2.  **Configure Environment**
    ```bash
    cp .env.example .env
    # Edit .env and set your DB_PASSWORD and specific CORS_ORIGINS if deploying to production.
    ```

3.  **Initialize Database**
    ```bash
    docker compose run --rm backend python3 -m alembic upgrade head
    ```

4.  **Start Services**
    ```bash
    docker compose up -d
    ```

5.  **Access Dashboard**
    Naviage to **[http://localhost:8080](http://localhost:8080)** in your browser.

    > **View Logs**: `docker compose logs -f backend` or `docker compose logs -f collector`

---

## 🛠️ Development Setup

If you want to contribute or modify the code, you can run each component individually.

### 1. Database Setup
Start a PostgreSQL instance. The easiest way is to use the docker-compose service:
```bash
docker compose up -d db
```
*Ensure the `DATABASE_URL` in your `.env` points to this instance (default: `localhost:5432`).*

### 2. Backend (FastAPI)
The backend requires Python 3.10+.

```bash
# Navigate to the root folder
cd Container-Security-Visualizer

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r backend/requirements.txt

# Run database migrations
python -m alembic upgrade head

# Start the server (Development Mode with Reload)
python -m backend.main
# OR
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
*API Documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).*

### 3. Frontend (React + Vite)
The frontend requires Node.js 18+.

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
*The UI will be running at [http://localhost:5173](http://localhost:5173).*

### 4. Collector (eBPF)
**Note**: This component **must** run on a Linux machine with `bcc` tools installed. Windows/Mac users should use a VM or the Docker Setup.

```bash
# Install BCC tools (Ubuntu example)
sudo apt-get install bpfcc-tools linux-headers-$(uname -r)

# Run the collector (requires root)
sudo python3 collector/collector.py
```

---

## 📂 Project Structure

```text
Container-Security-Visualizer/
├── backend/            # Python FastAPI application
│   ├── api/            # API Routes (events, stats, websockets)
│   ├── models/         # SQLAlchemy Database Models
│   └── services/       # Business Logic & Event Processing
├── collector/          # Python eBPF Consumer
│   └── ebpf/           # C source code for BPF programs
├── frontend/           # React Application
│   ├── src/
│   │   ├── components/ # Reusable UI Components
│   │   └── pages/      # Main Dashboard Views
├── utilities/          # Shared Helpers
└── docker-compose.yml  # Production Orchestration
```

## 🔒 Security & Privileges
The `collector` service requires `privileged: true` in Docker or `sudo` on bare metal. This is necessary to attach eBPF probes to the host kernel's syscalls. It is recommended to deploy this on a secure monitoring node with restricted access.

## 📄 License
This project is licensed under the [MIT License](LICENSE).
