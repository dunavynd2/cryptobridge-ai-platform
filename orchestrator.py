from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict

from agents.research_agent import research_task
from agents.crypto_agent import recommend_crypto_strategy
from agents.coding_agent import generate_code
from agents.testing_agent import run_tests

class AgentState(TypedDict):
    task: str
    findings: List[Dict]
    recommendation: Dict
    code: str
    test_results: Dict
    status: str

def research_node(state):
    findings = research_task(state['task'])
    return {'findings': findings}

def crypto_node(state):
    rec = recommend_crypto_strategy(state['task'])
    return {'recommendation': rec}

def coding_node(state):
    code = generate_code(state['task'])
    return {'code': code}

def testing_node(state):
    results = run_tests('temp_code.py')  # placeholder
    return {'test_results': results}

def orchestrator_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node('research', research_node)
    workflow.add_node('crypto', crypto_node)
    workflow.add_node('coding', coding_node)
    workflow.add_node('testing', testing_node)
    # Add edges
    workflow.set_entry_point('research')
    workflow.add_edge('research', 'crypto')
    workflow.add_edge('crypto', 'coding')
    workflow.add_edge('coding', 'testing')
    workflow.add_edge('testing', END)
    return workflow.compile()

if __name__ == "__main__":
    print("Starting CryptoBridge AI Orchestrator")
    app = orchestrator_workflow()
    result = app.invoke({"task": "Build PKI management microservice", "status": "started"})
    print(result)