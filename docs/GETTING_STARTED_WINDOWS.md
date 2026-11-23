# Windows / PowerShell quick start

Assumes Python 3.11+ and Git installed. If you received the project as a zip:

```powershell
Expand-Archive -LiteralPath "$HOME\Downloads\Samanvaya-v0.1.zip" -DestinationPath "$HOME\Desktop" -Force
Set-Location "$HOME\Desktop\Samanvaya"
py -m pip install -e .
py -m unittest discover -s tests -v
py -m samanvaya demo --audit .\local-demo.jsonl
py -m samanvaya verify-audit .\local-demo.jsonl
py examples\collective_demo.py
```

## Publishing a new GitHub repository

Create a **new empty** GitHub repository named `Samanvaya` under your account (`Mircus`). Do **not** tick the boxes for an initial README or license; both are already in this package.

Then from PowerShell:

```powershell
Set-Location "$HOME\Desktop\Samanvaya"
git init
git branch -M main
git add .
git commit -m "Samanvaya v0.1: constitutional kernel and HUAP salvage baseline"
git remote add origin https://github.com/Mircus/Samanvaya.git
git push -u origin main
```

GitHub may request browser authentication or credentials. If Git refuses to commit because your identity is missing, configure your own Git `user.name` and `user.email` (do not paste credentials into chat). The `.gitignore` excludes runtime JSONL logs and local environments.

## What to give Claude / Codex

Point them to your new repository and tell them to start with `docs/HANDOFF_FOR_CLAUDE_CODEX.md`, `docs/SECURITY.md`, and `docs/adr/` before changing code. Ask for a focused v0.2 P0 PR with tests; do not let a large architecture rewrite obscure the trust-boundary work.
