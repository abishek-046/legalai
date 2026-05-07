"""
Document data models (Pydantic schemas)
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class DocumentResponse(BaseModel):
    id: str
    userId: str
    filename: str
    documentType: str
    summary: Optional[str] = None
    riskLevel: Optional[RiskLevel] = None
    warnings: Optional[List[str]] = []
    suspiciousClauses: Optional[List[str]] = []
    missingClauses: Optional[List[str]] = []
    financialRisks: Optional[List[str]] = []
    expiryRisks: Optional[List[str]] = []
    unfairConditions: Optional[List[str]] = []
    recommendations: Optional[List[str]] = []
    safeToSign: Optional[bool] = None
    createdAt: datetime

    class Config:
        from_attributes = True


class DocumentListItem(BaseModel):
    id: str
    filename: str
    documentType: str
    riskLevel: Optional[RiskLevel] = None
    safeToSign: Optional[bool] = None
    createdAt: datetime
