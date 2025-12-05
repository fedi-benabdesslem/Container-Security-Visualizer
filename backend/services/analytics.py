#!/usr/bin/env python3
# services/analytics.py - Analytics and aggregation logic

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from backend.models.event import Event
from backend.utils.logger import logger


class AnalyticsService:
    """Service for computing analytics and aggregations"""

    @staticmethod
    def get_event_distribution_by_type(
            db: Session,
            start_time: Optional[int] = None,
            end_time: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Get distribution of events by monitor type
        """
        query = db.query(
            Event.monitor_type,
            func.count(Event.id).label('count')
        )

        if start_time:
            query = query.filter(Event.timestamp_ns >= start_time)
        if end_time:
            query = query.filter(Event.timestamp_ns <= end_time)

        results = query.group_by(Event.monitor_type).all()

        return {row.monitor_type: row.count for row in results}

    @staticmethod
    def get_risk_distribution(db: Session) -> Dict[str, int]:
        """
        Get distribution of events by risk level
        """
        query = db.query(
            Event.risk_score,
            func.count(Event.id).label('count')
        ).filter(
            Event.risk_score.isnot(None)
        ).group_by(Event.risk_score).all()

        # Categorize into risk levels
        distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}

        for row in query:
            if row.risk_score >= 8:
                distribution["critical"] += row.count
            elif row.risk_score >= 6:
                distribution["high"] += row.count
            elif row.risk_score >= 4:
                distribution["medium"] += row.count
            else:
                distribution["low"] += row.count

        return distribution

    @staticmethod
    def get_top_containers_by_event_count(
            db: Session,
            limit: int = 10
    ) -> List[Tuple[str, str, int]]:
        """
        Get top containers by event count

        Returns: List of (container_id, container_name, event_count)
        """
        results = db.query(
            Event.container_id,
            Event.container_name,
            func.count(Event.id).label('event_count')
        ).filter(
            Event.container_id.isnot(None)
        ).group_by(
            Event.container_id,
            Event.container_name
        ).order_by(
            desc('event_count')
        ).limit(limit).all()

        return [(r.container_id, r.container_name or "unknown", r.event_count) for r in results]

    @staticmethod
    def get_top_processes_by_event_count(
            db: Session,
            limit: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Get top processes by event count

        Returns: List of (process_name, event_count)
        """
        results = db.query(
            Event.comm,
            func.count(Event.id).label('event_count')
        ).filter(
            Event.comm.isnot(None)
        ).group_by(
            Event.comm
        ).order_by(
            desc('event_count')
        ).limit(limit).all()

        return [(r.comm, r.event_count) for r in results]

    @staticmethod
    def get_events_per_hour(
            db: Session,
            hours: int = 24
    ) -> List[Tuple[datetime, int]]:
        """
        Get event count per hour for the last N hours

        Returns: List of (hour_timestamp, event_count)
        """
        # Calculate start time (N hours ago)
        now = datetime.utcnow()
        start_time = now - timedelta(hours=hours)

        results = db.query(
            func.date_trunc('hour', Event.timestamp_iso).label('hour'),
            func.count(Event.id).label('count')
        ).filter(
            Event.timestamp_iso >= start_time
        ).group_by('hour').order_by('hour').all()

        return [(r.hour, r.count) for r in results]

    @staticmethod
    def get_most_risky_containers(
            db: Session,
            limit: int = 10
    ) -> List[Dict]:
        """
        Get containers with highest average risk scores
        """
        results = db.query(
            Event.container_id,
            Event.container_name,
            Event.container_image,
            func.avg(Event.risk_score).label('avg_risk'),
            func.max(Event.risk_score).label('max_risk'),
            func.count(Event.id).label('event_count')
        ).filter(
            and_(
                Event.container_id.isnot(None),
                Event.risk_score.isnot(None)
            )
        ).group_by(
            Event.container_id,
            Event.container_name,
            Event.container_image
        ).order_by(
            desc('avg_risk')
        ).limit(limit).all()

        return [
            {
                "container_id": r.container_id,
                "container_name": r.container_name or "unknown",
                "container_image": r.container_image or "unknown",
                "avg_risk_score": round(r.avg_risk, 2),
                "max_risk_score": r.max_risk,
                "event_count": r.event_count
            }
            for r in results
        ]

    @staticmethod
    def get_network_connections_summary(db: Session) -> Dict:
        """
        Get summary of network connections
        """
        total_connections = db.query(Event).filter(
            Event.monitor_type == 'network'
        ).count()

        unique_dest_ips = db.query(
            func.count(func.distinct(Event.dest_ip))
        ).filter(
            and_(
                Event.monitor_type == 'network',
                Event.dest_ip.isnot(None)
            )
        ).scalar() or 0

        top_destinations = db.query(
            Event.dest_ip,
            func.count(Event.id).label('count')
        ).filter(
            and_(
                Event.monitor_type == 'network',
                Event.dest_ip.isnot(None)
            )
        ).group_by(Event.dest_ip).order_by(desc('count')).limit(10).all()

        return {
            "total_connections": total_connections,
            "unique_destinations": unique_dest_ips,
            "top_destinations": [
                {"ip": r.dest_ip, "count": r.count}
                for r in top_destinations
            ]
        }

    @staticmethod
    def detect_anomalies(db: Session) -> List[Dict]:
        """
        Simple anomaly detection - find unusual patterns

        Returns list of detected anomalies
        """
        anomalies = []

        # 1. Containers with sudden spike in events
        # Get average events per container
        avg_query = db.query(
            func.avg(func.count(Event.id))
        ).filter(
            Event.container_id.isnot(None)
        ).group_by(Event.container_id).scalar() or 0

        threshold = avg_query * 3  # 3x average is anomaly

        high_activity = db.query(
            Event.container_id,
            Event.container_name,
            func.count(Event.id).label('count')
        ).filter(
            Event.container_id.isnot(None)
        ).group_by(
            Event.container_id,
            Event.container_name
        ).having(
            func.count(Event.id) > threshold
        ).all()

        for r in high_activity:
            anomalies.append({
                "type": "high_activity",
                "container_id": r.container_id,
                "container_name": r.container_name,
                "event_count": r.count,
                "threshold": int(threshold),
                "severity": "medium"
            })

        # 2. Multiple high-risk events from same container
        high_risk_containers = db.query(
            Event.container_id,
            Event.container_name,
            func.count(Event.id).label('count')
        ).filter(
            and_(
                Event.risk_score >= 7,
                Event.container_id.isnot(None)
            )
        ).group_by(
            Event.container_id,
            Event.container_name
        ).having(
            func.count(Event.id) >= 5
        ).all()

        for r in high_risk_containers:
            anomalies.append({
                "type": "multiple_high_risk_events",
                "container_id": r.container_id,
                "container_name": r.container_name,
                "high_risk_count": r.count,
                "severity": "high"
            })

        logger.info(f"Detected {len(anomalies)} anomalies")

        return anomalies


# Global analytics service instance
analytics = AnalyticsService()