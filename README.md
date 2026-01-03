# Container Security Visualizer


## What is it actually?

The **Container Security Visualizer** is a production-grade security monitoring platform designed to provide visibility into the runtime behavior of Docker containers. It leverages the power of **eBPF (Extended Berkeley Packet Filter)** to capture low-level system events directly from the Linux kernel without the overhead or security risks of traditional monitoring agents.

### Key Capabilities:
- **System Call Monitoring**: Captures `execve` system calls to track process executions within containers.
- **Network Observability**: Monitors TCP connection attempts to visualize container-to-container and container-to-external communication edges.
- **Automated Enrichment**: Dynamically maps kernel-level PIDs to Docker container metadata (Name, Image, Status).
- **Security Analytics**: Real-time risk scoring and categorization of events based on process intent and network destinations.
- **Live Visual Dashboard**: A modern, interactive dashboard that displays live event streams and dynamic connection graphs via WebSockets.

---

## Technical Architecture

- **Backend (FastAPI)**: Ingests events, manages long-term storage in PostgreSQL, and serves the frontend via REST and WebSockets.
- **Collector (eBPF + BCC)**: A privileged agent that loads eBPF programs into the kernel to capture security events.
- **Frontend (React + Vite)**: A premium, responsive UI for real-time visualization of your container security posture.
- **Database (PostgreSQL)**: Reliable storage for historical security events and container metadata.

---

## How to Download and Setup

### Prerequisites
- **Linux** (eBPF features require a Linux kernel 5.4+).
- **Docker & Docker Compose** installed.
- **Root/Sudo access** (to attach eBPF probes).

### Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/fedi-benabdesslem/Container-Security-Visualizer.git
   cd Container-Security-Visualizer
   ```

2. **Prepare Environment Variables**:
   ```bash
   cp .env.example .env
   ```
   *Note: Open `.env` and configure your `DB_PASSWORD` and `CORS_ORIGINS` for production use.*

3. **Initialize the Database**:
   Run the following command to set up the database schema:
   ```bash
   docker compose run --rm backend python3 -m alembic upgrade head
   ```

4. **Launch the Application**:
   Start all services in the background:
   ```bash
   docker compose up -d
   ```

---

## How to Run & Use it

### Accessing the Dashboard
Open your web browser and navigate to:
**[http://localhost:8080](http://localhost:8080)**

### Monitoring the logs
To view live logs from any component:
```bash
docker compose logs -f backend   # For API logs
docker compose logs -f collector # For eBPF event logs
```

### Stopping the Application
To shut down all services and keep the data:
```bash
docker compose down
```

---

## Project Structure
```text
├── backend/          # API & Database Logic
├── collector/        # eBPF Data Ingestion Agent
├── config/           # YAML Configuration Templates
├── ebpf/             # C Programs & Python Loaders
├── frontend/         # React Visualization Dashboard
├── utilities/        # Shared Docker & Security Utils
└── docker-compose.yml # Orchestration Definition
```

## Security & Privileges
The `collector` service requires `--privileged` mode to attach eBPF probes to the host kernel. It is recommended to run this on a dedicated monitoring host or with strict access controls.
