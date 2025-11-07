# Monitoring Stack Documentation

This document describes the Prometheus and Grafana monitoring implementation for the sogangcomputerclub.org project.

## Overview

The monitoring stack consists of:
- **Prometheus**: Metrics collection and storage
- **Grafana**: Metrics visualization and dashboards
- **FastAPI Instrumentation**: Application metrics exposure

## Architecture

```
FastAPI App (/metrics) -> Prometheus (scrapes) -> Grafana (queries) -> User Dashboard
```

## Services and Ports

| Service    | Port (Host) | Port (Container) | Purpose                     |
|------------|-------------|------------------|----------------------------|
| Prometheus | 9090        | 9090             | Metrics collection & queries|
| Grafana    | 3001        | 3000             | Dashboard & visualization   |
| FastAPI    | 8000        | 8000             | Application & metrics       |
| MariaDB    | 3307        | 3306             | Database                    |
| Redis      | 6381        | 6379             | Cache                       |

**Note**: MariaDB and Redis ports were changed from 3306 and 6380 respectively to avoid conflicts with host services.

## Accessing the Monitoring Stack

### Prometheus
- URL: http://localhost:9090
- Use the "Targets" page to verify scraping status
- Query examples:
  - `fastapi_requests_total` - Total request count
  - `rate(fastapi_requests_total[5m])` - Request rate per second
  - `histogram_quantile(0.95, rate(fastapi_request_duration_seconds_bucket[5m]))` - 95th percentile latency

### Grafana
- URL: http://localhost:3001
- Default credentials: `admin` / `admin`
- Pre-configured datasource: Prometheus
- Pre-configured dashboard: "FastAPI Application Metrics"

To change Grafana credentials, set environment variables:
```bash
GRAFANA_ADMIN_USER=your_username
GRAFANA_ADMIN_PASSWORD=your_secure_password
```

## Available Metrics

### Application Metrics
- `fastapi_requests_total` - Counter of total requests (labels: method, endpoint, status_code)
- `fastapi_request_duration_seconds` - Histogram of request durations (labels: method, endpoint)
- `memo_total` - Gauge of total memos in database
- `fastapi_active_connections` - Gauge of active database connections

### Python Runtime Metrics
- `python_gc_*` - Garbage collection statistics
- `process_*` - Process memory, CPU usage

## Dashboard Panels

The pre-configured FastAPI dashboard includes:
1. **Request Rate** - Requests per second over time
2. **Request Duration** - p95 and p50 latency percentiles
3. **Total Requests per Second** - Current RPS gauge
4. **Response Status Codes** - Distribution pie chart
5. **Requests by Endpoint** - Traffic breakdown by API endpoint

## Configuration Files

### Prometheus Configuration
- File: `prometheus.yml`
- Scrape interval: 15s (5s for FastAPI)
- Targets:
  - prometheus (self-monitoring)
  - fastapi:8000/metrics

### Grafana Provisioning
- Datasources: `grafana/provisioning/datasources/prometheus.yml`
- Dashboards: `grafana/provisioning/dashboards/default.yml`
- Dashboard JSON: `grafana/provisioning/dashboards/fastapi-dashboard.json`

## Docker Compose Configuration

Services are defined in both `docker-compose.yml` (development) and `docker-compose.prod.yml` (production).

### Development
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### FastAPI metrics not showing up
1. Check FastAPI is running: `docker-compose ps`
2. Verify metrics endpoint: `curl http://localhost:8000/metrics`
3. Check Prometheus targets: http://localhost:9090/targets

### Grafana dashboard is empty
1. Verify Prometheus datasource is connected (Configuration -> Data Sources)
2. Check if Prometheus has data: http://localhost:9090/graph
3. Verify dashboard queries are correct

### Port conflicts
If you get port binding errors:
1. Check what's using the port: `sudo ss -tlnp | grep <port>`
2. Stop the conflicting service or change the port in docker-compose.yml

## Adding More Metrics

To add custom metrics to FastAPI:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metric
MY_METRIC = Counter('my_metric_total', 'Description', ['label1', 'label2'])

# Use in code
MY_METRIC.labels(label1='value1', label2='value2').inc()
```

Metrics are automatically exported at the `/metrics` endpoint.

## Health Checks

- **FastAPI**: http://localhost:8000/health
- **Prometheus**: http://localhost:9090/-/healthy
- **Grafana**: http://localhost:3001/api/health

## Data Persistence

Both Prometheus and Grafana use Docker volumes for persistence:
- `prometheus_data` - Stores time-series metrics data
- `grafana_data` - Stores dashboards, users, and settings

To backup:
```bash
docker run --rm -v sogangcomputercluborg_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz /data
docker run --rm -v sogangcomputercluborg_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz /data
```

## Future Enhancements

Optional exporters that can be added:
- **Redis Exporter**: Monitor Redis cache metrics
- **MySQL Exporter**: Monitor MariaDB database metrics
- **Nginx Exporter**: Monitor nginx web server metrics
- **Node Exporter**: Monitor host system metrics

These are pre-configured in prometheus.yml but not yet deployed.
