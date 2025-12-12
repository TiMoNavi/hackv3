API_BASE="${API_BASE:-http://127.0.0.1:3000}"
MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_DB="${MYSQL_DB:-eventdb}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASS="${MYSQL_PASS:-7j6e+NkRPeudY~>XatbY}"  # .env.mysql 中的密码解码后

USERNAME="${USERNAME:-}"
EMAIL="${EMAIL:-}"
PASSWORD="${PASSWORD:-}"

set -euo pipefail

if [[ -z "${USERNAME}${EMAIL}" || -z "$PASSWORD" ]]; then
  echo "请设置 USERNAME 或 EMAIL 以及 PASSWORD 环境变量"; exit 1
fi

echo "[1] 登录获取 access_token"
if [[ -n "$USERNAME" ]]; then
  LOGIN_PAYLOAD=$(printf '{"username":"%s","email":null,"password":"%s"}' "$USERNAME" "$PASSWORD")
else
  LOGIN_PAYLOAD=$(printf '{"username":null,"email":"%s","password":"%s"}' "$EMAIL" "$PASSWORD")
fi
LOGIN_RESP=$(curl -sS -X POST "$API_BASE/auth/login" -H "Content-Type: application/json" -d "$LOGIN_PAYLOAD")
ACCESS_TOKEN=$(python - <<'PY' <<<"$LOGIN_RESP"
import sys,json
try:
  resp=json.loads(sys.stdin.read())
  data=resp.get("data") or {}
  print(data.get("access_token",""))
except Exception: print("")
PY
)
[[ -n "$ACCESS_TOKEN" ]] || { echo "登录失败：$LOGIN_RESP"; exit 2; }
echo "access_token: ${ACCESS_TOKEN:0:16}..."

echo "[2] 解析 uid 并设为管理员"
UID=$(python - <<PY
import os,sys,json,base64
token=os.environ["TOKEN"]
p=token.split(".")
payload=base64.urlsafe_b64decode(p[1]+'='*(-len(p[1])%4)).decode()
print(json.loads(payload)["sub"])
PY
TOKEN="$ACCESS_TOKEN")
mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASS" -D "$MYSQL_DB" \
  -e "UPDATE users SET isAdmin=1 WHERE uid=$UID;"

echo "[3] 管理员 ping"
curl -sS -H "Authorization: Bearer $ACCESS_TOKEN" "$API_BASE/admin/ping"

echo -e "\n[4] 管理员统计"
curl -sS -H "Authorization: Bearer $ACCESS_TOKEN" "$API_BASE/admin/stats"

echo -e "\n[5] 报名分页列表（第一页，全部状态）"
curl -sS -H "Authorization: Bearer $ACCESS_TOKEN" "$API_BASE/admin/registrations?page=1"

echo -e "\n[6] 用户分页列表（第一页）"
curl -sS -H "Authorization: Bearer $ACCESS_TOKEN" "$API_BASE/admin/users?page=1"

echo -e "\n[7] 审核报名（示例：ID=1 改为 approved，如不存在会返回错误）"
curl -sS -X PUT -H "Authorization: Bearer $ACCESS_TOKEN" "$API_BASE/admin/registrations/1/audit?status=approved"
echo -e "\n完成"
