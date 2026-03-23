#!/bin/bash
# 自动主题推荐发布脚本
# 根据文章内容自动推荐最合适的主题，让发布更有惊喜感

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印分隔线
print_separator() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# 解析参数
ARTICLE_PATH=""
AUTHOR=""
THEME=""
COLOR=""
MANUAL_THEME=""
MANUAL_COLOR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --theme)
            MANUAL_THEME="$2"
            shift 2
            ;;
        --color)
            MANUAL_COLOR="$2"
            shift 2
            ;;
        --author)
            AUTHOR="$2"
            shift 2
            ;;
        *.md|*.html)
            ARTICLE_PATH="$1"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

if [[ -z "$ARTICLE_PATH" ]]; then
    echo "用法: ./auto_publish.sh <文章路径> [--theme <主题>] [--color <颜色>] [--author <作者>]"
    echo ""
    echo "示例:"
    echo "  ./auto_publish.sh ../outputs/2026-03-21/文章标题/article.md"
    echo "  ./auto_publish.sh article.md --author 萧十一说"
    echo "  ./auto_publish.sh article.md --theme modern --color blue"
    exit 1
fi

# 转换为绝对路径
if [[ ! "$ARTICLE_PATH" = /* ]]; then
    ARTICLE_PATH="$(cd "$(dirname "$ARTICLE_PATH")" && pwd)/$(basename "$ARTICLE_PATH")"
fi

echo ""
echo -e "${CYAN}🎨 智能主题推荐系统${NC}"
print_separator

# 如果用户指定了主题，使用用户指定的
if [[ -n "$MANUAL_THEME" ]]; then
    THEME="$MANUAL_THEME"
    COLOR="$MANUAL_COLOR"
    echo -e "${YELLOW}📌 使用手动指定的主题: $THEME${NC}"
    if [[ -n "$COLOR" ]]; then
        echo -e "${YELLOW}🎨 颜色: $COLOR${NC}"
    fi
else
    # 自动推荐主题
    echo -e "${BLUE}🔍 正在分析文章内容...${NC}"
    
    # 调用主题推荐脚本
    RECOMMEND_JSON=$(cd "$SCRIPT_DIR" && bun auto_theme_selector.ts "$ARTICLE_PATH" 2>/dev/null)
    
    if [[ -n "$RECOMMEND_JSON" ]]; then
        THEME=$(echo "$RECOMMEND_JSON" | grep -o '"theme":"[^"]*"' | cut -d'"' -f4)
        COLOR=$(echo "$RECOMMEND_JSON" | grep -o '"color":"[^"]*"' | cut -d'"' -f4)
        THEME_NAME=$(echo "$RECOMMEND_JSON" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
        
        echo ""
        print_separator
        echo -e "${GREEN}🎉 推荐结果${NC}"
        echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "   ${PURPLE}✨ $THEME_NAME ✨${NC}"
        echo ""
        echo -e "   📦 主题: $THEME"
        echo -e "   🎨 颜色: $COLOR"
        echo ""
        print_separator
        
        # 显示主题风格说明
        case $THEME in
            modern)
                echo -e "   ${CYAN}→ 风格特点:${NC} 大圆角、胶囊标题、宽松行距，适合干货方法类"
                ;;
            grace)
                echo -e "   ${CYAN}→ 风格特点:${NC} 文字阴影、圆角卡片、精美引用，适合情感故事类"
                ;;
            simple)
                echo -e "   ${CYAN}→ 风格特点:${NC} 不对称圆角、大量留白、现代简约，适合生活休闲类"
                ;;
            default)
                echo -e "   ${CYAN}→ 风格特点:${NC} 居中标题、底部边框、H2彩色背景，适合热点评论类"
                ;;
        esac
        
        echo ""
        print_separator
        echo ""
    else
        # 推荐失败，使用默认
        THEME="modern"
        COLOR="blue"
        echo -e "${YELLOW}⚠️ 主题推荐失败，使用默认主题: modern${NC}"
    fi
fi

# 构建发布命令
CMD="bun wechat-api.ts \"$ARTICLE_PATH\""

if [[ -n "$AUTHOR" ]]; then
    CMD="$CMD --author \"$AUTHOR\""
fi

if [[ -n "$THEME" ]]; then
    CMD="$CMD --theme $THEME"
fi

if [[ -n "$COLOR" ]]; then
    CMD="$CMD --color $COLOR"
fi

# 执行发布
echo -e "${BLUE}🚀 开始发布文章...${NC}"
echo ""

cd "$SCRIPT_DIR" && eval $CMD

echo ""
echo -e "${GREEN}✅ 发布完成！${NC}"
