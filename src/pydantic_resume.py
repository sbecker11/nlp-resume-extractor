import json
from devtools import debug
from typing import List, Optional
from pydantic import BaseModel
from pydantic import ValidationError

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
    duration: Optional[Duration] = None
    workResponsibilitiesAccomplishments: List[str]


class EducationHistoryItem(BaseModel):
    institution: str
    degree: str
    majors: Optional[List[str]] = None
    minors: Optional[List[str]] = None
    gradePointAverage: Optional[str] = None
    duration: Optional[Duration] = None


class PydanticResume(BaseModel):
    contactInformation: ContactInformation
    workHistory: List[WorkHistoryItem]
    educationHistory: List[EducationHistoryItem]
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    publications: Optional[List[str]] = None
    patents: Optional[List[str]] = None
    websites: Optional[List[str]] = None


if __name__ == "__main__":
    
    pydantic_json_schema = PydanticResume.model_json_schema()
    print("Pydantic JSON schema:")
    print(json.dumps(pydantic_json_schema, indent=2))
    exit()

    # # Load the JSON data
    # with open('test-data-object.json', 'r') as data_file:
    #     data = json.load(data_file)

    # # Extract the json resume data
    # resume_obj = data.get("resume")
    
    # # create the PydanticResume object from the json resume data
    # try:
    #     pydantic_resume = PydanticResume(**resume_obj)
    #     print("resume_obj is valid and the PydanticResume object has been created.")
        
    #     print("PydanticResume object:")
    #     debug(pydantic_resume)
        
    #     print("resume_obj:")
    #     print(json.dumps(resume_obj, indent=2))
        
    # except ValidationError as e:
    #     print("JSON data is invalid against the Pydantic model.")
    #     print(e.json())
    #     exit(1)
    
    

        
    # """
    # # compare JSON-serialized values
    # # Convert PydanticResume object to string and replace characters
    # pydantic_resume_str = str(pydantic_resume).\
    #     replace("'", "").replace("=", ":")
    
    # # Convert resume_obj object to string and replace characters
    # json_resume_str = json.dumps(resume_obj).\
    #     replace('"', "").replace(": ", ":").\
    #         replace("{","(").replace("}",")")

    # if pydantic_resume_str == json_resume_str:
    #     print("The PydanticResume str matches the JSON Resume str")
    # else:
    #     print("The PydanticResume str does not match the resume_obj str")
    #     print("PydanticResume str:")
    #     print(pydantic_resume_str)
    #     print("resume_obj str:")
    #     print(json_resume_str)

    #     PydanticResume str:
    #     contactInformation:ContactInformation(firstName:Joe, lastName:Jones, email:joe@jones.com, phone:555-555-5555, address:123 Main St, city:San Francisco, state:CA, zipCode:94105, country:USA)  workHistory:[ WorkHistoryItem(workPositionOrTitle:clerk, workForCompanyName:company1, workLocationOrRemote:remote, duration:Duration(start:2019-01-01, end:2020-01-01), workResponsibilitiesAccomplishments:[accomplishment1, accomplishment2]), WorkHistoryItem(workPositionOrTitle:manager, workForCompanyName:company2, workLocationOrRemote:remote, duration:Duration(start:2019-01-01, end:2020-01-01), workResponsibilitiesAccomplishments:[accomplishment3, accomplishment4])]  educationHistory:[EducationHistoryItem(institution:school1, degree:BS, majors:[Computer Science], minors:[Math], gradePointAverage:3.5, duration:Duration(start:2015-01-01, end:2019-01-01)), EducationHistoryItem(institution:school2, degree:MS, majors:[Data Science], minors:[Statistics], gradePointAverage:3.8, duration:Duration(start:2019-01-01, end:2021-01-01))]  skills:[skill1, skill2, skill3] certifications:[cert1, cert2, cert3] publications:None patents:None websites:[site1, site2]
    #     resume_obj str:
    #     (contactInformation:                  (firstName:Joe, lastName:Jones, email:joe@jones.com, phone:555-555-5555, address:123 Main St, city:San Francisco, state:CA, zipCode:94105, country:USA), workHistory:[                (workPositionOrTitle:clerk, workForCompanyName:company1, workLocationOrRemote:remote, duration:        (start:2019-01-01, end:2020-01-01), workResponsibilitiesAccomplishments:[accomplishment1, accomplishment2]),                (workPositionOrTitle:manager, workForCompanyName:company2, workLocationOrRemote:remote, duration:        (start:2019-01-01, end:2020-01-01), workResponsibilitiesAccomplishments:[accomplishment3, accomplishment4])], educationHistory:[                    (institution:school1, degree:BS, majors:[Computer Science], minors:[Math], gradePointAverage:3.5, duration:        (start:2015-01-01, end:2019-01-01)),                     (institution:school2, degree:MS, majors:[Data Science], minors:[Statistics], gradePointAverage:3.8, duration:        (start:2019-01-01, end:2021-01-01))], skills:[skill1, skill2, skill3]                               certifications:[cert1, cert2, cert3],                               websites:[site1, site2] 
    # """