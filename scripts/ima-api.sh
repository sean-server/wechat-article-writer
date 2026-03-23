#!/bin/bash
# IMA 笔记 API 封装（纯 shell，零外部依赖）
# 用法：source ima-api.sh 加载函数
#   ima_create "标题" "正文"    # 新建笔记，返回 doc_id
#   ima_search "关键词"         # 搜索笔记标题
#   ima_append "doc_id" "内容" # 追加内容到已有笔记
#   ima_get "doc_id"           # 获取笔记正文

set -e

IMA_BASE_URL="https://ima.qq.com/openapi/note/v1"

# 加载凭证（若尚未加载）
if [ -z "$IMA_OPENAPI_CLIENTID" ]; then
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  SKILL_DIR="$(dirname "$SCRIPT_DIR")"

  _load_env() {
    local env_file="$1"
    [ -f "$env_file" ] || return
    while IFS='=' read -r key value; do
      value=$(echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sed 's/^["'"'"'"]//;s/["'"'"']$//')
      [ -n "$key" ] && [ -n "$value" ] && export "$key=$value"
    done < "$env_file"
  }

  _load_env "$HOME/.baoyu-skills/.env"
  _load_env "$(pwd)/.baoyu-skills/.env"
  _load_env "$SKILL_DIR/config/.env"
fi

_ima_post() {
  local endpoint="$1"
  local body="$2"
  curl -s -X POST "$IMA_BASE_URL/$endpoint" \
    -H "ima-openapi-clientid: $IMA_OPENAPI_CLIENTID" \
    -H "ima-openapi-apikey: $IMA_OPENAPI_APIKEY" \
    -H "Content-Type: application/json" \
    -d "$body"
}

# 新建笔记（Markdown 格式）
# 参数：标题 正文
# 返回：JSON（含 doc_id）
ima_create() {
  local title="$1"
  local content="$2"
  local md="# ${title}"$'\n\n'"${content}"
  local body
  body=$(python3 -c "import json,sys; d=__import__('urllib.parse').parse; print(json.dumps({'content_format':1,'content':open('/dev/stdin').read()}))" <<< "$md" 2>/dev/null) \
    || body=$(python3 -c "import json; print(json.dumps({'content_format':1,'content':'''${md//\'/\'}'''}))")
  _ima_post "import_doc" "$body"
}

# 搜索笔记（标题模糊匹配）
# 参数：关键词
ima_search() {
  local query="$1"
  local body
  body=$(python3 -c "import json; print(json.dumps({'search_type':0,'query_info':{'title':'''$query'''},'start':0,'end':20}))")
  _ima_post "search_note_book" "$body"
}

# 追加内容到已有笔记
# 参数：doc_id 追加内容
ima_append() {
  local doc_id="$1"
  local content="$2"
  local body
  body=$(python3 -c "import json; print(json.dumps({'doc_id':'''$doc_id','content_format':1,'content':'''$content'''}))")
  _ima_post "append_doc" "$body"
}

# 获取笔记正文
# 参数：doc_id
ima_get() {
  local doc_id="$1"
  local body
  body=$(python3 -c "import json; print(json.dumps({'doc_id':'''$doc_id','target_content_format':0}))")
  _ima_post "get_doc_content" "$body"
}
