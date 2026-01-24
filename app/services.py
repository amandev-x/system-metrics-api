import psutil 
import socket 
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import SystemMetric

class MetricsCollector:
    def __init__(self):
        self.net_io_start = psutil.net_io_counters()

    def collect_current_metrics(self):
        """ Collect System Metrics and return in Python Dict"""
        # CPU stats
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory Stats
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # Disk stats
        disk = psutil.disk_usage("/")
        disk_percent = disk.percent

        # Network stats (calculate difference from start)
        net_io_now = psutil.net_io_counters()
        network_sent_mb = (net_io_now.bytes_sent - self.net_io_start.bytes_sent) / (1024 * 1024)
        network_recv_mb = (net_io_now.bytes_recv - self.net_io_start.bytes_recv) / (1024 * 1024)

        # Get hostname (Userful for distributed system)
        hostname = socket.gethostname()

        return {
            "timestamp": datetime.now(timezone.utc),
            "cpu_percent": round(cpu_percent, 2),
            "memory_percent": round(memory_percent, 2),
            "disk_percent": round(disk_percent, 2),
            "network_sent_mb": round(network_sent_mb, 2),
            "network_recv_mb": round(network_recv_mb, 2),
            "hostname": hostname
        }
    
    def save_metrics(self, db: Session):
        metrics_data = self.collect_current_metrics()

        metric = SystemMetric(**metrics_data)

        db.add(metric)
        db.commit()
        db.refresh(metric)   # Get the ID that was generated auto

        return metric
    
metrics_collector = MetricsCollector()


