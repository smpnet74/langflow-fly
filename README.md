# Langflow on Fly.io

This project deploys Langflow 1.1.1 to Fly.io with persistent storage using a Fly volume.

## Setup Fly CLI

1. First install the Fly CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Configure Fly CLI for this session:
   ```bash
   source setup.sh
   ```

This will make the `fly` command available in your current terminal session.

## Prerequisites

1. Create a Fly.io account at https://fly.io/signup
2. Login to Fly:
   ```bash
   fly auth login
   ```

## Deployment Steps

1. Create a new Fly app:
   ```bash
   fly apps create
   ```

2. Deploy the application:
   ```bash
   fly deploy
   ```

The volume will be automatically created and configured during the first deployment.

## Configuration

### Inactivity Timeout
The application automatically shuts down after a period of inactivity to save resources. The timeout is configured in fly.toml:

```toml
[env]
  TIMEOUT_MINUTES = '5'
```

Default timeout is 5 minutes if not specified.

### Proxy Server
The application includes a custom proxy server that:
- Handles all incoming requests on port 8080
- Forwards requests to the Langflow instance running on port 8000
- Implements health check endpoints at `/health` and `/healthcheck`
- Tracks activity for auto-scaling purposes (excluding health checks)
- Provides detailed request logging

### Autoscaling
The application automatically scales based on the configuration in fly.toml:
- Scales to zero after inactivity timeout
- Automatically starts when traffic is received
- Uses 2GB memory with shared CPU (1 core)
- Maximum of 1 machine instance
- Implements force HTTPS for all traffic

## Notes

- The application uses a SQLite database stored on the Fly volume at `/data/langflow.db`
- The volume is automatically configured with:
  - Initial size: 1GB
  - Auto-extends when usage reaches 80% capacity
  - Extends in 500MB increments
  - Maximum size limit: 2GB
  - Minimum size: 1GB
- Resource configuration:
  - Memory: 2GB (upgraded from 1GB)
  - CPU: Shared, 1 core
  - Machines: 0-1 instances (automatically managed)
- Built using Python 3.12 with the latest Langflow image
- Includes automatic request monitoring and logging
- Implements graceful shutdown handling via SIGTERM

## Monitoring

You can monitor the application's scaling status using:
```bash
./check_scale.sh
```

This will show:
- Current number of running instances
- Instance details including ID and region
- Real-time scaling events

### Health Checks
The application implements two health check endpoints:
- `/health`
- `/healthcheck`

These endpoints are used by Fly.io to monitor the application's status and don't affect the inactivity timeout.
