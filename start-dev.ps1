# Starts backend (:8000), job-seeker site (:5173) and recruiter (:5174) in separate windows.
# Uses the devenv conda env for both Python and Node (system Node 22.11 is too old for Vite 7).
$env:Path = "D:\Conda\envs\devenv;D:\Conda\envs\devenv\Scripts;" + $env:Path
$root = $PSScriptRoot

Push-Location "$root\backend"
python manage.py migrate
Pop-Location
if ($LASTEXITCODE -ne 0) { Write-Error "migrate failed - is the peeljobs DB created? See backend\create_db.sql"; exit 1 }

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; python manage.py runserver 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\site'; pnpm dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\recruiter'; pnpm dev"
