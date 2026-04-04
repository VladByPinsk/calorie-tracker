#!/usr/bin/env bash
set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────
# Read from environment — never bake secrets or personal accounts into scripts.
#   export GITHUB_TOKEN=<your PAT>
#   OWNER=MyOrg REPO=my-repo BRANCH=main ./set-branch-protection.sh
OWNER="${OWNER:-VladByPinsk}"
REPO="${REPO:-calorie-tracker}"
BRANCH="${BRANCH:-main}"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "ERROR: GITHUB_TOKEN is not set. Export it before running this script." >&2
  exit 1
fi

API_URL="https://api.github.com/repos/${OWNER}/${REPO}/branches/${BRANCH}/protection"

# Re-apply branch protection rules.
# bypass_pull_request_allowances.users accepts login strings (not numeric IDs)
# per the GitHub REST API v2022-11-28 spec.
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X PUT \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "${API_URL}" \
  -d '{
    "required_status_checks": { "strict": true, "contexts": ["CI"] },
    "enforce_admins": false,
    "required_pull_request_reviews": {
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": true,
      "required_approving_review_count": 1,
      "require_last_push_approval": false
    },
    "bypass_pull_request_allowances": {
      "users": ["'"${OWNER}"'"],
      "teams": [],
      "apps": []
    },
    "restrictions": null,
    "allow_force_pushes": false,
    "allow_deletions": false,
    "required_conversation_resolution": true,
    "required_linear_history": true
  }')

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | tail -1 | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_STATUS:")
echo "HTTP status: $HTTP_STATUS"
echo "Raw response: $BODY"

echo "$BODY" > /tmp/bp_response.json
python3 /dev/stdin /tmp/bp_response.json <<'PYEOF'
import sys, json
d = json.load(open(sys.argv[1]))
rpr = d.get('required_pull_request_reviews', {})
bpa = d.get('bypass_pull_request_allowances', {})
print('require_last_push_approval:', rpr.get('require_last_push_approval'))
print('enforce_admins            :', d.get('enforce_admins', {}).get('enabled'))
print('bypass users              :', [u.get('login') for u in bpa.get('users', [])])
PYEOF
