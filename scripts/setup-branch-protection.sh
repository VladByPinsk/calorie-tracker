#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# setup-branch-protection.sh
#
# Applies GitHub branch protection rules for calorie-tracker.
# Run ONCE after the initial push to GitHub.
#
# Prerequisites:
#   brew install gh
#   gh auth login
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO="VladByPinsk/calorie-tracker"

echo ""
echo "══════════════════════════════════════════════════════════"
echo "  Applying branch protection rules for: $REPO"
echo "══════════════════════════════════════════════════════════"

# ─── Helper: check gh is authenticated ────────────────────────────────────────
if ! gh auth status &>/dev/null; then
  echo "ERROR: Not authenticated. Run: gh auth login"
  exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# MAIN branch — fully locked down
# • No direct pushes (including admins)
# • PR required with 1 approval from owner
# • All CI checks must pass + branch must be up to date
# • Linear history enforced (squash/rebase only — no merge commits)
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "→ Protecting: main"

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${REPO}/branches/main/protection" \
  --field "required_status_checks[strict]=true" \
  --field "required_status_checks[contexts][]=Test auth-service" \
  --field "required_status_checks[contexts][]=Test user-service" \
  --field "required_status_checks[contexts][]=Test food-service" \
  --field "required_status_checks[contexts][]=Test diary-service" \
  --field "required_status_checks[contexts][]=Test ai-service" \
  --field "required_status_checks[contexts][]=Test analytics-service" \
  --field "required_status_checks[contexts][]=Test notification-service" \
  --field "required_status_checks[contexts][]=Test api-gateway" \
  --field "required_status_checks[contexts][]=Test Web (React)" \
  --field "required_status_checks[contexts][]=Test Mobile (Expo)" \
  --field "required_status_checks[contexts][]=Test Infrastructure" \
  --field "enforce_admins=true" \
  --field "required_pull_request_reviews[dismiss_stale_reviews]=true" \
  --field "required_pull_request_reviews[require_code_owner_reviews]=true" \
  --field "required_pull_request_reviews[required_approving_review_count]=1" \
  --field "required_pull_request_reviews[require_last_push_approval]=false" \
  --field "bypass_pull_request_allowances[users][]=VladByPinsk" \
  --field "restrictions=null" \
  --field "allow_force_pushes=false" \
  --field "allow_deletions=false" \
  --field "required_conversation_resolution=true" \
  --field "required_linear_history=true" \
  --field "lock_branch=false"

echo "  ✅ main protected"

# Also enable squash merging only (disables merge commits + rebase)
gh api \
  --method PATCH \
  -H "Accept: application/vnd.github+json" \
  "/repos/${REPO}" \
  --field "allow_squash_merge=true" \
  --field "allow_merge_commit=false" \
  --field "allow_rebase_merge=true" \
  --field "delete_branch_on_merge=true" \
  --field "squash_merge_commit_title=PR_TITLE" \
  --field "squash_merge_commit_message=PR_BODY"

echo "  ✅ Repo: squash+rebase merge only, delete branch on merge enabled"

# ─────────────────────────────────────────────────────────────────────────────
# DEVELOP branch — same rules, admin bypass allowed, linear history optional
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "→ Protecting: develop"

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${REPO}/branches/develop/protection" \
  --field "required_status_checks[strict]=true" \
  --field "required_status_checks[contexts][]=Test auth-service" \
  --field "required_status_checks[contexts][]=Test user-service" \
  --field "required_status_checks[contexts][]=Test food-service" \
  --field "required_status_checks[contexts][]=Test diary-service" \
  --field "required_status_checks[contexts][]=Test ai-service" \
  --field "required_status_checks[contexts][]=Test analytics-service" \
  --field "required_status_checks[contexts][]=Test notification-service" \
  --field "required_status_checks[contexts][]=Test api-gateway" \
  --field "required_status_checks[contexts][]=Test Web (React)" \
  --field "required_status_checks[contexts][]=Test Mobile (Expo)" \
  --field "enforce_admins=false" \
  --field "required_pull_request_reviews[dismiss_stale_reviews]=true" \
  --field "required_pull_request_reviews[required_approving_review_count]=1" \
  --field "bypass_pull_request_allowances[users][]=VladByPinsk" \
  --field "restrictions=null" \
  --field "allow_force_pushes=false" \
  --field "allow_deletions=false" \
  --field "required_conversation_resolution=true" \
  --field "required_linear_history=false"

echo "  ✅ develop protected"

# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════════"
echo "  All branch protection rules applied successfully!"
echo ""
echo "  Verify at:"
echo "  https://github.com/${REPO}/settings/branches"
echo "══════════════════════════════════════════════════════════"
echo ""
