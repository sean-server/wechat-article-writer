#!/bin/bash
# 发布脚本：从头到尾完成封面图 + 内容配图 + 发布
# 所有路径均相对于本脚本所在目录，无需硬编码

set -e

# 本脚本所在目录（skill 根目录）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 加载凭证（优先级：config/.env > .baoyu-skills/.env）
# shellcheck source=/dev/null
source "$SCRIPT_DIR/source-env.sh"

# 参数
ARTICLE_MD="$1"
TITLE="$2"
AUTHOR="${3:-萧十一说}"
THEME="${4:-modern}"  # 默认使用 modern 主题

if [ -z "$ARTICLE_MD" ] || [ -z "$TITLE" ]; then
    echo "用法: ./publish.sh <文章.md> <标题> [作者] [主题]"
    echo "示例: ./publish.sh ../outputs/2026-03-20/成年人的崩溃/article.md '成年人的崩溃' '萧十一说' modern"
    exit 1
fi

# 获取目录
ARTICLE_DIR=$(dirname "$ARTICLE_MD")
IMGS_DIR="$ARTICLE_DIR/imgs"

echo "========================================="
echo "📤 开始发布流程"
echo "========================================="
echo "文章: $ARTICLE_MD"
echo "标题: $TITLE"
echo "作者: $AUTHOR"
echo "主题: $THEME"
echo ""

# Step 1: 生成封面图
echo "📋 Step 1: 生成封面图..."
python3 "$SCRIPT_DIR/generate_cover.py" \
    "$TITLE" \
    "$IMGS_DIR/cover.png" \
    "$AUTHOR"
echo ""

# Step 2: 生成内容配图
echo "📋 Step 2: 生成内容配图..."
python3 "$SCRIPT_DIR/generate_content_imgs.py" "$ARTICLE_MD"
echo ""

# Step 3: 发布到公众号
echo "📋 Step 3: 发布到公众号..."
cd "$SCRIPT_DIR"
bun wechat-api.ts "$ARTICLE_MD" \
    --theme "$THEME" \
    --author "$AUTHOR" \
    --cite

echo ""
echo "========================================="
echo "✅ 发布完成！"
echo "========================================="
