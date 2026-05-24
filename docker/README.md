# Docker Configuration

## Cross-Platform Setup (Windows & macOS)

### Prerequisites

Install **Docker Desktop** from https://www.docker.com/products/docker-desktop/

### Starting Services

```bash
# From project root
docker compose up -d
```

### Services

| Service  | Port  | Purpose                          |
| -------- | ----- | -------------------------------- |
| ChromaDB | 8000  | Semantic memory for crash cases  |

### Data Persistence

- ChromaDB data: `./data/chroma/` (mounted volume)
- SQLite data: `./data/` (shared volume mount)

### Stopping Services

```bash
docker compose down
```

### Platform Notes

- **Windows**: Docker Desktop uses WSL2 backend. Ensure WSL2 is installed and enabled.
- **macOS**: Docker Desktop runs natively via virtualization framework. Colima and OrbStack are also compatible alternatives.

### Troubleshooting

- **Port 8000 already in use**: Change the host port mapping in `docker-compose.yml`
- **Permission denied on data directory**: Run `mkdir -p data/chroma` before starting
- **Docker Desktop not running**: Start Docker Desktop and wait for the engine to be ready
