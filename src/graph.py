import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


# 1. Define the State - This flows through the langgraph workflow
class ClearanceState(TypedDict):
    proposed_name: str
    is_viable: bool
    # 'Annotated' with 'operator.add' tells LangGraph to append to this list
    # rather than overwriting it when a node returns new blockers.
    blockers: Annotated[list[str], operator.add]
    risk_score: int


# 2. The Nodes (With explicit print statements to track execution)
def dns_check_node(state: ClearanceState):
    print(f"\n[Node] Running DNS Check for: '{state['proposed_name']}'")

    # Mock logic: Pretend "Schema Flow" has its domain taken
    if "schema flow" in state["proposed_name"].lower():
        print("  ❌ DNS Failed! Short-circuiting...")
        return {"is_viable": False, "blockers": [".com is already actively hosted."]}

    print("  ✅ DNS Passed!")
    return {"is_viable": True}


def companies_house_node(state: ClearanceState):
    print(f"[Node] Running Companies House Check for: '{state['proposed_name']}'")

    # Mock logic: Pretend "Search Flow" triggers a corporate clash
    if "search flow" in state["proposed_name"].lower():
        print("  ❌ Companies House Failed! Short-circuiting...")
        return {
            "is_viable": False,
            "blockers": ["Exact match found on Companies House register."],
        }

    print("  ✅ Companies House Passed!")
    return {"is_viable": True}


# 3. THE ROUTER: This function decides the path
def check_viability(state: ClearanceState) -> str:
    """
    Looks at the state. If it's viable, we return 'continue'.
    If a node set is_viable to False, we return 'stop'.
    """
    if state["is_viable"]:
        return "continue"
    else:
        return "stop"


# 4. Build the Graph
workflow = StateGraph(ClearanceState)

# Add our nodes to the graph
workflow.add_node("dns_check", dns_check_node)
workflow.add_node("companies_house", companies_house_node)

# Define the flow: START -> dns_check -> companies_house -> END
workflow.add_edge(START, "dns_check")

# Step B: The Short Circuit!
# After DNS, use the router to decide if we hit Companies House or END.
workflow.add_conditional_edges(
    "dns_check",  # Node the edge starts from
    check_viability,  # The routing function to evaluate
    {  # Map the router's string output to actual nodes
        "continue": "companies_house",
        "stop": END,
    },
)

workflow.add_edge("companies_house", END)

# Compile it into an executable application
app = workflow.compile()

# Test 1: A clean name
initial_state = {
    "proposed_name": "Search Flow",
    "is_viable": True,
    "blockers": [],
    "risk_score": 0,
}

print("Testing VeloSeek Analytics:")
result = app.invoke(
    {
        "proposed_name": "VeloSeek Analytics",
        "is_viable": True,
        "blockers": [],
        "risk_score": 0,
    }
)

print("Final State:", result)
