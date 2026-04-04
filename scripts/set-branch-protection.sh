#!/usr/bin/env bash
set -euo pipefail

TOKEN=$(security find-internet-password -s github.com -a VladByPinsk -w 2>/dev/null)

# Get numeric user ID
USER_ID=$(curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/user \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "User ID: $USER_ID"

# Re-apply with numeric ID in bypass allowances
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/VladByPinsk/calorie-tracker/branches/main/protection" \
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
      "users": ["VladByPinsk"],
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

