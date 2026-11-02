Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

WshShell.CurrentDirectory = scriptDir
WshShell.Run """" & scriptDir & "\venv\Scripts\python.exe"" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000", 0, False
WshShell.Run """" & scriptDir & "\venv\Scripts\python.exe"" -m streamlit run frontend/app.py --server.port 8501 --server.headless true", 0, False