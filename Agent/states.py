# defining the Schema for the desired output
# we have separated this form the graph file because this will help in langgraph states
from typing import Optional

from pydantic import BaseModel , Field , ConfigDict


# for planner Agent
class File(BaseModel):
    path : str = Field(description="""The relative file path including directory and filename (e.g., 'src/components/Header.jsx'). "
                                         "This specifies exactly where the file should be located in the project structure.""")

    purpose: str = Field(description=""" "A clear explanation of what this file is responsible for, such as its functionality, "
                                         "logic, UI role, configuration purpose, or why it is required in the application." """)



class Plan(BaseModel):
    Name : str = Field(description="The official name of the application or project. It should be concise, descriptive, "
                                    "and represent the core purpose or branding of the app.")

    Description : str = Field(description="A short overview (2–3 sentences) explaining what the application does, who it is for, "
                                            "and the main problem it solves or value it provides.")

    TechStack : str = Field(description="A list or description of all technologies, frameworks, languages, libraries, and tools "
                                         "that will be used to build the application (e.g., Python, FastAPI, React, PostgreSQL, Docker).")

    Features :list[str] = Field(description="A detailed list of core functionalities the application must include. "
                                            "Each item should represent one feature, such as authentication, payment integration, "
                                            "real-time notifications, dashboard analytics, etc.")

    Files : list[File] = Field(description="A structured list of all files required for the project. Each entry must specify "
                                         "the file path and clearly describe its purpose so developers understand its role "
                                            "in the system architecture.")




# for Architecture Agent

class Implementation(BaseModel):
    filepath : str = Field(description= "Exact relative path of the file to be created or modified. "
                                        "Must match the file referenced in the project plan.")

    task_description : str = Field(description="A detailed, explicit engineering task to be performed on this file. "
                                                "Must clearly specify what to implement, including the exact variables, "
                                                "functions, classes, and components to define, along with integration details.")


class TaskPlan(BaseModel):
    Implementation_steps : list[Implementation] = Field(description= "Ordered list of implementation tasks required to complete the project. "
                                                                    "Tasks must be dependency-aware, meaning foundational components appear first. "
                                                                    "Each entry must correspond to a specific file and contain a fully detailed task description.")

    model_config = ConfigDict(extra="allow")   # it allows  to add the extra elements





class coder_states(BaseModel):
    task_plan : TaskPlan = Field(description="The plan of the task to be implemented .")
    current_step_index : int = Field(0,description="The index of the current step in the implementation step.")
    current_file_content: Optional[str] = Field(None, description="The content of the file currently being executed or edited .")