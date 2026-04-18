from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from src.models import Regulation, UserPreference
from src.utils.errors import NotFoundException

class RegulationService:
    """Business logic for accessing and filtering regulations."""

    @staticmethod
    def get_filtered_regulations(
        db: Session,
        limit: int = 20,
        offset: int = 0,
        domains: Optional[List[str]] = None,
        source: Optional[str] = None,
        impact: Optional[str] = None,
        query: Optional[str] = None
    ):
        """Fetch regulations with advanced filtering and search."""
        import re
        db_query = db.query(Regulation).order_by(desc(Regulation.created_at))

        if source:
            # Validate source - must be alphanumeric
            valid_sources = ["SEBI", "RBI", "MCA", "MEITY", "DPIIT"]
            if source not in valid_sources:
                from src.utils.errors import ValidationException
                raise ValidationException(f"Invalid source: {source}", "source", source)
            db_query = db_query.filter(Regulation.source_body == source)

        if impact:
            # Validate impact - must be one of the allowed values
            valid_impacts = ["HIGH", "MEDIUM", "LOW"]
            if impact not in valid_impacts:
                from src.utils.errors import ValidationException
                raise ValidationException(f"Invalid impact: {impact}", "impact", impact)
            db_query = db_query.filter(Regulation.ai_impact_level == impact)

        if domains:
            # Validate domains - alphanumeric with underscores only
            valid_domain_pattern = re.compile(r"^[a-z_]+$", re.IGNORECASE)
            for domain in domains:
                if not valid_domain_pattern.match(domain):
                    from src.utils.errors import ValidationException
                    raise ValidationException(
                        f"Invalid domain format: {domain}",
                        "domains",
                        str(domains)
                    )
                # Use parameterized query
                db_query = db_query.filter(Regulation.domains.contains(f'"{domain}"'))

        if query:
            # Sanitize query string - remove special SQL characters
            sanitized_query = re.sub(r"[%;'\"\\]", "", query)[:255]  # Limit length
            # Simple keyword search across title and content with parameterized queries
            search_term = f"%{sanitized_query}%"
            db_query = db_query.filter(
                (Regulation.original_title.ilike(search_term)) |
                (Regulation.full_text.ilike(search_term)) |
                (Regulation.ai_tldr.ilike(search_term))
            )

        total = db_query.count()
        results = db_query.offset(offset).limit(limit).all()

        return results, total

    @staticmethod
    def get_time_series_stats(db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """Generate daily counts of regulations for the last N days."""
        start_date = datetime.utcnow() - timedelta(days=days)

        # Group by date
        stats = db.query(
            func.date(Regulation.created_at).label("date"),
            func.count(Regulation.id).label("count")
        ).filter(Regulation.created_at >= start_date)\
         .group_by("date")\
         .order_by("date").all()

        # Fill in gaps for missing dates
        result = []
        current_date = start_date.date()
        stats_map = {row[0]: row[1] for row in stats}

        while current_date <= datetime.utcnow().date():
            result.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "count": stats_map.get(current_date, 0)
            })
            current_date += timedelta(days=1)

        return result

class SessionService:
    """Business logic for managing user sessions and preferences."""

    @staticmethod
    def get_session_preferences(db: Session, session_id: str):
        pref = db.query(UserPreference).filter(UserPreference.session_id == session_id).first()
        if not pref:
            raise NotFoundException("Session", session_id)
        return pref

    @staticmethod
    def get_personalized_feed(db: Session, session_id: str, limit: int = 20, offset: int = 0):
        """Get regulations filtered by a user's saved domain preferences."""
        pref = SessionService.get_session_preferences(db, session_id)
        import json
        domains = json.loads(pref.selected_domains) if pref.selected_domains else []

        return RegulationService.get_filtered_regulations(
            db, limit=limit, offset=offset, domains=domains
        )
