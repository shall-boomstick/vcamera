#!/bin/bash
# Script to set up GitHub remote and push

REPO_NAME="vcamera"
GITHUB_USER="shall-boomstick"
BRANCH="001-virtual-camera-server"

echo "Setting up GitHub remote for $REPO_NAME..."

# Add remote
git remote add origin git@github.com:${GITHUB_USER}/${REPO_NAME}.git 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Remote added successfully"
else
    echo "Remote might already exist, checking..."
    git remote set-url origin git@github.com:${GITHUB_USER}/${REPO_NAME}.git
    echo "✓ Remote URL updated"
fi

# Check if remote repo exists
echo "Checking if repository exists on GitHub..."
if curl -s https://api.github.com/repos/${GITHUB_USER}/${REPO_NAME} | grep -q '"name"'; then
    echo "✓ Repository exists on GitHub"
    echo ""
    echo "Pushing to GitHub..."
    git push -u origin ${BRANCH}
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Successfully pushed to GitHub!"
        echo "Repository: https://github.com/${GITHUB_USER}/${REPO_NAME}"
    else
        echo ""
        echo "✗ Push failed. Make sure the repository exists on GitHub."
        echo "Create it at: https://github.com/new"
        echo "Repository name: ${REPO_NAME}"
        echo "Then run this script again."
    fi
else
    echo ""
    echo "⚠ Repository doesn't exist on GitHub yet."
    echo ""
    echo "To create it:"
    echo "1. Go to: https://github.com/new"
    echo "2. Repository name: ${REPO_NAME}"
    echo "3. Description: Virtual Camera Server"
    echo "4. Make it Public or Private (your choice)"
    echo "5. DO NOT initialize with README, .gitignore, or license"
    echo "6. Click 'Create repository'"
    echo ""
    echo "Then run this script again:"
    echo "  bash setup_remote.sh"
    echo ""
    echo "Or manually run:"
    echo "  git push -u origin ${BRANCH}"
fi

