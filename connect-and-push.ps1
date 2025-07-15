# connect-and-push.ps1

$remoteUrl = "https://github.com/HelmPurt/ai-boot.git"

Write-Host "🌐 Adding remote origin..."
git remote add origin $remoteUrl

Write-Host "📌 Setting branch name to 'main'..."
git branch -M main

Write-Host "🚀 Pushing to GitHub..."
git push -u origin main

Write-Host "`n✅ All done! Your local project is now live on GitHub:"
Write-Host $remoteUrl
