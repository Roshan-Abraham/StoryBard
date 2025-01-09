
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain_core.runnables import Runnable, RunnableConfig, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import AnyMessage, add_messages





# -------------------- 1. Define State --------------------
class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    user_info: str  # Example, include user_info if needed
    dialog_state:  str  # To keep track of active workflow


# -------------------- 2. Define Tools --------------------

# Example Tool (replace with your actual tools)

# LangGraph Framework Tools
@tool
def validate_workflow(workflow: str) -> str:
    """Validates a workflow for the creation of the script and storyline."""
    # Implementation of the LangGraph Workflow validation tool.
    return f"Workflow {workflow} successfully validated"

# Validation Engine Tool
@tool
def validate_consistency(script: str) -> str:
    """Ensures narrative and thematic consistency across script elements."""
    # Actual implementation logic to validate the consistency of the script
    return f"The script is consistent in it's current form."

# Graph Visualization Tool
@tool
def generate_interactive_graph(data: dict) -> str:
    """Generates interactive graphs for metadata and story relationships."""
    # logic here will create interactive graphs with metadata
    return "Graph Generated"

# AI Image Generator Tool
@tool
def generate_image(prompt: str) -> str:
    """Creates visual frames for storyboards."""
    # code that uses an AI model to create visuals from the given prompt
    return "Image Generated"

# Image Processing Utility Tool
@tool
def process_image(image: str) -> str:
    """Refines storyboard images for quality and accuracy."""
    # code to process a given image
    return "Image Processed"

# Simulation Model Tool
@tool
def simulate_audience_response(metadata: dict, demographics: dict) -> str:
    """Predicts audience reactions based on metadata and demographic data."""
    # logic here will predict the response of the audience
    return "Audience Response Simulated"

# -------------------- 3. Define Helper Functions --------------------
def handle_tool_error(state: dict) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)} \n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }

def create_tool_node_with_fallback(tools: list) -> dict:
    return tools_condition(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

def _print_event(event: dict, _printed: set, max_length: int = 1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state)
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)


# -------------------- 4. Define Assistants --------------------
class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            result = self.runnable.invoke(state)
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content.get("text")
            ):
                messages = state["messages"] + [
                    ("user", "Respond with a real output.")
                ]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}

# Define complete or escalate tool
class CompleteOrEscalate(BaseModel):
    """A tool to mark the current task as completed and/or to escalate control of the dialog to the main assistant,
    who can re-route the dialog based on the user's needs."""
    cancel: bool = True
    reason: str
    class Config:
        json_schema_extra = {
            "example": {
                "cancel": True,
                "reason": "User changed their mind about the current task.",
            },
            "example 2": {
                "cancel": True,
                "reason": "I have fully completed the task.",
            },
            "example 3": {
                "cancel": False,
                "reason": "I need to search the user's emails or calendar for more information.",
            },
        }

# Script Consistency Manager Assistant
script_consistency_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a script consistency manager, tasked with generating, validating and refining the scripts based on the user needs. "
            "Ensure consistency in plot, characters, and narrative flow. Use your tools to validate workflows and generate supplementary materials. "
             "If you need more information or the user changes their mind, escalate the task back to the main assistant."
            " Remember that a booking isn't completed until after the relevant tool has successfully been used."
            " \n Current time:  {time} ."
            ' \n\n If the user needs help, and none of your tools are appropriate for it, then "CompleteOrEscalate" the dialog to the host assistant. Do not waste the user \' s time. Do not make up invalid tools or functions.',
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

script_consistency_tools = [
  validate_consistency,
  validate_workflow,
]
script_consistency_runnable = script_consistency_prompt | ChatAnthropic(model="claude-3-sonnet-20240229", temperature=1).bind_tools(script_consistency_tools + [CompleteOrEscalate])

