#!/bin/bash
# 加载 skill 内置凭证（便携核心）
# 优先级：环境变量 > skill config/.env > ~/.baoyu-skills/.env

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

_load_env() {
  local env_file="$1"
  if [ -f "$env_file" ]; then
    while IFS='=' read -r key value; do
      key=$(echo "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
      # 跳过空行和注释行
      if [ -z "$key" ] || [ "${key:0:1}" = "#" ]; then
        continue
      fi
      value=$(echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sed 's/^["'"'"'"]//;s/["'"'"']$//')
      if [ -n "$key" ] && [ -n "$value" ]; then
        export "$key=$value"
      fi
    done < "$env_file"
  fi
}

# 按优先级加载（后者覆盖前者）
_load_env "$HOME/.baoyu-skills/.env"
_load_env "$(pwd)/.baoyu-skills/.env"
_load_env "$SKILL_DIR/config/.env"
