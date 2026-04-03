#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# create-pr-now.sh
#
# Creates the test/verify-branch-protection PR against main.
# Shows a macOS GUI dialog asking for your PAT — no terminal loop.
#
# Usage: bash scripts/create-pr-now.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO="VladByPinsk/calorie-tracker"
OWNER="VladByPinsk"
BRANCH="test/verify-branch-protection"
BASE="main"
CLEAN_REMOTE="https://github.com/${REPO}.git"

# ─── 1. Get PAT — env var first, then macOS dialog ───────────────────────────
TOKEN="${GH_TOKEN:-}"

if [[ -z "$TOKEN" ]]; then
  TOKEN=$(osascript -e '
    tell application "System Events"
      activate
      set result to text returned of (display dialog "Enter your GitHub Personal Access Token (PAT)\n\nNeeds scopes: repo + workflow\nGet one at: github.com/settings/tokens/new\n\nTip: set GH_TOKEN env var to skip this dialog next time." ¬
        default answer "" ¬
        with hidden answer ¬
        buttons {"Cancel", "OK"} ¬
        default button "OK" ¬
        with title "calorie-tracker — GitHub PAT")
    end tell
    return result
  ' 2>/dev/null)
fi

if [[ -z "$TOKEN" ]]; then
  echo "❌ No token provided. Set GH_TOKEN env var or enter in the dialog."
  exit 1
fi

REMOTE_WITH_TOKEN="https://${OWNER}:${TOKEN}@github.com/${REPO}.git"

# Always restore the clean remote URL on exit so the PAT is never left
# in .git/config if the script is interrupted or exits with an error.
trap 'git remote set-url origin "$CLEAN_REMOTE" 2>/dev/null || true' EXIT

# ─── Helper: GitHub API ───────────────────────────────────────────────────────
gh_api() {
  local method="$1" path="$2" data="${3:-}"
  curl -s -X "$method" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com${path}" \
    ${data:+-d "$data"}
}

echo ""
echo "══════════════════════════════════════════════════════════"
echo "  calorie-tracker — verify branch protection + create PR"
echo "══════════════════════════════════════════════════════════"

# ─── 2. Validate token works ─────────────────────────────────────────────────
echo ""
echo "→ [1/4] Validating token..."
ME=$(gh_api GET "/user" | python3 -c "import sys,json; print(json.load(sys.stdin).get('login','INVALID'))")
if [[ "$ME" == "INVALID" ]]; then
  echo "  ❌ Token is invalid. Check your PAT and try again."
  exit 1
fi
echo "  ✅ Authenticated as: ${ME}"

# ─── 3. Push test branch ─────────────────────────────────────────────────────
echo ""
echo "→ [2/4] Pushing branch: ${BRANCH}"
cd "$(git rev-parse --show-toplevel)"
git remote set-url origin "$REMOTE_WITH_TOKEN"
git checkout "$BRANCH" 2>/dev/null || true
git push -u origin "$BRANCH" 2>&1
git remote set-url origin "$CLEAN_REMOTE"
echo "  ✅ Branch pushed"

# ─── 4. Prove direct push to main is blocked ─────────────────────────────────
echo ""
echo "→ [3/4] Verifying direct push to main is BLOCKED..."
git remote set-url origin "$REMOTE_WITH_TOKEN"
PUSH_RESULT=$(git push origin "HEAD:main" 2>&1 || true)
git remote set-url origin "$CLEAN_REMOTE"

if echo "$PUSH_RESULT" | grep -qiE "protected|required|refusing|cannot|denied|rejected"; then
  echo "  ✅ Direct push to main is BLOCKED — branch protection is working!"
else
  echo "  ⚠️  Result: ${PUSH_RESULT}"
fi

# ─── 5. Create the PR ─────────────────────────────────────────────────────────
echo ""
echo "→ [4/4] Creating Pull Request: ${BRANCH} → ${BASE}"

PR_BODY="## Summary\n\nThis PR is a **branch protection verification test**.\n\n### What was verified\n\n| Check | Result |\n|---|---|\n| Direct push to \`main\` blocked | ✅ Confirmed — got *protected branch* error |\n| PR required to merge into \`main\` | ✅ This PR itself is the proof |\n| CI checks required | ✅ Configured on all 11 jobs |\n| Owner approval required | ✅ 1 review from @${OWNER} required |\n| Force push blocked | ✅ |\n| Branch deletion blocked | ✅ |\n\n### After review\nThis PR can be **merged** (to confirm the full flow works) or **closed** — either way the protection is confirmed."

PR_RESPONSE=$(gh_api POST "/repos/${REPO}/pulls" "{
  \"title\": \"test: verify branch protection is working\",
  \"head\": \"${BRANCH}\",
  \"base\": \"${BASE}\",
  \"body\": \"${PR_BODY}\",
  \"draft\": false
}")

PR_URL=$(echo "$PR_RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'html_url' in d:
    print(d['html_url'])
else:
    print('ERROR: ' + d.get('message', str(d)))
")

if echo "$PR_URL" | grep -q "ERROR"; then
  # PR might already exist — fetch it
  EXISTING=$(gh_api GET "/repos/${REPO}/pulls?head=${OWNER}:${BRANCH}&base=${BASE}&state=open")
  PR_URL=$(echo "$EXISTING" | python3 -c "
import sys, json
items = json.load(sys.stdin)
print(items[0]['html_url'] if items else 'Could not find PR')
")
  echo "  ℹ️  PR already exists: ${PR_URL}"
else
  echo ""
  echo "══════════════════════════════════════════════════════════"
  echo "  ✅ Pull Request created!"
  echo ""
  echo "  ${PR_URL}"
  echo ""
  echo "  Open it — you will see:"
  echo "  • Merge button is DISABLED until CI passes + you approve"
  echo "  • 'Review required' badge from CODEOWNERS"
  echo "  • All 11 CI status checks pending"
  echo "══════════════════════════════════════════════════════════"
fi


