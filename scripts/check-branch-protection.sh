#!/usr/bin/env bash
set -euo pipefail

TOKEN=$(security find-internet-password -s github.com -a VladByPinsk -w 2>/dev/null)

curl -s \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/VladByPinsk/calorie-tracker/branches/main/protection" \
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