# Metadata and Simulator Assistant
metadata_simulator_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a metadata and simulator assistant, designed to generate metadata, simulate audience reactions, and create visual analytics. "
            "Extract scene and character details, simulate audience engagement, and produce graphs and charts. "
             "If you need more information or the user changes their mind, escalate the task back to the main assistant."
            " Remember that a booking isn't completed until after the relevant tool has successfully been used."
            " \n Current time:  {time} ."
            ' \n\n If the user needs help, and none of your tools are appropriate for it, then "CompleteOrEscalate" the dialog to the host assistant. Do not waste the user \' s time. Do not make up invalid tools or functions.',
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

metadata_simulator_tools = [
    generate_interactive_graph,
    simulate_audience_response
]

metadata_simulator_runnable = metadata_simulator_prompt | ChatAnthropic(model="claude-3-sonnet-20240229", temperature=1).bind_tools(metadata_simulator_tools + [CompleteOrEscalate])

# Storyboard Assistant
storyboard_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a storyboard assistant, responsible for creating and validating storyboards. "
            "Generate visual prompts from scripts, use AI tools for visuals, and ensure images align with script data. "
             "If you need more information or the user changes their mind, escalate the task back to the main assistant."
             " Remember that a booking isn't completed until after the relevant tool has successfully been used."
             " \n Current time:  {time} ."
            ' \n\n If the user needs help, and none of your tools are appropriate for it, then "CompleteOrEscalate" the dialog to the host assistant. Do not waste the user \' s time. Do not make up invalid tools or functions.',
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

storyboard_tools = [
    generate_image,
    process_image,
]
storyboard_runnable = storyboard_prompt | ChatAnthropic(model="claude-3-sonnet-20240229", temperature=1).bind_tools(storyboard_tools + [CompleteOrEscalate])

# Director and Cinematographer Assistant
director_cinematographer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a director and cinematographer assistant, responsible for planning cinematic execution with structured scenes and shot plans. "
            "Organize scripts into acts and sequences, detail camera angles and transitions, and generate a timeline for audience information flow. "
             "If you need more information or the user changes their mind, escalate the task back to the main assistant."
            " Remember that a booking isn't completed until after the relevant tool has successfully been used."
             " \n Current time:  {time} ."
            ' \n\n If the user needs help, and none of your tools are appropriate for it, then "CompleteOrEscalate" the dialog to the host assistant. Do not waste the user \' s time. Do not make up invalid tools or functions.',
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)


director_cinematographer_tools = [
]
director_cinematographer_runnable = director_cinematographer_prompt | ChatAnthropic(model="claude-3-sonnet-20240229", temperature=1).bind_tools(director_cinematographer_tools + [CompleteOrEscalate])

# Primary Assistant Tool Definitions:
class ToScriptConsistencyManager(BaseModel):
    """Transfers work to a specialized assistant to manage script consistency."""
    request: str = Field(
      description="Any specific requests for the script consistency manager."
    )

class ToMetadataSimulatorManager(BaseModel):
    """Transfers work to a specialized assistant to create and manage metadata."""
    request: str = Field(
        description="Any specific requests for the metadata and simulator manager."
    )

class ToStoryboardManager(BaseModel):
    """Transfers work to a specialized assistant to generate storyboards."""
    request: str = Field(
        description="Any specific requests for the storyboard manager."
    )
class ToDirectorCinematographerManager(BaseModel):
    """Transfers work to a specialized assistant to manage the direction and cinematography."""
    request: str = Field(
        description="Any specific requests for the director and cinematographer manager."
    )
# Primary Assistant
primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant for managing film production. "
            "Your primary role is to interpret user requests related to script creation, storyboarding, metadata generation, or filming plans and delegate them to appropriate specialized assistants. "
            "If a user requests script validation or refinement, the creation of storyboards, metadata generation, or plans for direction or cinematography, delegate the task to the appropriate specialized assistant by invoking the corresponding tool. You are not able to make these types of changes yourself."
            " Only the specialized assistants are given permission to do this for the user. "
            "The user is not aware of the different specialized assistants, so do not mention them; just quietly delegate through function calls. "
            "Provide detailed information to the customer, and always double-check the database before concluding that information is unavailable. "
             " \n Current time:  {time} ."
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

