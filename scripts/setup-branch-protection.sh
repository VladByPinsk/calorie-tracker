#!/usr/bin/env bash
# Sets up GitHub branch protection rules using GitHub CLI (gh).
# Prerequisites: brew install gh && gh auth login
set -euo pipefail

REPO='VladByPinsk/calorie-tracker'

echo '==> Setting up branch protection for: main'

gh api \
  --method PUT \
  -H 'Accept: application/vnd.github+json' \
  /repos/${REPO}/branches/main/protection \
  --input - << 'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Test auth-service",
      "Test user-service",
      "Test food-service",
      "Test diary-service",
      "Test ai-service",
      "Test analytics-service",
      "Test notification-service",
      "Test api-gateway",
      "Test Web (React)",
      "Test Mobile (Expo)",
      "Test Infrastructure"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1,
    "require_last_push_approval": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "required_linear_history": true
}
JSON

echo '==> Setting up branch protection for: develop'

gh api \
  --method PUT \
  -H 'Accept: application/vnd.github+json' \
  /repos/${REPO}/branches/develop/protection \
  --input - << 'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Test auth-service",
      "Test user-service",
      "Test food-service",
      "Test diary-service",
      "Test ai-service",
      "Test analytics-service",
      "Test notification-service",
      "Test api-gateway",
      "Test Web (React)",
      "Test Mobile (Expo)"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON

echo '==> Branch protection rules applied.'
