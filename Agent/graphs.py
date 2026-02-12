from langchain_classic.agents import create_react_agent
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph , START , END
from typing import TypedDict
from Agent.prompts import *
from Agent.states import *
from Agent.tools import *

## Model
token = os.getenv("GROQ_API_TOKEN")
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3
)


# Create a state
class State(TypedDict):
    user_prompt: str
    planner_output_response: Plan | None
    task_plan: dict
    coder_state : dict


# Defining the planner Agent
def planner_agent(state:State):
    users_prompt = planner_prompt(state["user_prompt"])
    resp = llm.with_structured_output(Plan).invoke(users_prompt)
    return {"planner_output_response":resp}

def architecture_agent(state:State):
    plan= state["planner_output_response"]
    resp = llm.with_structured_output(TaskPlan).invoke(architecture_prompt(plan))
    if resp is None:
        raise ValueError("Architect did not return a valid response")

    resp.planner_output_response = plan                     # we can do this because we use Config_dict , plan is the input
    return {"task_plan":resp}



def coder_agent(state:State):
    coder_state = state.get('coder_state')
    if coder_state is None:
        coder_state = coder_states(task_plan = state['task_plan'],current_step_index=0)

    steps = coder_state.task_plan.Implementation_steps

    if coder_state.current_step_index >= len(steps):
        return {"coder_state" : coder_state , "status":"DONE"}


    current_task = steps[coder_state.current_step_index]
    existing_content = read_file.run(current_task.filepath)
    user_prompt= (
        f"Task:{current_task.task_description}\n"
        f"File:{current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n"
        "use write_file(path,content) to save your changes  "
    )
    system_prompt =coder_prompt()
    coder_tools = [read_file,write_file,list_files,get_current_directory]
    llm_with_tool = llm.bind_tools(coder_tools)                                        # WITHOUT THIS IT WILL RAISE THE TOOL CALL ERROR
    react_agent = create_react_agent(llm_with_tool, coder_tools)
    react_agent.invoke({"messages": [{"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}]})

    coder_state.current_step_index += 1

    return {"coder_state":coder_state}



#creating a graph
builder = StateGraph(State)

# adding a node to the tree
builder.add_node("planner_node",planner_agent)
builder.add_node("architecture_node",architecture_agent)
builder.add_node("coder_agent",coder_agent)

# adding edges to the tree
builder.add_edge(START,"planner_node")
builder.add_edge("planner_node","architecture_node")
builder.add_edge("architecture_node","coder_agent")

builder.add_conditional_edges("coder_agent",
                              lambda s : "END" if s.get("status")== "DONE" else "coder_agent",
                              {"END":END , "coder_agent":"coder_agent"} )

builder.set_entry_point("planner_node")

graph = builder.compile()


# creating a main function to call the output

if __name__ == "__main__":
    user_prompt = "Create a simple calculater web application"

    result = graph.invoke({"user_prompt":user_prompt},
                          {"recursion_limit":100})                               # it is used to stop the recurssion , sometimes model goes in infinite loop , which will cost more money is it is not being stopped
    print(result)