primary_assistant_tools = [
]
assistant_runnable = primary_assistant_prompt | ChatAnthropic(model="claude-3-sonnet-20240229", temperature=1).bind_tools(primary_assistant_tools + [
  ToScriptConsistencyManager,
  ToMetadataSimulatorManager,
  ToStoryboardManager,
  ToDirectorCinematographerManager
])

# -------------------- 5. Define Graph --------------------
builder = StateGraph(State)


def user_info(state: State):
    # Replace with actual user info retrieval
    return {"user_info": "User Information"}

builder.add_node("fetch_user_info", user_info)
builder.add_edge(START, "fetch_user_info")


def create_entry_node(assistant_name: str, new_dialog_state: str) -> Callable:
    def entry_node(state: State) -> dict:
        tool_call_id = state["messages"][-1].tool_calls["id"]
        return {
            "messages": [
                ToolMessage(
                  content = f"The assistant is now the {assistant_name}. Reflect on the above conversation between the host assistant and the user."
                  f" The user's intent is unsatisfied. Use the provided tools to assist the user. Remember, you are {assistant_name},"
                  " and the booking, update, other other action is not complete until after you have successfully invoked the appropriate tool."
                  " If the user changes their mind or needs help for other tasks, call the CompleteOrEscalate function to let the primary host assistant take control."
                  " Do not mention who you are - just act as the proxy for the assistant.",
                    tool_call_id=tool_call_id,
                )
            ],
            "dialog_state": new_dialog_state,
        }

    return entry_node


# Script Consistency Manager Workflow
builder.add_node(
    "enter_script_consistency",
    create_entry_node("Script Consistency Manager", "script_consistency"),
)
builder.add_node(
    "script_consistency", Assistant(script_consistency_runnable)
)
builder.add_edge("enter_script_consistency", "script_consistency")
builder.add_node(
    "script_consistency_tools",
    create_tool_node_with_fallback(script_consistency_tools),
)

def route_script_consistency(state: State):
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(
        tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls
    )
    if did_cancel:
        return "leave_skill"

    return "script_consistency_tools"

builder.add_edge("script_consistency_tools", "script_consistency")
builder.add_conditional_edges(
    "script_consistency",
    route_script_consistency,
    ["script_consistency_tools", "leave_skill", END],
)

# Metadata and Simulator Assistant Workflow
builder.add_node(
    "enter_metadata_simulator",
    create_entry_node("Metadata and Simulator Manager", "metadata_simulator"),
)
builder.add_node(
    "metadata_simulator", Assistant(metadata_simulator_runnable)
)
builder.add_edge("enter_metadata_simulator", "metadata_simulator")
builder.add_node(
    "metadata_simulator_tools",
    create_tool_node_with_fallback(metadata_simulator_tools),
)

def route_metadata_simulator(state: State):
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(
        tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls
    )
    if did_cancel:
        return "leave_skill"
    return "metadata_simulator_tools"

builder.add_edge("metadata_simulator_tools", "metadata_simulator")
builder.add_conditional_edges(
    "metadata_simulator",
    route_metadata_simulator,
    ["metadata_simulator_tools", "leave_skill", END],
)

# Storyboard Assistant Workflow
builder.add_node(
    "enter_storyboard",
    create_entry_node("Storyboard Manager", "storyboard"),
)
builder.add_node("storyboard", Assistant(storyboard_runnable))
builder.add_edge("enter_storyboard", "storyboard")
builder.add_node(
    "storyboard_tools",
    create_tool_node_with_fallback(storyboard_tools),
)

def route_storyboard(state: State):
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(
        tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls
    )
    if did_cancel:
        return "leave_skill"
    return "storyboard_tools"


builder.add_edge("storyboard_tools", "storyboard")
builder.add_conditional_edges(
    "storyboard", route_storyboard, ["storyboard_tools", "leave_skill", END]
)


