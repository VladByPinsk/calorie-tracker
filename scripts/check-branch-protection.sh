#!/usr/bin/env bash
set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────
# Read from environment — never bake secrets or personal accounts into scripts.
#   export GITHUB_TOKEN=<your PAT>
#   OWNER=MyOrg REPO=my-repo BRANCH=main ./check-branch-protection.sh
OWNER="${OWNER:-VladByPinsk}"
REPO="${REPO:-calorie-tracker}"
BRANCH="${BRANCH:-main}"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "ERROR: GITHUB_TOKEN is not set. Export it before running this script." >&2
  exit 1
fi

curl -s \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/${OWNER}/${REPO}/branches/${BRANCH}/protection" \
  > /tmp/bp_check.json

python3 - /tmp/bp_check.json <<'PYEOF'
import sys, json
d = json.load(open(sys.argv[1]))
rpr = d.get('required_pull_request_reviews', {})
print('enforce_admins (owner can bypass)  :', d.get('enforce_admins', {}).get('enabled'))
print('require_code_owner_reviews         :', rpr.get('require_code_owner_reviews'))
print('required_approving_review_count    :', rpr.get('required_approving_review_count'))
print('dismiss_stale_reviews              :', rpr.get('dismiss_stale_reviews'))
print('required_linear_history            :', d.get('required_linear_history', {}).get('enabled'))
print('required_conversation_resolution   :', d.get('required_conversation_resolution', {}).get('enabled'))
PYEOF
