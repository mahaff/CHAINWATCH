@ECHO OFF
CLS
SET "REPO_ROOT=%~dp0"
SET "PATH=%REPO_ROOT%google-cloud-sdk\bin;%REPO_ROOT%venv\Scripts;%PATH%"
cd /d "%REPO_ROOT%"
ECHO Google Cloud CLI and ADK are ready.
ECHO Use "gcloud -h" or "adk -h" to list commands.
ECHO ---
ECHO ON
