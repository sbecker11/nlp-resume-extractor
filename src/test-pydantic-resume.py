from typing import List, Optional
from pydantic import BaseModel


class Duration(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None


class ContactInformation(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None
    country: str


class WorkHistoryItem(BaseModel):
    workPositionOrTitle: str
    workForCompanyName: str
    workLocationOrRemote: str
    workDuration: Optional[Duration] = None
    workResponsibilitiesAccomplishments: List[str]


class EducationHistoryItem(BaseModel):
    institution: str
    degree: str
    majors: Optional[List[str]] = None
    minors: Optional[List[str]] = None
    gradePointAverage: Optional[str] = None
    duration: Optional[Duration] = None


class Resume(BaseModel):
    contactInformation: ContactInformation
    workHistory: List[WorkHistoryItem]
    educationHistory: List[EducationHistoryItem]
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    publications: Optional[List[str]] = None
    patents: Optional[List[str]] = None
    websites: Optional[List[str]] = None