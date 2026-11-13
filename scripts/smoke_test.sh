#!/bin/bash
BASE=${1:-http://localhost:8081}
FIELD=${2:-name}
fail() { echo "FAIL: $1"; exit 1; }

echo "== 1. List items"
code=$(curl -s -o /dev/null -w "%{http_code}" $BASE/api/items)
[ "$code" = "200" ] && echo "PASS list" || fail "list returned $code"

echo "== 2. Empty item rejected"
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "{\"$FIELD\":\"\"}" $BASE/api/items)
[ "$code" = "400" ] && echo "PASS validation" || fail "empty item returned $code"

echo "== 3. Create and read back"
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "{\"$FIELD\":\"smoke-test-item\"}" $BASE/api/items)
[ "$code" = "201" ] || [ "$code" = "200" ] || fail "create returned $code"
curl -s $BASE/api/items | grep -q "smoke-test-item" && echo "PASS create + list" || fail "item not found"

echo "== 4. SQL injection stored as text"
curl -s -o /dev/null -X POST -H "Content-Type: application/json" -d "{\"$FIELD\":\"x'); DROP TABLE items;--\"}" $BASE/api/items
code=$(curl -s -o /dev/null -w "%{http_code}" $BASE/api/items)
[ "$code" = "200" ] && echo "PASS parameterized queries (table still exists)" || fail "table broken"

echo "ALL TESTS PASSED"
