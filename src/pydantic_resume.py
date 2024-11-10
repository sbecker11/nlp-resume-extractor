"""
This module defines data models for a resume using Pydantic.
"""

from datetime import datetime
import warnings
from typing import Optional, List
from pydantic import BaseModel, Field, validator

warnings.filterwarnings('ignore', category=DeprecationWarning)

class Duration(BaseModel):
    """
    Duration model to represent the start and end dates.
    """
    start: Optional[str] = Field(None, description="The start date")
    end: Optional[str] = Field(None, description="The end date")

    @validator('start', 'end')
    @classmethod
    def validate_date_format(cls, value, field):
        """ validate_date_format """
        
        date_formats = {
            '%Y-%m-%d': 'YYYY-MM-DD',
            '%Y-%m': 'YYYY-MM', 
            '%Y': 'YYYY',
            '%b %d, %Y': 'MM DD, YYYY',
            '%b %Y': 'MM YYYY',
            '%B %d, %Y': 'MMM DD, YYYY',
            '%B %Y': 'MMM YYYY'
        }
        date_format_values = ", ".join([value for value in date_formats.values()])

        if value is None:
            return value
        for date_format, _ in date_formats.items():
            try:
                datetime.strptime(value, date_format)
                return value
            except ValueError:
                pass
        raise ValueError(f"{field.field_name} is not in the list of supported datetime formats {date_format_values}")

class ContactInformation(BaseModel):
    """
    ContactInformation
    Args:
    """
    firstName: str = Field(..., description="The person's first name")
    lastName: str = Field(..., description="The person's last name")
    email: str = Field(..., description="The person's email address")
    phone: Optional[str] = Field(None, description="The person's phone number")
    """
    ContactInformation model to store personal contact details.
    """

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

    """
    WorkHistoryItem model to store details of work history.
    """

