"""
API Routes

Defines all REST API endpoints for the RegRadar application.
Includes regulations, sessions, preferences, stats, and admin endpoints.
"""

import uuid
import json
from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from datetime import datetime
from src.database import get_db
from src.models import Regulation, UserPreference, ScraperRun
from src.api.schemas import (
    RegulationListResponse,
    RegulationResponse,
    DomainsResponse,
    DomainCount,
    StatsResponse,
    SessionRequest,
    SessionResponse,
    PreferenceUpdateRequest,
    PaginationParams,
)
from src.services.regulation_service import RegulationService, SessionService
from src.utils.logger import get_logger
from src.utils.errors import RegRadarException, ValidationException, DatabaseException, NotFoundException
from src.utils.validators import InputValidator

router = APIRouter()
logger = get_logger(__name__)


@router.get("/regulations", response_model=RegulationListResponse, tags=["Regulations"])
async def list_regulations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    domains: str = Query("", description="Comma-separated domain filters"),
    source: str = Query("", description="Filter by source body"),
    impact: str = Query("", description="Filter by impact level"),
    db: Session = Depends(get_db),
) -> RegulationListResponse:
    """
    Get list of regulations with filtering and pagination.

    Supports filtering by:
    - domains: Comma-separated list (e.g., 'banking,securities')
    - source: SEBI, RBI, MCA, MEITY, DPIIT
    - impact: HIGH, MEDIUM, LOW

    Args:
        limit: Number of records to return (1-100, default 20)
        offset: Number of records to skip (default 0)
        domains: Comma-separated domain filters
        source: Filter by regulatory source
        impact: Filter by impact level
        db: Database session

    Returns:
        List of regulations with pagination info

    Raises:
        ValidationException: If parameters invalid
    """
    try:
        # Validate pagination using InputValidator
        limit, offset = InputValidator.validate_pagination(limit, offset)

        # Build query
        query = db.query(Regulation).order_by(desc(Regulation.created_at))

        # Apply source filter with validation
        if source:
            source = InputValidator.validate_source(source)
            query = query.filter(Regulation.source_body == source)

        # Apply impact filter with validation
        if impact:
            impact = InputValidator.validate_impact(impact)
            query = query.filter(Regulation.ai_impact_level == impact)

        # Apply domain filters with validation
        if domains:
            domain_list = [d.strip() for d in domains.split(",") if d.strip()]
            domain_list = InputValidator.validate_domains(domain_list)
            for domain in domain_list:
                # Use parameterized query with contains
                query = query.filter(Regulation.domains.contains(f'"{domain}"'))

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        regulations = query.offset(offset).limit(limit).all()

        # Convert to response models (parse JSON fields)
        regulation_responses = []
        for r in regulations:
            reg_dict = {
                "id": r.id,
                "source_body": r.source_body,
                "original_title": r.original_title,
                "original_date": r.original_date,
                "source_url": r.source_url,
                "ai_title": r.ai_title,
                "ai_tldr": r.ai_tldr,
                "ai_what_changed": r.ai_what_changed,
                "ai_who_affected": r.ai_who_affected,
                "ai_action_required": r.ai_action_required,
                "ai_impact_level": r.ai_impact_level,
                "domains": json.loads(r.domains) if isinstance(r.domains, str) else r.domains,
                "processing_status": r.processing_status,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            regulation_responses.append(RegulationResponse(**reg_dict))

        page = (offset // limit) + 1
        has_more = (offset + limit) < total

        logger.info(
            "Listed regulations",
            extra={
                "total": total,
                "page": page,
                "limit": limit,
                "has_more": has_more,
            },
        )

        return RegulationListResponse(
            regulations=regulation_responses,
            total=total,
            page=page,
            page_size=limit,
            has_more=has_more,
        )

    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Error listing regulations: {str(e)}")
        raise DatabaseException(str(e), "list_regulations")


@router.get("/my-feed", response_model=RegulationListResponse, tags=["Regulations"])
async def get_my_feed(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session_id: str = Query(..., description="User session ID for personalized feed"),
    db: Session = Depends(get_db),
) -> RegulationListResponse:
    """
    Get a personalized feed of regulations based on session domain preferences.
    """
    try:
        regulations, total = SessionService.get_personalized_feed(
            db, session_id=session_id, limit=limit, offset=offset
        )

        regulation_responses = []
        for r in regulations:
            reg_dict = {
                "id": r.id,
                "source_body": r.source_body,
                "original_title": r.original_title,
                "original_date": r.original_date,
                "source_url": r.source_url,
                "ai_title": r.ai_title,
                "ai_tldr": r.ai_tldr,
                "ai_what_changed": r.ai_what_changed,
                "ai_who_affected": r.ai_who_affected,
                "ai_action_required": r.ai_action_required,
                "ai_impact_level": r.ai_impact_level,
                "domains": json.loads(r.domains) if isinstance(r.domains, str) else r.domains,
                "processing_status": r.processing_status,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            regulation_responses.append(RegulationResponse(**reg_dict))

        page = (offset // limit) + 1
        has_more = (offset + limit) < total

        return RegulationListResponse(
            regulations=regulation_responses,
            total=total,
            page=page,
            page_size=limit,
            has_more=has_more,
        )
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting personalized feed: {str(e)}")
        raise DatabaseException(str(e), "get_my_feed")

@router.get("/regulations/{regulation_id}", response_model=RegulationResponse, tags=["Regulations"])
async def get_regulation(
    regulation_id: int,
    db: Session = Depends(get_db),
) -> RegulationResponse:
    """
    Get a specific regulation by ID.

    Args:
        regulation_id: ID of the regulation
        db: Database session

    Returns:
        Regulation details

    Raises:
        NotFoundException: If regulation not found
    """
    try:
        regulation = db.query(Regulation).filter(Regulation.id == regulation_id).first()

        if not regulation:
            logger.warning(f"Regulation not found: {regulation_id}")
            raise NotFoundException("Regulation", regulation_id)

        logger.info(f"Retrieved regulation: {regulation_id}")

        # Parse JSON fields
        reg_dict = {
            "id": regulation.id,
            "source_body": regulation.source_body,
            "original_title": regulation.original_title,
            "original_date": regulation.original_date,
            "source_url": regulation.source_url,
            "ai_title": regulation.ai_title,
            "ai_tldr": regulation.ai_tldr,
            "ai_what_changed": regulation.ai_what_changed,
            "ai_who_affected": regulation.ai_who_affected,
            "ai_action_required": regulation.ai_action_required,
            "ai_impact_level": regulation.ai_impact_level,
            "domains": json.loads(regulation.domains) if isinstance(regulation.domains, str) else regulation.domains,
            "processing_status": regulation.processing_status,
            "created_at": regulation.created_at,
            "updated_at": regulation.updated_at,
        }
        return RegulationResponse(**reg_dict)

    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting regulation {regulation_id}: {str(e)}")
        raise DatabaseException(str(e), "get_regulation")


@router.get("/domains", response_model=DomainsResponse, tags=["Domains"])
async def list_domains(db: Session = Depends(get_db)) -> DomainsResponse:
    """
    Get available domains with regulation counts.

    Returns a list of all regulatory domains with the count of regulations
    in each domain.

    Args:
        db: Database session

    Returns:
        List of domains with counts

    Raises:
        DatabaseException: If database query fails
    """
    try:
        # Get all regulations
        regulations = db.query(Regulation).all()

        # Count regulations by domain
        domain_counts = {}
        for regulation in regulations:
            try:
                domains = json.loads(regulation.domains)
                for domain in domains:
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in domains for regulation {regulation.id}")
                continue

        # Convert to DomainCount objects
        domain_list = [
            DomainCount(name=name, count=count)
            for name, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        logger.info(f"Listed {len(domain_list)} domains")
        return DomainsResponse(domains=domain_list)

    except Exception as e:
        logger.error(f"Error listing domains: {str(e)}")
        raise DatabaseException(str(e), "list_domains")


@router.get("/stats", response_model=StatsResponse, tags=["Stats"])
async def get_stats(db: Session = Depends(get_db)) -> StatsResponse:
    """
    Get statistics dashboard data, including time-series trends.
    """
    try:
        # Total regulations
        total = db.query(func.count(Regulation.id)).scalar() or 0

        # By source body
        by_source = {}
        source_counts = db.query(
            Regulation.source_body, func.count(Regulation.id)
        ).group_by(Regulation.source_body).all()
        for source, count in source_counts:
            by_source[source] = count

        # By impact level
        by_impact = {}
        impact_counts = db.query(
            Regulation.ai_impact_level, func.count(Regulation.id)
        ).group_by(Regulation.ai_impact_level).all()
        for impact, count in impact_counts:
            by_impact[impact] = count

        # By domain (optimized: use database aggregation instead of loading all records)
        by_domain = {}
        try:
            # Fetch only the domains JSON field to minimize memory usage
            domain_records = db.query(Regulation.domains).filter(
                Regulation.domains != None,
                Regulation.domains != ""
            ).all()
            for (domains_json,) in domain_records:
                try:
                    domains = json.loads(domains_json)
                    for domain in domains:
                        by_domain[domain] = by_domain.get(domain, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    continue
        except Exception as e:
            logger.warning(f"Failed to compute domain stats: {str(e)}")
            by_domain = {}

        # Time series trend (last 30 days)
        time_series = RegulationService.get_time_series_stats(db)

        # Last update
        last_regulation = db.query(Regulation).order_by(desc(Regulation.created_at)).first()
        last_updated = last_regulation.created_at if last_regulation else datetime.utcnow()

        return {
            "total_regulations": total,
            "by_source": by_source,
            "by_impact": by_impact,
            "by_domain": by_domain,
            "last_updated": last_updated,
            "trends": time_series
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise DatabaseException(str(e), "get_stats")


@router.post("/session", response_model=SessionResponse, tags=["Session"])
async def create_session(
    request: SessionRequest,
    db: Session = Depends(get_db),
) -> SessionResponse:
    """
    Create a new user session.

    Each session has a unique ID and can track domain preferences.
    Phase 1: No authentication, just session ID based tracking.
    Phase 2: Will add email and authentication.

    Args:
        request: Session creation request with optional domain preferences
        db: Database session

    Returns:
        Session details with ID and domains

    Raises:
        ValidationException: If domains invalid
        DatabaseException: If session creation fails
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4()).replace("-", "")[:50]  # Simplified unique ID

        # Convert domains to JSON
        domains_json = json.dumps(request.domains)

        # Create user preference record
        user_pref = UserPreference(
            session_id=session_id,
            selected_domains=domains_json,
        )

        db.add(user_pref)
        db.commit()

        logger.info(
            f"Created session: {session_id}",
            extra={
                "session_id": session_id,
                "domains": request.domains,
            },
        )

        return SessionResponse(
            session_id=session_id,
            domains=request.domains,
            created_at=user_pref.created_at,
            last_accessed=user_pref.last_accessed,
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating session: {str(e)}")
        raise DatabaseException(str(e), "create_session")


@router.get("/session/{session_id}", response_model=SessionResponse, tags=["Session"])
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> SessionResponse:
    """
    Get session details by ID.

    Args:
        session_id: Session ID
        db: Database session

    Returns:
        Session details

    Raises:
        NotFoundException: If session not found
    """
    try:
        user_pref = db.query(UserPreference).filter(
            UserPreference.session_id == session_id
        ).first()

        if not user_pref:
            logger.warning(f"Session not found: {session_id}")
            raise NotFoundException("Session", session_id)

        domains = json.loads(user_pref.selected_domains)

        logger.info(f"Retrieved session: {session_id}")
        return SessionResponse(
            session_id=session_id,
            domains=domains,
            created_at=user_pref.created_at,
            last_accessed=user_pref.last_accessed,
        )

    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {str(e)}")
        raise DatabaseException(str(e), "get_session")


@router.put("/session/{session_id}", response_model=SessionResponse, tags=["Session"])
async def update_session(
    session_id: str,
    request: PreferenceUpdateRequest,
    db: Session = Depends(get_db),
) -> SessionResponse:
    """
    Update session preferences (domains).

    Args:
        session_id: Session ID
        request: Update request with new preferences
        db: Database session

    Returns:
        Updated session details

    Raises:
        NotFoundException: If session not found
        DatabaseException: If update fails
    """
    try:
        user_pref = db.query(UserPreference).filter(
            UserPreference.session_id == session_id
        ).first()

        if not user_pref:
            logger.warning(f"Session not found: {session_id}")
            raise NotFoundException("Session", session_id)

        # Update domains if provided
        if request.domains is not None:
            user_pref.selected_domains = json.dumps(request.domains)

        # Update last_accessed
        user_pref.last_accessed = datetime.utcnow()

        db.commit()

        domains = json.loads(user_pref.selected_domains)

        logger.info(
            f"Updated session: {session_id}",
            extra={"domains": domains},
        )

        return SessionResponse(
            session_id=session_id,
            domains=domains,
            created_at=user_pref.created_at,
            last_accessed=user_pref.last_accessed,
        )

    except NotFoundException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating session {session_id}: {str(e)}")
        raise DatabaseException(str(e), "update_session")


@router.get("/scraper-runs", tags=["Scraper"])
async def get_scraper_runs(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    source: str = Query("", description="Filter by source body"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get recent scraper run history.

    Args:
        limit: Number of runs to return
        offset: Number of runs to skip
        source: Filter by source body
        db: Database session

    Returns:
        List of scraper runs with pagination
    """
    try:
        query = db.query(ScraperRun).order_by(desc(ScraperRun.run_timestamp))

        if source:
            query = query.filter(ScraperRun.source_body == source)

        total = query.count()
        runs = query.offset(offset).limit(limit).all()

        logger.info(f"Retrieved {len(runs)} scraper runs")

        return {
            "runs": [
                {
                    "id": r.id,
                    "source_body": r.source_body,
                    "status": r.status,
                    "regulations_found": r.regulations_found,
                    "regulations_new": r.regulations_new,
                    "regulations_duplicated": r.regulations_duplicated,
                    "duration_seconds": r.duration_seconds,
                    "run_timestamp": r.run_timestamp.isoformat() if r.run_timestamp else None,
                }
                for r in runs
            ],
            "total": total,
            "page": (offset // limit) + 1,
            "page_size": limit,
            "has_more": (offset + limit) < total,
        }

    except Exception as e:
        logger.error(f"Error getting scraper runs: {str(e)}")
        raise DatabaseException(str(e), "get_scraper_runs")
