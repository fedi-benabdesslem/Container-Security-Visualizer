# Container Security Visualizer

A real-time interactive dashboard for visualizing container security events, network communications, and system activity using eBPF data streams.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **TypeScript** | Type safety |
| **Cytoscape.js** | Graph visualization (containers as nodes, interactions as edges) |
| **WebSocket** | Real-time event streaming from backend |
| **Axios** | REST API calls for historical data |
| **TailwindCSS** | Styling and theming |
| **shadcn/ui** | UI component library |
| **Vite** | Build tool and dev server |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
├─────────────┬─────────────┬─────────────┬─────────────┬────────┤
│  GraphView  │  Timeline   │   Alerts    │   Filters   │ History│
│ (Cytoscape) │  (Events)   │  (Panel)    │  (Panel)    │ (REST) │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴───┬────┘
       │             │             │             │          │
       └─────────────┴──────┬──────┴─────────────┘          │
                            │                               │
              ┌─────────────▼─────────────┐    ┌───────────▼──────────┐
              │   WebSocket Connection    │    │     REST API         │
              │  ws://localhost:8000/ws   │    │ http://localhost:8000│
              └───────────────────────────┘    └──────────────────────┘
```

## Backend Connection

### Health Check

**Endpoint:** `GET http://localhost:8000/health`

Polled every 5 seconds to determine connection status (Connected/Disconnected indicator).

```json
{
  "status": "healthy",
  "database": "healthy",
  "version": "0.1.0"
}
```

### WebSocket - Real-Time Events

**Endpoint:** `ws://localhost:8000/ws/events`

Supports query parameters for server-side filtering:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `monitor_type` | Filter by event type | `syscall`, `network` |
| `min_risk_score` | Minimum risk score (0-10) | `7` |
| `suspicious_only` | Only security-relevant events | `true` |

**Examples:**
```
ws://localhost:8000/ws/events                          # All events
ws://localhost:8000/ws/events?monitor_type=syscall     # Syscall only
ws://localhost:8000/ws/events?monitor_type=network     # Network only
ws://localhost:8000/ws/events?suspicious_only=true     # Suspicious only
ws://localhost:8000/ws/events?min_risk_score=7         # High risk only
```

**Connection Message:**
```json
{
  "type": "connected",
  "message": "Connected to event stream",
  "filters": { "monitor_type": "syscall" },
  "active_connections": 1
}
```

**Event Payload:**
```json
{
  "id": 123,
  "timestamp_iso": "2025-12-16T17:00:00Z",
  "timestamp_ns": 1734378000000000000,
  "monitor_type": "syscall",
  "pid": 1234,
  "uid": 1000,
  "comm": "bash",
  "container_id": "abc123456789",
  "container_name": "web_app",
  "container_image": "nginx:latest",
  "container_status": "running",
  "argv": "/bin/bash -c id",
  "event_type": "tcp_connect",
  "source_ip": "172.17.0.2",
  "dest_ip": "142.250.74.100",
  "source_port": 45732,
  "dest_port": 443,
  "risk_score": 7,
  "categories": ["process", "privilege"],
  "is_security_relevant": true
}
```

### REST API Endpoints

#### Historical Events
```
GET /api/events
```
| Parameter | Type | Description |
|-----------|------|-------------|
| `start_time` | number | Start timestamp (nanoseconds) |
| `end_time` | number | End timestamp (nanoseconds) |
| `monitor_type` | string | `syscall` or `network` |
| `container_id` | string | Filter by container ID |
| `container_name` | string | Filter by container name |
| `min_risk_score` | number | Minimum risk score (0-10) |
| `search` | string | Search in comm, container_name, argv |
| `limit` | number | Results per page (default: 50, max: 1000) |
| `offset` | number | Pagination offset (default: 0) |

**Response:**
```json
{
  "events": [...],
  "total": 1543,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

#### Security Alerts
```
GET /api/alerts?limit=50
```
**Response:**
```json
[
  {
    "id": 789,
    "timestamp_iso": "2025-12-16T16:55:23Z",
    "container_name": "db_server",
    "comm": "psql",
    "risk_score": 9,
    "categories": ["privilege", "process"],
    "description": "psql (PID: 1234) in container db_server: SELECT * FROM users"
  }
]
```

#### Summary Statistics
```
GET /api/stats/summary
```
**Response:**
```json
{
  "total_events": 12034,
  "total_containers": 6,
  "syscall_events": 8000,
  "network_events": 4034,
  "high_risk_events": 42,
  "timespan_start": "2025-12-16T12:00:00Z",
  "timespan_end": "2025-12-16T17:00:00Z"
}
```

#### Timeline Data
```
GET /api/stats/timeline?interval=1m
```
| Parameter | Options |
|-----------|---------|
| `interval` | `1m`, `5m`, `15m`, `1h`, `6h`, `1d` |

**Response:**
```json
{
  "interval": "1m",
  "data": [
    { "timestamp": "2025-12-16T16:50:00Z", "count": 23, "syscall_count": 15, "network_count": 8 },
    { "timestamp": "2025-12-16T16:51:00Z", "count": 31, "syscall_count": 20, "network_count": 11 }
  ]
}
```

#### Containers
```
GET /api/containers
```
**Response:**
```json
[
  {
    "container_id": "abc123456789",
    "container_name": "web_app",
    "container_image": "nginx:latest",
    "event_count": 2345,
    "first_seen": "2025-12-16T12:00:00Z",
    "last_seen": "2025-12-16T17:00:00Z",
    "risk_level": "medium"
  }
]
```

#### Container Events
```
GET /api/containers/{container_id}/events?limit=100
```

## Filter Mappings

| UI Toggle | WebSocket Parameter |
|-----------|---------------------|
| Network Events | `monitor_type=network` |
| Syscall Events | `monitor_type=syscall` |
| Highlight Suspicious | `suspicious_only=true` |

## Risk Levels

| Level | Color | Description |
|-------|-------|-------------|
| `low` / `safe` | Green | Normal activity |
| `medium` / `warning` | Yellow | Elevated activity, needs attention |
| `high` / `critical` | Red | Suspicious/malicious activity detected |

## Global API (Window Methods)

The frontend exposes methods for programmatic control:

```javascript
// Graph View
window.graphView.addNode({ id, name, image, status, riskLevel })
window.graphView.addEdge({ id, source, target, type, weight })
window.graphView.removeNode(nodeId)
window.graphView.clearGraph()
window.graphView.highlightNode(nodeId)

// Event Timeline
window.eventTimeline.addEvent({ id, timestamp, type, containerId, containerName, data, severity })
window.eventTimeline.clearEvents()

// Alerts Panel
window.alertsPanel.pushAlert({ id, timestamp, title, description, severity, containerName })
window.alertsPanel.clearAlerts()
```

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Configuration

Update backend URLs in:
- `src/hooks/useWebSocket.ts` - WebSocket URL builder
- `src/hooks/useHealthCheck.ts` - Health endpoint
- `src/lib/api.ts` - REST API base URL

## License

MIT
