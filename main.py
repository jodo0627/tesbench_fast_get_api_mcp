from fastapi import FastAPI, Query, HTTPException  # type: ignore
from typing import List, Dict, Any
from utils.testbench import Connection

app = FastAPI(title="TestBenchCliReporter API", description="Stellt alle GET-Methoden der Connection-Klasse als Endpunkte bereit.", version="1.0.0")

def get_connection(server_url: str, loginname: str, password: str, verify: bool = False) -> Connection:
    try:
        return Connection(server_url=server_url, loginname=loginname, password=password, verify=verify)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/projects", summary="Alle Projekte abrufen")
def get_all_projects(server_url: str = Query(...), loginname: str = Query(...), password: str = Query(...)) -> Dict:
    conn = get_connection(server_url, loginname, password)
    return conn.get_all_projects()

@app.get("/filters", summary="Alle Filter abrufen")
def get_all_filters(server_url: str = Query(...), loginname: str = Query(...), password: str = Query(...)) -> List[Dict]:
    conn = get_connection(server_url, loginname, password)
    return conn.get_all_filters()

@app.get("/testers/{project_key}", summary="Alle Tester eines Projekts abrufen")
def get_all_testers_of_project(project_key: str, server_url: str = Query(...), loginname: str = Query(...), password: str = Query(...)) -> List[Dict]:
    conn = get_connection(server_url, loginname, password)
    return conn.get_all_testers_of_project(project_key)

@app.get("/members/{project_key}", summary="Alle Mitglieder eines Projekts abrufen")
def get_all_members_of_project(project_key: str, server_url: str = Query(...), loginname: str = Query(...), password: str = Query(...)) -> List[Dict]:
    conn = get_connection(server_url, loginname, password)
    return conn.get_all_members_of_project(project_key)

@app.get("/cycle_structure/{cycle_key}", summary="Testzyklus-Struktur abrufen")
def get_test_cycle_structure(cycle_key: str, server_url: str = Query(...), loginname: str = Query(...), password: str = Query(...)) -> List[Dict]:
    conn = get_connection(server_url, loginname, password)
    return conn.get_test_cycle_structure(cycle_key)

@app.get("/tov_structure/{tov_key}", summary="TOV-Struktur abrufen")
def get_tov_structure(tov_key: str, server_url: str = Query(...), loginname: str = Query(...), password: str = Query(...)) -> List[Dict]:
    conn = get_connection(server_url, loginname, password)
    return conn.get_tov_structure(tov_key)

@app.get("/spec_test_cases/{test_case_set_key}/{specification_key}", summary="Spezifikations-Testfälle abrufen")
def get_spec_test_cases(test_case_set_key: str, specification_key: str, server_url: str = Query(...), loginname: str = Query(...), password: str = Query(...)) -> List[Dict]:
    conn = get_connection(server_url, loginname, password)
    return conn.get_spec_test_cases(test_case_set_key, specification_key)

@app.get("/exec_test_cases/{test_case_set_key}/{execution_key}", summary="Ausführungs-Testfälle abrufen")
def get_exec_test_cases(test_case_set_key: str, execution_key: str, server_url: str = Query(...), loginname: str = Query(...), password: str = Query(...)) -> List[Dict]:
    conn = get_connection(server_url, loginname, password)
    return conn.get_exec_test_cases(test_case_set_key, execution_key)

@app.post("/test_cases", summary="Testfälle abrufen (Kombiniert)")
def get_test_cases(test_case_set_structure: Dict[str, Any], server_url: str = Query(...), loginname: str = Query(...), password: str = Query(...)) -> Dict[str, Dict]:
    conn = get_connection(server_url, loginname, password)
    return conn.get_test_cases(test_case_set_structure)
