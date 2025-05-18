# TestBenchCliReporter FastAPI Server

Dieses Projekt stellt einen FastAPI-Server bereit, der alle GET-Funktionen aus dem `TestBenchCliReporter` als API-Endpunkte verfügbar macht.
Es nutzt dabei Teile diese Repositories: [testbench-cli-reporter](https://github.com/imbus/testbench-cli-reporter), und integriert diese Funktionen in ein FastAPI MCP: [fastapi_mcp](https://github.com/tadata-org/fastapi_mcp)

## Starten des Servers

1. Starte den Server mit:
   
   ```pwsh
   uv run uvicorn main:app --reload
   ```

2. Die API-Dokumentation ist dann unter [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) erreichbar.

## Configuration

The connection parameters for the TestBench server are now set globally in `main.py`:

```
SERVER_URL = "http://localhost:8080"  # Set your default server URL here
LOGINNAME = "admin"                    # Set your default login name here
PASSWORD = "admin"                    # Set your default password here
```

You do **not** need to provide `server_url`, `loginname` or `password` as query parameters for any endpoint. The API uses these predefined values for all requests.

To change the connection, simply edit the values at the top of `main.py` and restart the server.

## Endpunkte
- `/projects` – Gibt alle Projekte zurück
- `/filters` – Gibt alle Filter zurück
- `/testers/{project_key}` – Gibt alle Tester eines Projekts zurück
- `/members/{project_key}` – Gibt alle Mitglieder eines Projekts zurück
- `/cycle_structure/{cycle_key}` – Gibt die Struktur eines Testzyklus zurück
- `/tov_structure/{tov_key}` – Gibt die Struktur eines TOV zurück
- `/spec_test_cases/{test_case_set_key}/{specification_key}` – Gibt Spezifikationstestfälle zurück
- `/exec_test_cases/{test_case_set_key}/{execution_key}` – Gibt Ausführungstestfälle zurück
- `/test_cases` – Gibt Testfälle (kombiniert) zurück

Weitere Endpunkte können durch Hinzufügen von GET-Methoden in der Datei `main.py` ergänzt werden.

---

> **Hinweis:** Diese API ist nur für die lokale Verwendung vorgesehen und stellt standardmäßig keine Verbindung zu externen Systemen her.
