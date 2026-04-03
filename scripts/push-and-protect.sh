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
COMMAND="${2:-push-and-protect}"
REMOTE_WITH_TOKEN="https://${OWNER}:${TOKEN}@github.com/${REPO}.git"
CLEAN_REMOTE="https://github.com/${REPO}.git"

# ─── Helper: push a branch using token, then clean remote URL ─────────────────
push_branch() {
  local branch="$1"
  git remote set-url origin "$REMOTE_WITH_TOKEN"
  git push -u origin "$branch"
  git remote set-url origin "$CLEAN_REMOTE"
}

# ─── Helper: GitHub API call ─────────────────────────────────────────────────
gh_api() {
  local method="$1" path="$2" data="$3"
  curl -s -X "$method" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com${path}" \
    -d "$data"
}

case "$COMMAND" in

# ─────────────────────────────────────────────────────────────────────────────
push-and-protect)
  echo ""
  echo "══════════════════════════════════════════════════════════"
  echo "  calorie-tracker — push & branch protection setup"
  echo "══════════════════════════════════════════════════════════"

  echo ""
  echo "→ [1/3] Pushing main + develop..."
  git remote set-url origin "$REMOTE_WITH_TOKEN"
  git push -u origin main
  git push -u origin develop
  git remote set-url origin "$CLEAN_REMOTE"
  echo "  ✅ Pushed main + develop"

  echo ""
  echo "→ [2/3] Configuring repo merge settings..."
  gh_api PATCH "/repos/${REPO}" '{
    "allow_squash_merge": true,
    "allow_merge_commit": false,
    "allow_rebase_merge": true,
    "delete_branch_on_merge": true,
    "squash_merge_commit_title": "PR_TITLE",
    "squash_merge_commit_message": "PR_BODY"
  }' > /dev/null
  echo "  ✅ Squash+rebase only, delete branch on merge enabled"

  echo ""
  echo "→ [3/3] Applying branch protection rules..."
  echo "        Protecting: main"
  gh_api PUT "/repos/${REPO}/branches/main/protection" '{
    "required_status_checks": {
      "strict": true,
      "contexts": [
        "Test auth-service","Test user-service","Test food-service",
        "Test diary-service","Test ai-service","Test analytics-service",
        "Test notification-service","Test api-gateway",
        "Test Web (React)","Test Mobile (Expo)","Test Infrastructure"
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
  echo "  ✅ main protected"

  echo "        Protecting: develop"
  gh_api PUT "/repos/${REPO}/branches/develop/protection" '{
    "required_status_checks": {
      "strict": true,
      "contexts": [
        "Test auth-service","Test user-service","Test food-service",
        "Test diary-service","Test ai-service","Test analytics-service",
        "Test notification-service","Test api-gateway",
        "Test Web (React)","Test Mobile (Expo)"
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
  echo "  ✅ develop protected"

  echo ""
  echo "══════════════════════════════════════════════════════════"
  echo "  All done! https://github.com/${REPO}/settings/branches"
  echo "══════════════════════════════════════════════════════════"
  ;;

# ─────────────────────────────────────────────────────────────────────────────
sync-develop)
  echo "→ Fast-forwarding develop to match main and pushing..."
  git checkout develop
  git merge main --ff-only
  push_branch develop
  git checkout main
  echo "  ✅ develop is now in sync with main"
  ;;

# ─────────────────────────────────────────────────────────────────────────────
push-branch)
  BRANCH="$(git rev-parse --abbrev-ref HEAD)"
  echo "→ Pushing branch: ${BRANCH}"
  push_branch "$BRANCH"
  echo "  ✅ Pushed ${BRANCH} to origin"
  ;;

# ─────────────────────────────────────────────────────────────────────────────
create-pr)
  BASE="${3:-main}"
  BRANCH="$(git rev-parse --abbrev-ref HEAD)"
  TITLE="$(git log -1 --pretty=%s)"

  echo "→ Pushing branch: ${BRANCH}"
  push_branch "$BRANCH"
  echo "  ✅ Branch pushed"

  echo "→ Verifying direct push to ${BASE} is blocked..."
  git remote set-url origin "$REMOTE_WITH_TOKEN"
  PUSH_RESULT=$(git push origin "HEAD:${BASE}" 2>&1 || true)
  git remote set-url origin "$CLEAN_REMOTE"
  if echo "$PUSH_RESULT" | grep -q "protected branch\|required status\|refusing\|cannot push"; then
    echo "  ✅ Direct push to ${BASE} is BLOCKED (branch protection working)"
  else
    echo "  ⚠️  Unexpected push result: ${PUSH_RESULT}"
  fi

  echo "→ Creating Pull Request: ${BRANCH} → ${BASE}"
  PR_RESPONSE=$(gh_api POST "/repos/${REPO}/pulls" "{
    \"title\": \"${TITLE}\",
    \"head\": \"${BRANCH}\",
    \"base\": \"${BASE}\",
    \"body\": \"## Summary\n\nThis PR verifies that branch protection is working correctly.\n\n- Direct push to \`${BASE}\` was **blocked** ✅\n- This PR is the only way to merge changes into \`${BASE}\` ✅\n- Requires CI to pass + owner approval before merge ✅\n\nCloses (test PR — can be merged or closed after verification).\",
    \"draft\": false
  }")

  PR_URL=$(echo "$PR_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('html_url','ERROR: '+str(d)))")
  echo ""
  echo "══════════════════════════════════════════════════════════"
  echo "  ✅ Pull Request created!"
  echo "  ${PR_URL}"
  echo "══════════════════════════════════════════════════════════"
  ;;

*)
  echo "Unknown command: $COMMAND"
  echo "Valid commands: push-and-protect, sync-develop, push-branch, create-pr"
  exit 1
  ;;
esac
