$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:Path = "$repoRoot\google-cloud-sdk\bin;$repoRoot\venv\Scripts;$env:Path"
Set-Location $repoRoot

Write-Host "Google Cloud CLI and ADK are ready."
Write-Host 'Use "gcloud -h" or "adk -h" to list commands.'
