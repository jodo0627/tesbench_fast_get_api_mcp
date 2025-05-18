# TestBenchCliReporter FastAPI Server

Dieses Projekt stellt einen FastAPI-Server bereit, der alle GET-Funktionen aus einer Klasse `TestBenchCliReporter` als API-Endpunkte verfügbar macht.

## Starten des Servers

1. Stelle sicher, dass FastAPI und Uvicorn installiert sind:
   
   ```pwsh
   pip install fastapi uvicorn
   ```

2. Starte den Server mit:
   
   ```pwsh
   uvicorn main:app --reload
   ```

3. Die API-Dokumentation ist dann unter [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) erreichbar.

## Endpunkte
- `/status` – Gibt den aktuellen Status zurück
- `/info` – Gibt allgemeine Informationen zurück

Weitere Endpunkte können durch Hinzufügen von GET-Methoden in der Klasse `TestBenchCliReporter` ergänzt werden.
