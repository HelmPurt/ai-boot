# push-ai-boot.ps1

# Check for .gitignore file
if (Test-Path ".gitignore") {
    Write-Host "✅ .gitignore found — verifying tracking status..."

    $status = git ls-files --error-unmatch .gitignore 2>$null
    if ($status) {
        Write-Host ".gitignore is already tracked in Git."
    } else {
        Write-Host "⚠️ .gitignore not tracked — forcing add..."
        git add -f .gitignore
        Write-Host "🔁 Committing .gitignore now..."
        git commit -m "Force add .gitignore to Git tracking"
    }
} else {
    Write-Host "🚨 No .gitignore file found in this folder!"
}

# Stage all changes
Write-Host "`n📦 Staging all modified files..."
git add .

# Prompt for commit message
$commitMessage = Read-Host "📝 Enter your commit message"

# Commit
Write-Host "📤 Committing: '$commitMessage'"
git commit -m "$commitMessage"

# Push to GitHub
Write-Host "`n🚀 Pushing to GitHub (origin/main)..."
git push

Write-Host "`n✅ All done, Helmuth! Your code is now live on GitHub."
