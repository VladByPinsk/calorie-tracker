#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# push-and-protect.sh
#
# One-shot script: pushes both branches to GitHub and applies branch
# protection rules. Run ONCE from Terminal.app (not from the IDE).
#
# Usage:
#   bash scripts/push-and-protect.sh <YOUR_GITHUB_PAT>
#
# How to get a PAT (30 seconds):
#   1. Open: https://github.com/settings/tokens/new
#   2. Note: calorie-tracker
#   3. Expiration: 90 days
#   4. Scopes: check  repo  AND  workflow
#   5. Click "Generate token" and copy it
#   6. Run: bash scripts/push-and-protect.sh ghp_PASTE_HERE
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO="VladByPinsk/calorie-tracker"
OWNER="VladByPinsk"

# ─── Validate token argument ──────────────────────────────────────────────────
if [[ $# -lt 1 || -z "${1:-}" ]]; then
  echo ""
  echo "Usage: bash scripts/push-and-protect.sh <YOUR_GITHUB_PAT>"
  echo ""
  echo "Get a PAT at: https://github.com/settings/tokens/new"
  echo "Required scopes: repo, workflow"
  exit 1
fi

TOKEN="$1"

echo ""
echo "══════════════════════════════════════════════════════════"
echo "  calorie-tracker — push & branch protection setup"
echo "══════════════════════════════════════════════════════════"

# ─── Step 1: Push main + develop ─────────────────────────────────────────────
echo ""
echo "→ [1/3] Pushing branches to GitHub..."

REMOTE_WITH_TOKEN="https://${OWNER}:${TOKEN}@github.com/${REPO}.git"

git remote set-url origin "$REMOTE_WITH_TOKEN"
git push -u origin main
git push -u origin develop

# Remove token from remote URL immediately after push
git remote set-url origin "https://github.com/${REPO}.git"
echo "  ✅ Pushed main + develop  |  token removed from remote URL"

# ─── Step 2: Apply repo-level settings ───────────────────────────────────────
echo ""
echo "→ [2/3] Configuring repo merge settings..."

curl -s -X PATCH \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/${REPO}" \
  -d '{
    "allow_squash_merge": true,
    "allow_merge_commit": false,
    "allow_rebase_merge": true,
    "delete_branch_on_merge": true,
    "squash_merge_commit_title": "PR_TITLE",
    "squash_merge_commit_message": "PR_BODY"
  }' > /dev/null

echo "  ✅ Squash+rebase only, delete branch on merge enabled"

# ─── Step 3: Branch protection — main ────────────────────────────────────────
echo ""
echo "→ [3/3] Applying branch protection rules..."
echo "        Protecting: main"

curl -s -X PUT \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/${REPO}/branches/main/protection" \
  -d '{
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
    "required_conversation_resolution": true,
    "required_linear_history": true,
    "lock_branch": false
  }' > /dev/null

echo "  ✅ main: PRs required, 1 approval (owner), all CI must pass, no force push"

# ─── Branch protection — develop ─────────────────────────────────────────────
echo "        Protecting: develop"

curl -s -X PUT \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/${REPO}/branches/develop/protection" \
  -d '{
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
      "required_approving_review_count": 1,
      "require_last_push_approval": false
    },
    "restrictions": null,
    "allow_force_pushes": false,
    "allow_deletions": false,
    "required_conversation_resolution": true,
    "required_linear_history": false
  }' > /dev/null

echo "  ✅ develop: PRs required, 1 approval, CI must pass"

# ─── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════════"
echo "  All done! Verify branch protection at:"
echo "  https://github.com/${REPO}/settings/branches"
echo "══════════════════════════════════════════════════════════"
echo ""