class EducationHistoryItem(BaseModel):
    """
    EducationHistoryItem model to store details of educational background.
    """
    institution: str = Field(..., description="The name of the institution")
    degree: str = Field(..., description="The degree obtained")
    majors: str = Field(..., description="The majors")
    duration: Optional[Duration] = Field(None, description="Start and end dates of education")
    """
    This module defines data models for a resume using Pydantic.
    """
    
    from datetime import datetime
    import warnings
    from typing import Optional, List
    from pydantic import BaseModel, Field, validator
    
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    
    class Duration(BaseModel):
        """
        Duration model to represent the start and end dates.
        """
        start: Optional[str] = Field(None, description="The start date")
        end: Optional[str] = Field(None, description="The end date")
    
        @validator('start', 'end')
        @classmethod
        def validate_date_format(cls, value, field):
            """ validate_date_format """
            
            date_formats = {
                '%Y-%m-%d': 'YYYY-MM-DD',
                '%Y-%m': 'YYYY-MM', 
                '%Y': 'YYYY',
                '%b %d, %Y': 'MM DD, YYYY',
                '%b %Y': 'MM YYYY',
                '%B %d, %Y': 'MMM DD, YYYY',
                '%B %Y': 'MMM YYYY'
            }
            date_format_values = ", ".join([value for value in date_formats.values()])
    
            if value is None:
                return value
            for date_format, _ in date_formats.items():
                try:
                    datetime.strptime(value, date_format)
                    return value
                except ValueError:
                    pass
            raise ValueError(f"{field.field_name} is not in the list of supported datetime formats {date_format_values}")
    
    class ContactInformation(BaseModel):
        """
        ContactInformation
        Args:
        """
        firstName: str = Field(..., description="The person's first name")
        lastName: str = Field(..., description="The person's last name")
        email: str = Field(..., description="The person's email address")
        phone: Optional[str] = Field(None, description="The person's phone number")
        """
        ContactInformation model to store personal contact details.
        """
    
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
    
        """
        WorkHistoryItem model to store details of work history.
        """
    
    class EducationHistoryItem(BaseModel):
        """
        EducationHistoryItem model to store details of educational background.
        """
        institution: str = Field(..., description="The name of the institution")
        degree: str = Field(..., description="The degree obtained")
        majors: str = Field(..., description="The majors")
        duration: Optional[Duration] = Field(None, description="Start and end dates of education")
    
    class PydanticResume(BaseModel):
        """
        PydanticResume model that contains all the other models.
        """
        contactInformation: ContactInformation = Field(..., description="Contact details")
        workHistory: List[WorkHistoryItem] = Field(..., description="Work history")
        educationHistory: List[EducationHistoryItem] = Field(..., description="Educational background")
        skills: Optional[str] = Field(None, description="List of skills")
        certifications: Optional[str] = Field(None, description="List of certifications")
        publications: Optional[str] = Field(None, description="List of publications")
        patents: Optional[str] = Field(None, description="List of patents")
        websites: Optional[List[str]] = Field(None, description="List of personal or professional websites")
    
    resume_data = {
        "contactInformation": {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
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
    
    contact_info_data = {k: v for k, v in resume_data["contactInformation"].items() if k in ContactInformation.__fields__}
    
    resume_parsed = PydanticResume(
        contactInformation=ContactInformation(**contact_info_data),
        workHistory=[WorkHistoryItem(**item) for item in resume_data["workHistory"]],
        educationHistory=[EducationHistoryItem(**item) for item in resume_data["educationHistory"]],
        skills=resume_data.get("skills"),
        certifications=resume_data.get("certifications"),
        publications=resume_data.get("publications"),
        patents=resume_data.get("patents"),
        websites=resume_data.get("websites")
    )   
    
    # Accessing data
    print(resume_parsed.contactInformation)
    print(resume_parsed.workHistory[0].workPositionOrTitle)
    print(resume_parsed.skills)
    print(resume_parsed)
        """
        PydanticResume model that contains all the other models.
        """
        contactInformation: ContactInformation = Field(..., description="Contact details")
        workHistory: List[WorkHistoryItem] = Field(..., description="Work history")
        educationHistory: List[EducationHistoryItem] = Field(..., description="Educational background")
        skills: Optional[str] = Field(None, description="List of skills")
        certifications: Optional[str] = Field(None, description="List of certifications")
        publications: Optional[str] = Field(None, description="List of publications")
        patents: Optional[str] = Field(None, description="List of patents")
        websites: Optional[List[str]] = Field(None, description="List of personal or professional websites")


    class PydanticResume(BaseModel):
        """
        PydanticResume model that contains all the other models.
        """
        contactInformation: ContactInformation = Field(..., description="Contact details")
        workHistory: List[WorkHistoryItem] = Field(..., description="Work history")
        educationHistory: List[EducationHistoryItem] = Field(..., description="Educational background")
        skills: Optional[str] = Field(None, description="List of skills")
        certifications: Optional[str] = Field(None, description="List of certifications")
        publications: Optional[str] = Field(None, description="List of publications")
        patents: Optional[str] = Field(None, description="List of patents")
        websites: Optional[List[str]] = Field(None, description="List of personal or professional websites")
    
    resume_data = {
        "contactInformation": {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
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
    
    contact_info_data = {k: v for k, v in resume_data["contactInformation"].items() if k in ContactInformation.__fields__}
    
    resume_parsed = PydanticResume(
        contactInformation=ContactInformation(**contact_info_data),
        workHistory=[WorkHistoryItem(**item) for item in resume_data["workHistory"]],
        educationHistory=[EducationHistoryItem(**item) for item in resume_data["educationHistory"]],
        skills=resume_data.get("skills"),
        certifications=resume_data.get("certifications"),
        publications=resume_data.get("publications"),
        patents=resume_data.get("patents"),
        websites=resume_data.get("websites")
    )   
    
    # Accessing data
    print(resume_parsed.contactInformation)
    print(resume_parsed.workHistory[0].workPositionOrTitle)
    print(resume_parsed.skills)
    print(resume_parsed)

