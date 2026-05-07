@echo off
echo ============================================
echo   LegalAI - Push to GitHub
echo ============================================
echo.

set /p GITHUB_URL="Paste your GitHub repo URL (e.g. https://github.com/username/legalai.git): "
set /p GIT_NAME="Your name (for Git commits): "
set /p GIT_EMAIL="Your email (same as GitHub): "

echo.
echo Setting up Git...
git config --global user.name "%GIT_NAME%"
git config --global user.email "%GIT_EMAIL%"

echo Initializing repository...
git init

echo Adding all files...
git add .

echo Creating first commit...
git commit -m "Initial commit - LegalAI full stack app"

echo Setting main branch...
git branch -M main

echo Adding remote origin...
git remote add origin %GITHUB_URL%

echo Pushing to GitHub...
git push -u origin main

echo.
echo ============================================
echo   SUCCESS! Code pushed to GitHub.
echo   Now follow the deployment steps in README.
echo ============================================
pause
