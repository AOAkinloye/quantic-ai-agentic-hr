import json
import os
from mcp.server.fastmcp import FastMCP
from rag_pipeline import retrieve

# Initialize FastMCP server
mcp = FastMCP("HROperationsServer")

MOCK_DATA_DIR = "mock_data"

def load_json(filename: str):
    path = os.path.join(MOCK_DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_json(filename: str, data):
    path = os.path.join(MOCK_DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

@mcp.tool()
def search_policy_documents(query: str, k: int = 3) -> str:
    """Searches HR policy documents (PTO, Remote Work, Benefits, etc.) to answer questions."""
    results = retrieve(query, k)
    if not results:
        return "No relevant policies found."
    
    formatted = []
    for i, res in enumerate(results):
        metadata = res["metadata"]
        header = metadata.get("Header 1", metadata.get("Header 2", "Section"))
        source = metadata.get("source", "Unknown")
        formatted.append(f"[Source: {source}, Section: {header}]\n{res['content']}")
        
    return "\n\n---\n\n".join(formatted)

@mcp.tool()
def lookup_employee_profile(employee_id: str) -> str:
    """Looks up an employee's profile including department, role, manager, and location."""
    employees = load_json("employees.json")
    for emp in employees:
        if emp.get("employee_id") == employee_id:
            return json.dumps(emp, indent=2)
    return f"Employee {employee_id} not found."

@mcp.tool()
def check_pto_balance(employee_id: str) -> str:
    """Checks the accrued and used PTO and sick leave balance for an employee."""
    balances = load_json("pto_balances.json")
    for bal in balances:
        if bal.get("employee_id") == employee_id:
            return json.dumps(bal, indent=2)
    return f"PTO balance for {employee_id} not found."

@mcp.tool()
def lookup_benefits_status(employee_id: str) -> str:
    """Looks up an employee's benefits elections (health, dental, vision, 401k)."""
    benefits = load_json("benefits.json")
    for ben in benefits:
        if ben.get("employee_id") == employee_id:
            return json.dumps(ben, indent=2)
    return f"Benefits data for {employee_id} not found."

@mcp.tool()
def create_mock_hr_ticket(employee_id: str, request_type: str, description: str) -> str:
    """Creates a mock HR ticket for requests like PTO approval, Expense reimbursement, etc."""
    tickets = load_json("tickets.json")
    ticket_id = f"TICKET-{len(tickets) + 1:04d}"
    new_ticket = {
        "ticket_id": ticket_id,
        "employee_id": employee_id,
        "request_type": request_type,
        "description": description,
        "status": "Open"
    }
    tickets.append(new_ticket)
    save_json("tickets.json", tickets)
    return f"Success: HR ticket {ticket_id} created for {employee_id}."

if __name__ == "__main__":
    mcp.run()
