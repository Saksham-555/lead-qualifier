param([string]$Base = "main", [string]$Spec = "Review these changes.")
$dir = Join-Path (Get-Location) ".review"
New-Item -ItemType Directory -Force $dir | Out-Null
git diff "$Base...HEAD" | Out-File -Encoding utf8 "$dir\review.diff"
if ((Get-Item "$dir\review.diff").Length -lt 10) { Write-Host "No changes to review."; exit 0 }
claude -p --model opus --allowedTools "Read,Grep,Glob" "Use the code-reviewer subagent. Spec: $Spec. The diff is in .review/review.diff." | Out-File -Encoding utf8 REVIEW.md
Write-Host "Wrote REVIEW.md"
