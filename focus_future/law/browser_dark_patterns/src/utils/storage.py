"""
Storage utilities for persisting exploration sessions in SQLite.

Provides database interface for saving and retrieving sessions, findings, and evidence.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import aiosqlite

from src.evidence.models import ExplorationSession, Finding


class SessionStorage:
    """SQLite-based storage for exploration sessions."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize session storage.

        Args:
            db_path: Path to SQLite database (default: ./data/sessions/sessions.db)
        """
        self.db_path = db_path or Path("./data/sessions/sessions.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self) -> None:
        """Initialize database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    session_name TEXT NOT NULL,
                    target_url TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    frameworks_used TEXT NOT NULL,
                    max_depth INTEGER NOT NULL,
                    total_patterns_checked INTEGER DEFAULT 0,
                    total_patterns_detected INTEGER DEFAULT 0,
                    agent_version TEXT,
                    model_used TEXT,
                    session_data TEXT NOT NULL
                )
            """
            )

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS findings (
                    finding_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    pattern_id TEXT NOT NULL,
                    pattern_name TEXT NOT NULL,
                    framework_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    url TEXT NOT NULL,
                    page_title TEXT,
                    summary TEXT NOT NULL,
                    validated BOOLEAN DEFAULT 0,
                    false_positive BOOLEAN DEFAULT 0,
                    timestamp TEXT NOT NULL,
                    finding_data TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """
            )

            # Create indexes for faster queries
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_findings_session_id ON findings(session_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_findings_framework ON findings(framework_name)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity)"
            )

            await db.commit()

    async def save_session(self, session: ExplorationSession) -> None:
        """
        Save exploration session to database.

        Args:
            session: ExplorationSession to save
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Serialize session data
            session_data = session.model_dump_json()

            # Insert or replace session
            await db.execute(
                """
                INSERT OR REPLACE INTO sessions (
                    session_id, session_name, target_url, start_time, end_time,
                    frameworks_used, max_depth, total_patterns_checked,
                    total_patterns_detected, agent_version, model_used, session_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    session.session_id,
                    session.session_name,
                    session.target_url,
                    session.start_time.isoformat(),
                    session.end_time.isoformat() if session.end_time else None,
                    json.dumps(session.frameworks_used),
                    session.max_depth,
                    session.total_patterns_checked,
                    session.total_patterns_detected,
                    session.agent_version,
                    session.model_used,
                    session_data,
                ),
            )

            # Save all findings
            for finding in session.findings:
                await self.save_finding(db, finding, session.session_id)

            await db.commit()

    async def save_finding(
        self, db: aiosqlite.Connection, finding: Finding, session_id: str
    ) -> None:
        """
        Save finding to database.

        Args:
            db: Database connection
            finding: Finding to save
            session_id: Associated session ID
        """
        finding_data = finding.model_dump_json()

        await db.execute(
            """
            INSERT OR REPLACE INTO findings (
                finding_id, session_id, pattern_id, pattern_name, framework_name,
                severity, confidence, url, page_title, summary, validated,
                false_positive, timestamp, finding_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                finding.finding_id,
                session_id,
                finding.pattern_id,
                finding.pattern_name,
                finding.framework_name,
                finding.severity.value,
                finding.confidence,
                finding.url,
                finding.page_title,
                finding.summary,
                finding.validated,
                finding.false_positive,
                finding.timestamp.isoformat(),
                finding_data,
            ),
        )

    async def load_session(self, session_id: str) -> Optional[ExplorationSession]:
        """
        Load exploration session from database.

        Args:
            session_id: Session ID to load

        Returns:
            ExplorationSession or None if not found
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT session_data FROM sessions WHERE session_id = ?", (session_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return ExplorationSession.model_validate_json(row[0])
                return None

    async def list_sessions(
        self, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        List all sessions with basic info.

        Args:
            limit: Maximum number of sessions to return
            offset: Offset for pagination

        Returns:
            List of session summaries
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT session_id, session_name, target_url, start_time, end_time,
                       total_patterns_detected, frameworks_used
                FROM sessions
                ORDER BY start_time DESC
                LIMIT ? OFFSET ?
            """,
                (limit, offset),
            ) as cursor:
                rows = await cursor.fetchall()

                return [
                    {
                        "session_id": row[0],
                        "session_name": row[1],
                        "target_url": row[2],
                        "start_time": row[3],
                        "end_time": row[4],
                        "total_patterns_detected": row[5],
                        "frameworks_used": json.loads(row[6]),
                    }
                    for row in rows
                ]

    async def get_findings_by_session(self, session_id: str) -> list[Finding]:
        """
        Get all findings for a session.

        Args:
            session_id: Session ID

        Returns:
            List of findings
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT finding_data FROM findings WHERE session_id = ? ORDER BY timestamp",
                (session_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [Finding.model_validate_json(row[0]) for row in rows]

    async def get_findings_by_framework(
        self, framework_name: str, limit: int = 100
    ) -> list[Finding]:
        """
        Get findings for a specific framework.

        Args:
            framework_name: Framework name
            limit: Maximum number of findings

        Returns:
            List of findings
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT finding_data FROM findings
                WHERE framework_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (framework_name, limit),
            ) as cursor:
                rows = await cursor.fetchall()
                return [Finding.model_validate_json(row[0]) for row in rows]

    async def update_finding_validation(
        self, finding_id: str, validated: bool, false_positive: bool, notes: str = ""
    ) -> None:
        """
        Update finding validation status.

        Args:
            finding_id: Finding ID
            validated: Whether validated
            false_positive: Whether it's a false positive
            notes: Reviewer notes
        """
        async with aiosqlite.connect(self.db_path) as db:
            # First get the current finding data
            async with db.execute(
                "SELECT finding_data FROM findings WHERE finding_id = ?", (finding_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    finding = Finding.model_validate_json(row[0])
                    finding.validated = validated
                    finding.false_positive = false_positive
                    finding.notes = notes

                    # Update in database
                    await db.execute(
                        """
                        UPDATE findings
                        SET validated = ?, false_positive = ?, finding_data = ?
                        WHERE finding_id = ?
                    """,
                        (validated, false_positive, finding.model_dump_json(), finding_id),
                    )

                    await db.commit()

    async def delete_session(self, session_id: str) -> None:
        """
        Delete session and all associated findings.

        Args:
            session_id: Session ID to delete
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM findings WHERE session_id = ?", (session_id,))
            await db.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            await db.commit()

    async def get_statistics(self) -> dict[str, Any]:
        """
        Get overall statistics from database.

        Returns:
            Dictionary with statistics
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Total sessions
            async with db.execute("SELECT COUNT(*) FROM sessions") as cursor:
                total_sessions = (await cursor.fetchone())[0]

            # Total findings
            async with db.execute("SELECT COUNT(*) FROM findings") as cursor:
                total_findings = (await cursor.fetchone())[0]

            # Findings by severity
            async with db.execute(
                "SELECT severity, COUNT(*) FROM findings GROUP BY severity"
            ) as cursor:
                severity_counts = dict(await cursor.fetchall())

            # Findings by framework
            async with db.execute(
                "SELECT framework_name, COUNT(*) FROM findings GROUP BY framework_name"
            ) as cursor:
                framework_counts = dict(await cursor.fetchall())

            # Most recent session
            async with db.execute(
                "SELECT session_name, start_time FROM sessions ORDER BY start_time DESC LIMIT 1"
            ) as cursor:
                row = await cursor.fetchone()
                most_recent_session = (
                    {"name": row[0], "time": row[1]} if row else None
                )

            return {
                "total_sessions": total_sessions,
                "total_findings": total_findings,
                "findings_by_severity": severity_counts,
                "findings_by_framework": framework_counts,
                "most_recent_session": most_recent_session,
            }

    async def search_findings(
        self,
        pattern_name: Optional[str] = None,
        framework: Optional[str] = None,
        min_confidence: Optional[float] = None,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> list[Finding]:
        """
        Search findings with filters.

        Args:
            pattern_name: Filter by pattern name (partial match)
            framework: Filter by framework name
            min_confidence: Minimum confidence threshold
            severity: Filter by severity level
            limit: Maximum results

        Returns:
            List of matching findings
        """
        query = "SELECT finding_data FROM findings WHERE 1=1"
        params = []

        if pattern_name:
            query += " AND pattern_name LIKE ?"
            params.append(f"%{pattern_name}%")

        if framework:
            query += " AND framework_name = ?"
            params.append(framework)

        if min_confidence is not None:
            query += " AND confidence >= ?"
            params.append(min_confidence)

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [Finding.model_validate_json(row[0]) for row in rows]


# Helper function
async def get_storage(db_path: Optional[Path] = None) -> SessionStorage:
    """
    Get initialized session storage.

    Args:
        db_path: Optional database path

    Returns:
        Initialized SessionStorage instance
    """
    storage = SessionStorage(db_path)
    await storage.initialize()
    return storage
