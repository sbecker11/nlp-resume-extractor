"""
This module defines data models for a resume using Pydantic.
"""

from datetime import datetime
import warnings
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

warnings.filterwarnings('ignore', category=DeprecationWarning)

class Duration(BaseModel):
    """
    Duration

    Args:
        BaseModel (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    start: Optional[str] = Field(None, description="The start date")
    end: Optional[str] = Field(None, description="The end date")

    @field_validator('start', 'end')
    @classmethod
    def validate_date_format(cls, value, field):
        if value is None:
            return value
        date_formats = ['%Y-%m-%d', '%Y-%m', '%Y']
        for date_format in date_formats:
            try:
                datetime.strptime(value, date_format)
                return value
            except ValueError:
                pass
        raise ValueError(f"{field.name} must be in the format 'YYYY-MM-DD', 'YYYY-MM', or 'YYYY'")

class ContactInformation(BaseModel):
    """
    ContactInformation
    Args:
        BaseModel (_type_): _description_
    """
    firstName: str = Field(..., description="The person's first name")
    lastName: str = Field(..., description="The person's last name")
    email: str = Field(..., description="The person's email address")
    phone: Optional[str] = Field(None, description="The person's phone number")
    address: Optional[str] = Field(None, description="The person's street address")
    city: Optional[str] = Field(None, description="The city")
    state: Optional[str] = Field(None, description="The state or province")
    zipcode: Optional[str] = Field(None, description="The zip or postal code")
    country: Optional[str] = Field(None, description="The country")

class WorkHistoryItem(BaseModel):
    """
    WorkHistoryItem
    Args:
        BaseModel (_type_): _description_
    """
    workPositionOrTitle: str = Field(..., description="The job title")
    workForCompanyName: str = Field(..., description="The company name")
    workLocationOrRemote: str = Field(..., description="Location or 'Remote' if remote work")
    workDuration: Optional[Duration] = Field(None, description="Start and end dates of employment")
    workResponsibilitiesAccomplishments: List[str] = Field(..., description="List of responsibilities or accomplishments")

class EducationHistoryItem(BaseModel):
    """
    EductionHistoryItem

    Args:
        BaseModel (_type_): _description_
    """
    institution: str = Field(..., description="Name of the educational institution")
    degree: str = Field(..., description="Degree earned")
    majors: Optional[str] = Field(None, description="List of majors")
    minors: Optional[str] = Field(None, description="List of minors")
    gradePointAverage: Optional[str] = Field(None, description="GPA")
    duration: Optional[Duration] = Field(None, description="Start and end dates of education")

class Resume(BaseModel):
    """
    Resume

    Args:
        BaseModel (_type_): _description_
    """
    contactInformation: ContactInformation = Field(..., description="Contact details")
    workHistory: List[WorkHistoryItem] = Field(..., description="Work history")
    educationHistory: List[EducationHistoryItem] = Field(..., description="Educational background")
    skills: Optional[str] = Field(None, description="List of skills")
    certifications: Optional[str] = Field(None, description="List of certifications")
    publications: Optional[str] = Field(None, description="List of publications")
    patents: Optional[str] = Field(None, description="List of patents")
    websites: Optional[List[str]] = Field(None, description="List of personal or professional websites")

# Example usage
resume_data = {
    "contactInformation": {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@example.com",
        "phone": "123-456-7890",
        "address": None,
        "city": None,
        "state": None,
        "zipcode": None,
        "country": "USA"
    },
    "workHistory": [
        {
            "workPositionOrTitle": "Software Engineer",
            "workForCompanyName": "TechCo",
            "workLocationOrRemote": "San Francisco, CA",
            "workDuration": {"start": "2019-01", "end": "2021-06"},
            "workResponsibilitiesAccomplishments": [
                "Developed a scalable web application",
                "Led a team of five developers"
            ]
        }
    ],
    "educationHistory": [
        {
            "institution": "Example University",
            "degree": "BS",
            "majors": "Computer Science",
            "duration": {"start": "2015", "end": "2019"}
        }
    ],
    "skills": "Python, JavaScript, AWS",
    "websites": ["linkedin.com/in/johndoe", "github.com/johndoe"]
}

resume = Resume(
    contactInformation=ContactInformation(**resume_data["contactInformation"]),
    workHistory=[WorkHistoryItem(**item) for item in resume_data["workHistory"]],
    educationHistory=[EducationHistoryItem(**item) for item in resume_data["educationHistory"]],
    skills=resume_data.get("skills"),
    certifications=resume_data.get("certifications"),
    publications=resume_data.get("publications"),
    patents=resume_data.get("patents"),
    websites=resume_data.get("websites")
)

# Accessing data
print(resume.contactInformation)
print(resume.workHistory[0].workPositionOrTitle)
print(resume.skills)
print(resume)
