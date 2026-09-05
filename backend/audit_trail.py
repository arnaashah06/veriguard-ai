# backend/audit_trail.py
"""
VeriGuard AI - Compliance Audit Trail Engine
Generates an immutable, millisecond-accurate timestamped log of all checks,
algorithmic executions, and cryptographic validations performed during verification.
"""

import time
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


class AuditTrailLogger:
    def __init__(self, session_id: Optional[str] = None):
        self.start_time = time.time()
        self.session_id = session_id or f"VR-AUDIT-{int(self.start_time * 1000)}"
        self.session_iso = datetime.now(timezone.utc).isoformat()
        self.events: List[Dict[str, Any]] = []
        self._index = 1

    def log_event(
        self,
        category: str,
        step: str,
        status: str = "SUCCESS",
        details: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Records a timestamped audit event with elapsed millisecond offset.
        """
        now = time.time()
        elapsed_ms = round((now - self.start_time) * 1000, 1)
        now_iso = datetime.now(timezone.utc).isoformat()

        icon_map = {
            "INGESTION": "📥",
            "OCR": "🔍",
            "FORENSICS": "🧬",
            "VALIDATION": "📑",
            "BIOMETRICS": "👤",
            "CROSS_DOC": "✨",
            "RISK_ENGINE": "🎯",
            "COMPLIANCE": "🗄️",
            "SEAL": "🔒",
        }

        event = {
            "index": self._index,
            "timestamp": now_iso,
            "elapsed_ms": elapsed_ms,
            "elapsed_formatted": f"+{int(elapsed_ms)}ms",
            "category": category.upper(),
            "category_icon": icon_map.get(category.upper(), "📌"),
            "step": step,
            "status": status.upper(),
            "details": details,
            "metadata": metadata or {},
        }
        self.events.append(event)
        self._index += 1
        return event

    def finalize(self) -> Dict[str, Any]:
        """
        Finalizes and cryptographically seals the audit trail ledger.
        """
        total_duration_ms = round((time.time() - self.start_time) * 1000, 1)

        # Generate cryptographic seal hash over all logged event signatures
        hasher = hashlib.sha256()
        for ev in self.events:
            sig = f"{ev['index']}:{ev['timestamp']}:{ev['step']}:{ev['status']}:{ev['details']}"
            hasher.update(sig.encode("utf-8"))
        seal_hash = hasher.hexdigest().upper()

        # Log final sealing event
        seal_event = {
            "index": self._index,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "elapsed_ms": total_duration_ms,
            "elapsed_formatted": f"+{int(total_duration_ms)}ms",
            "category": "SEAL",
            "category_icon": "🔒",
            "step": "Cryptographic Audit Ledger Sealed",
            "status": "SUCCESS",
            "details": f"Screening session verified and sealed with SHA-256 digest: {seal_hash[:16]}...",
            "metadata": {"seal_hash": seal_hash, "total_events": len(self.events) + 1},
        }
        self.events.append(seal_event)

        return {
            "audit_id": self.session_id,
            "session_start": self.session_iso,
            "total_duration_ms": total_duration_ms,
            "total_events": len(self.events),
            "cryptographic_seal": seal_hash,
            "events": self.events,
        }