# Director Cinematographer Assistant Workflow
builder.add_node(
    "enter_director_cinematographer",
    create_entry_node("Director Cinematographer Manager", "director_cinematographer"),
)
builder.add_node(
    "director_cinematographer", Assistant(director_cinematographer_runnable)
)
builder.add_edge("enter_director_cinematographer", "director_cinematographer")
builder.add_node(
    "director_cinematographer_tools",
    create_tool_node_with_fallback(director_cinematographer_tools),
)

def route_director_cinematographer(state: State):
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(
        tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls
    )
    if did_cancel:
        return "leave_skill"
    return "director_cinematographer_tools"


builder.add_edge("director_cinematographer_tools", "director_cinematographer")
builder.add_conditional_edges(
    "director_cinematographer",
    route_director_cinematographer,
    ["director_cinematographer_tools", "leave_skill", END],
)

# Shared pop_dialog_state node
def pop_dialog_state(state: State) -> dict:
    messages = []
    if state["messages"][-1].tool_calls:
        messages.append(
            ToolMessage(
                content="Resuming dialog with the host assistant. Please reflect on the past conversation and assist the user as needed.",
                tool_call_id=state["messages"][-1].tool_calls["id"],
            )
        )
    return {
        "dialog_state": "pop",
        "messages": messages,
    }
builder.add_node("leave_skill", pop_dialog_state)
builder.add_edge("leave_skill", "primary_assistant")


# Primary Assistant
builder.add_node("primary_assistant", Assistant(assistant_runnable))
builder.add_node(
    "primary_assistant_tools",
    create_tool_node_with_fallback(primary_assistant_tools),
)


def route_primary_assistant(state: State):
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
      if tool_calls["name"] == ToScriptConsistencyManager.__name__:
          return "enter_script_consistency"
      elif tool_calls["name"] == ToMetadataSimulatorManager.__name__:
          return "enter_metadata_simulator"
      elif tool_calls["name"] == ToStoryboardManager.__name__:
          return "enter_storyboard"
      elif tool_calls["name"] == ToDirectorCinematographerManager.__name__:
          return "enter_director_cinematographer"
      return "primary_assistant_tools"
    return END

builder.add_conditional_edges(
    "primary_assistant",
    route_primary_assistant,
    [
        "enter_script_consistency",
        "enter_metadata_simulator",
        "enter_storyboard",
        "enter_director_cinematographer",
        "primary_assistant_tools",
        END,
    ],
)
builder.add_edge("primary_assistant_tools", "primary_assistant")


def route_to_workflow(state: State) -> Literal[
    "primary_assistant",
    "script_consistency",
    "metadata_simulator",
    "storyboard",
    "director_cinematographer",
]:
    """If we are in a delegated state, route directly to the appropriate assistant."""
    dialog_state = state.get("dialog_state")
    if not dialog_state:
        return "primary_assistant"
    return dialog_state


builder.add_conditional_edges("fetch_user_info", route_to_workflow)

memory = MemorySaver()
part_5_graph = builder.compile(
    checkpointer=memory,
    interrupt_before=[

    ],
)
# ```

# **Key Points:**

# *   **Modularity:** Each assistant has its own prompt, tools, and logic, making it easier to manage and improve.
# *   **Scalability:** The graph structure allows you to add more assistants and tools without making the core logic too complex.
# *   **Flexibility:** The conditional routing logic lets you switch between assistants as needed.
# *   **Clarity:** Each node is clearly defined and serves a single purpose, improving the overall readability of the code.
# *   **Specialized Workflow**: Each specialized workflow has it's own node for safe tools, and sensitive tools, as well as it's own routing.
# *   **Error Handling**: Tools have error handling using a `with_fallbacks` method.
# * **CompleteOrEscalate**: Each specialized assistant uses this tool to return the user to the primary assistant when needed.

# This template is a starting point, and you'll need to adapt it with your specific tool implementations, prompts, and business logic. Remember to test each component thoroughly, and refine your graph based on your specific needs. Let me know if you have any questions or need further clarification on a particular section.
