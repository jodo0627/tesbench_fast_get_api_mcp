from fastapi import FastAPI, HTTPException  # type: ignore
from typing import List, Dict, Any
from utils.testbench import Connection

from fastapi_mcp import FastApiMCP  # type: ignore

app = FastAPI(
    title="TestBenchCliReporter GET API",
    description="interact with the imbus TestBench API",
    version="0.1.0",
    openapi_url="/openapi.json",
)

# Global configuration for connection parameters
SERVER_URL = "http://localhost:8080"  # Set your default server URL here
LOGINNAME = "admin"  # Set your default login name here
PASSWORD = "admin"  # Set your default password here


def get_connection(verify: bool = False) -> Connection:
    try:
        return Connection(
            server_url=SERVER_URL, loginname=LOGINNAME, password=PASSWORD, verify=verify
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/projects", summary="Get all projects", operation_id="get_all_projects")
def get_all_projects() -> Dict:
    """
    Returns all projects accessible to the user.

    Parameters:
    - None
    
    Returns:
    - Dict: A dictionary containing all projects.
    """
    conn = get_connection()
    return conn.get_all_projects()


@app.get("/filters", summary="Get all filters", operation_id="get_all_filters")
def get_all_filters() -> List[Dict]:
    """
    Returns all available filters.

    Parameters:
    - None
    
    Returns:
    - List[Dict]: A list of dictionaries with filter information.
    """
    conn = get_connection()
    return conn.get_all_filters()


@app.get(
    "/testers/{project_key}",
    summary="Get all testers of a project",
    operation_id="get_all_testers_of_project",
)
def get_all_testers_of_project(project_key: str) -> List[Dict]:
    """
    Returns all testers of a specific project.

    Parameters:
    - project_key (str): The key of the project.
    
    Returns:
    - List[Dict]: A list of dictionaries with tester information.
    """
    conn = get_connection()
    return conn.get_all_testers_of_project(project_key)


@app.get(
    "/members/{project_key}",
    summary="Get all members of a project",
    operation_id="get_all_members_of_project",
)
def get_all_members_of_project(project_key: str) -> List[Dict]:
    """
    Returns all members of a specific project.

    Parameters:
    - project_key (str): The key of the project.
    
    Returns:
    - List[Dict]: A list of dictionaries with member information.
    """
    conn = get_connection()
    return conn.get_all_members_of_project(project_key)


@app.get(
    "/cycle_structure/{cycle_key}",
    summary="Get test cycle structure",
    operation_id="get_test_cycle_structure",
)
def get_test_cycle_structure(cycle_key: str) -> List[Dict]:
    """
    Returns the structure of a test cycle.

    Parameters:
    - cycle_key (str): The key of the test cycle.
    
    Returns:
    - List[Dict]: A list of dictionaries with structure information.
    """
    conn = get_connection()
    return conn.get_test_cycle_structure(cycle_key)


@app.get(
    "/tov_structure/{tov_key}",
    summary="Get TOV structure",
    operation_id="get_tov_structure",
)
def get_tov_structure(tov_key: str) -> List[Dict]:
    """
    Returns the structure of a TOV (Test Object Directory).

    Parameters:
    - tov_key (str): The key of the TOV.
    
    Returns:
    - List[Dict]: A list of dictionaries with TOV structure information.
    """
    conn = get_connection()
    return conn.get_tov_structure(tov_key)


@app.get(
    "/spec_test_cases/{test_case_set_key}/{specification_key}",
    summary="Get specification test cases",
    operation_id="get_spec_test_cases",
)
def get_spec_test_cases(test_case_set_key: str, specification_key: str) -> List[Dict]:
    """
    Returns all specification test cases for a given test case set and specification.

    Parameters:
    - test_case_set_key (str): The key of the test case set.
    - specification_key (str): The key of the specification.
    
    Returns:
    - List[Dict]: A list of dictionaries with specification test cases.
    """
    conn = get_connection()
    return conn.get_spec_test_cases(test_case_set_key, specification_key)


@app.get(
    "/exec_test_cases/{test_case_set_key}/{execution_key}",
    summary="Get execution test cases",
    operation_id="get_exec_test_cases",
)
def get_exec_test_cases(test_case_set_key: str, execution_key: str) -> List[Dict]:
    """
    Returns all execution test cases for a given test case set and execution.

    Parameters:
    - test_case_set_key (str): The key of the test case set.
    - execution_key (str): The key of the execution.
    
    Returns:
    - List[Dict]: A list of dictionaries with execution test cases.
    """
    conn = get_connection()
    return conn.get_exec_test_cases(test_case_set_key, execution_key)


@app.post(
    "/test_cases", summary="Get test cases (combined)", operation_id="get_test_cases"
)
def get_test_cases(test_case_set_structure: Dict[str, Any]) -> Dict[str, Dict]:
    """
    Returns test cases based on a provided test case set structure.

    Parameters:
    - test_case_set_structure (Dict[str, Any]): The structure of the test case set.
    
    Returns:
    - Dict[str, Dict]: A dictionary with test case data.
    """
    conn = get_connection()
    return conn.get_test_cases(test_case_set_structure)


mcp = FastApiMCP(
    app,
    name="TestBench GET MCP",
    describe_all_responses=True,
    describe_full_response_schema=True,
)

# Mount the MCP server directly to the FastAPI app
mcp.mount()
