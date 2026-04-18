"""
Input validation utilities for RegRadar API.

Provides centralized validation functions to prevent common security issues
like injection attacks, invalid data types, and malformed inputs.
"""

import re
from typing import Optional, List
from src.utils.errors import ValidationException


class InputValidator:
    """Centralized input validation for the RegRadar API."""

    # Validation patterns
    SESSION_ID_PATTERN = re.compile(r"^[a-z0-9\-]{32,50}$")
    DOMAIN_PATTERN = re.compile(r"^[a-z_]{2,20}$", re.IGNORECASE)
    SOURCE_PATTERN = re.compile(r"^[A-Z]{2,10}$")
    IMPACT_PATTERN = re.compile(r"^(HIGH|MEDIUM|LOW)$")
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    VALID_SOURCES = ["SEBI", "RBI", "MCA", "MEITY", "DPIIT"]
    VALID_IMPACTS = ["HIGH", "MEDIUM", "LOW"]

    @staticmethod
    def validate_session_id(session_id: str) -> str:
        """Validate session ID format."""
        if not session_id or not isinstance(session_id, str):
            raise ValidationException("Invalid session ID: must be a non-empty string", "session_id", session_id)
        if not InputValidator.SESSION_ID_PATTERN.match(session_id):
            raise ValidationException(
                "Invalid session ID format: must be 32-50 character alphanumeric string",
                "session_id",
                session_id
            )
        return session_id

    @staticmethod
    def validate_domain(domain: str) -> str:
        """Validate domain format."""
        if not domain or not isinstance(domain, str):
            raise ValidationException("Invalid domain: must be a non-empty string", "domain", domain)
        if not InputValidator.DOMAIN_PATTERN.match(domain):
            raise ValidationException(
                "Invalid domain format: must be 2-20 characters, alphanumeric with underscores",
                "domain",
                domain
            )
        return domain.lower()

    @staticmethod
    def validate_domains(domains: List[str]) -> List[str]:
        """Validate list of domains."""
        if not isinstance(domains, list):
            raise ValidationException("Domains must be a list", "domains", str(domains))
        if len(domains) > 10:
            raise ValidationException("Maximum 10 domains allowed", "domains", str(len(domains)))
        return [InputValidator.validate_domain(d) for d in domains]

    @staticmethod
    def validate_source(source: str) -> str:
        """Validate regulatory source."""
        if not source or not isinstance(source, str):
            raise ValidationException("Invalid source: must be a non-empty string", "source", source)
        source = source.upper()
        if source not in InputValidator.VALID_SOURCES:
            raise ValidationException(
                f"Invalid source: must be one of {InputValidator.VALID_SOURCES}",
                "source",
                source
            )
        return source

    @staticmethod
    def validate_impact(impact: str) -> str:
        """Validate impact level."""
        if not impact or not isinstance(impact, str):
            raise ValidationException("Invalid impact: must be a non-empty string", "impact", impact)
        impact = impact.upper()
        if impact not in InputValidator.VALID_IMPACTS:
            raise ValidationException(
                f"Invalid impact: must be one of {InputValidator.VALID_IMPACTS}",
                "impact",
                impact
            )
        return impact

    @staticmethod
    def validate_pagination(limit: int, offset: int) -> tuple[int, int]:
        """Validate pagination parameters."""
        if not isinstance(limit, int) or not isinstance(offset, int):
            raise ValidationException("Limit and offset must be integers", "pagination", f"limit={limit}, offset={offset}")
        if limit < 1 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100", "limit", limit)
        if offset < 0:
            raise ValidationException("Offset must be non-negative", "offset", offset)
        return limit, offset

    @staticmethod
    def sanitize_search_query(query: str, max_length: int = 255) -> str:
        """Sanitize search query string."""
        if not isinstance(query, str):
            raise ValidationException("Query must be a string", "query", str(type(query)))
        # Remove SQL/NoSQL injection patterns and limit length
        sanitized = re.sub(r"[%;'\"\\`]", "", query)[:max_length]
        if not sanitized:
            raise ValidationException("Query cannot be empty after sanitization", "query", query)
        return sanitized
