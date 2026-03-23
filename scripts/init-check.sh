#!/bin/bash
# wechat-article-writer 初始化检查脚本
# 检测运行环境和必要配置是否完整

# 不使用 set -e，改为手动错误处理

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 检查项计数
CHECK_PASSED=0
CHECK_FAILED=0
CHECK_WARN=0

# 记忆文件路径（相对于 skill 根目录）
MEMORY_FILE="$SKILL_DIR/.initialized"

print_header() {
    echo ""
    echo "========================================"
    echo "  wechat-article-writer 初始化检查"
    echo "========================================"
    echo ""
}

print_section() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo "----------------------------------------"
}

print_ok() {
    echo -e "${GREEN}✓${NC} $1"
    ((CHECK_PASSED++))
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    ((CHECK_FAILED++))
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((CHECK_WARN++))
}

print_info() {
    echo -e "  $1"
}

# ==================== 检查1: 运行环境 ====================
check_environment() {
    print_section "1. 运行环境检查"
    
    # 检查 Bun
    if command -v bun &> /dev/null; then
        BUN_VERSION=$(bun --version)
        print_ok "Bun 已安装 (版本: $BUN_VERSION)"
    else
        print_error "Bun 未安装"
        print_info "安装命令: curl -fsSL https://bun.sh/install | bash"
    fi
    
    # 检查 Python3
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_ok "Python3 已安装 (版本: $PYTHON_VERSION)"
    else
        print_error "Python3 未安装"
        print_info "请安装 Python3: https://www.python.org/downloads/"
    fi
    
    # 检查 pip3
    if command -v pip3 &> /dev/null; then
        print_ok "pip3 已安装"
    else
        print_warn "pip3 未安装（可能影响 Python 依赖安装）"
    fi
    
    # 检查 curl
    if command -v curl &> /dev/null; then
        print_ok "curl 已安装"
    else
        print_error "curl 未安装（必需，用于 API 调用）"
    fi
}

# ==================== 检查2: Python依赖 ====================
check_python_deps() {
    print_section "2. Python 依赖检查"
    
    local deps=("PIL" "requests" "urllib3")
    local dep_names=("Pillow" "requests" "urllib3")
    
    for i in "${!deps[@]}"; do
        local dep="${deps[$i]}"
        local name="${dep_names[$i]}"
        
        if python3 -c "import $dep" 2>/dev/null; then
            print_ok "Python 模块: $name"
        else
            print_warn "Python 模块缺失: $name"
            print_info "安装命令: pip3 install $name"
        fi
    done
}

# ==================== 检查3: 配置文件 ====================
check_config() {
    print_section "3. 配置文件检查"
    
    local config_file="$SKILL_DIR/config/.env"
    
    if [[ -f "$config_file" ]]; then
        print_ok "配置文件存在: config/.env"
        
        # 检查微信公众号凭证
        local wechat_app_id=$(grep "^WECHAT_APP_ID=" "$config_file" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        local wechat_secret=$(grep "^WECHAT_APP_SECRET=" "$config_file" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        
        if [[ -n "$wechat_app_id" && "$wechat_app_id" != "your_app_id" && ${#wechat_app_id} -gt 10 ]]; then
            print_ok "微信公众号 AppID 已配置"
        else
            print_error "微信公众号 AppID 未配置或无效"
            print_info "获取方式: 登录微信公众平台 → 开发 → 基本配置"
        fi
        
        if [[ -n "$wechat_secret" && "$wechat_secret" != "your_app_secret" && ${#wechat_secret} -gt 20 ]]; then
            print_ok "微信公众号 AppSecret 已配置"
        else
            print_error "微信公众号 AppSecret 未配置或无效"
        fi
        
        # 检查 IMA 凭证
        local ima_clientid=$(grep "^IMA_OPENAPI_CLIENTID=" "$config_file" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        local ima_apikey=$(grep "^IMA_OPENAPI_APIKEY=" "$config_file" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        
        if [[ -n "$ima_clientid" && "$ima_clientid" != "your_client_id" && ${#ima_clientid} -gt 10 ]]; then
            print_ok "IMA ClientID 已配置"
        else
            print_warn "IMA ClientID 未配置（可选，用于自动保存到 IMA 笔记）"
            print_info "获取方式: https://ima.qq.com/agent-interface"
        fi
        
        if [[ -n "$ima_apikey" && "$ima_apikey" != "your_api_key" && ${#ima_apikey} -gt 10 ]]; then
            print_ok "IMA APIKey 已配置"
        else
            print_warn "IMA APIKey 未配置（可选）"
        fi
        
    else
        print_error "配置文件不存在: config/.env"
        print_info "请复制 config/.env.example 到 config/.env 并填写凭证"
    fi
}

# ==================== 检查4: 知识库文件 ====================
check_knowledge_base() {
    print_section "4. 知识库文件检查"
    
    local kb_dir="$SKILL_DIR/references/knowledge_base"
    local files=(
        "01_用户画像.md:用户画像"
        "02_个人自传.md:个人自传"
        "03_写作风格指南.md:写作风格指南"
        "05_文案框架库.md:文案框架库"
        "07_内容日历.md:内容日历"
    )
    
    for item in "${files[@]}"; do
        local file="${item%%:*}"
        local name="${item##*:}"
        local filepath="$kb_dir/$file"
        
        if [[ -f "$filepath" ]]; then
            # 检查文件是否有内容（非模板）
            local line_count=$(wc -l < "$filepath" 2>/dev/null || echo "0")
            if [[ $line_count -gt 50 ]]; then
                print_ok "$name 已完善 ($line_count 行)"
            else
                print_warn "$name 内容较少 ($line_count 行)，建议完善"
            fi
        else
            print_error "$name 文件缺失: $file"
        fi
    done
}

# ==================== 检查5: 脚本文件 ====================
check_scripts() {
    print_section "5. 脚本文件检查"
    
    local scripts=(
        "scripts/publish.sh:发布脚本"
        "scripts/auto_publish.sh:自动发布脚本"
        "scripts/wechat-api.ts:微信 API 脚本"
        "scripts/md-to-wechat.ts:Markdown 转换脚本"
        "scripts/generate_cover.py:封面生成脚本"
        "scripts/generate_content_imgs.py:内容配图脚本"
        "scripts/ima-api.sh:IMA API 脚本"
    )
    
    for item in "${scripts[@]}"; do
        local script="${item%%:*}"
        local name="${item##*:}"
        local scriptpath="$SKILL_DIR/$script"
        
        if [[ -f "$scriptpath" ]]; then
            if [[ -x "$scriptpath" ]] || [[ "$script" == *.ts ]]; then
                print_ok "$name"
            else
                print_warn "$name 存在但可能无执行权限"
            fi
        else
            print_error "$name 缺失: $script"
        fi
    done
}

# ==================== 检查6: 网络连接 ====================
check_network() {
    print_section "6. 网络连接检查"
    
    # 检查是否可以访问微信 API
    if curl -s --max-time 5 "https://api.weixin.qq.com/cgi-bin/token" > /dev/null 2>&1; then
        print_ok "可以访问微信公众号 API"
    else
        print_warn "无法访问微信公众号 API（可能是网络问题）"
    fi
    
    # 检查是否可以访问 IMA API
    if curl -s --max-time 5 "https://ima.qq.com" > /dev/null 2>&1; then
        print_ok "可以访问 IMA 服务"
    else
        print_warn "无法访问 IMA 服务（可能是网络问题）"
    fi
    
    # 检查是否可以访问 Unsplash
    if curl -s --max-time 5 "https://unsplash.com" > /dev/null 2>&1; then
        print_ok "可以访问 Unsplash（封面图片来源）"
    else
        print_warn "无法访问 Unsplash（可能影响封面图下载）"
    fi
}

# ==================== 检查7: 微信公众号API连通性 ====================
check_wechat_api() {
    print_section "7. 微信公众号 API 连通性检查"
    
    local config_file="$SKILL_DIR/config/.env"
    local wechat_app_id=$(grep "^WECHAT_APP_ID=" "$config_file" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    local wechat_secret=$(grep "^WECHAT_APP_SECRET=" "$config_file" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    
    # 如果凭证未配置，跳过此检查
    if [[ -z "$wechat_app_id" || -z "$wechat_secret" || "$wechat_app_id" == "your_app_id" ]]; then
        print_warn "微信公众号凭证未配置，跳过 API 连通性检查"
        print_info "请先在 config/.env 中配置 WECHAT_APP_ID 和 WECHAT_APP_SECRET"
        return
    fi
    
    # 尝试获取 access_token
    local api_url="https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=$wechat_app_id&secret=$wechat_secret"
    local response=$(curl -s --max-time 10 "$api_url" 2>/dev/null)
    
    # 检查响应
    if echo "$response" | grep -q '"access_token"'; then
        print_ok "微信公众号 API 连接成功（access_token 获取正常）"
        print_ok "IP 白名单配置正确"
    elif echo "$response" | grep -q 'invalid ip.*not in whitelist'; then
        # 提取报错的 IP 地址
        local blocked_ip=$(echo "$response" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        print_error "微信公众号 IP 白名单未配置"
        print_info "当前公网 IP: $blocked_ip"
        print_info ""
        print_info "请按以下步骤添加 IP 白名单："
        print_info "1. 登录微信公众平台: https://mp.weixin.qq.com"
        print_info "2. 左侧菜单 → 设置与开发 → 基本配置"
        print_info "3. 找到「IP白名单」，点击修改"
        print_info "4. 添加以下 IP: $blocked_ip"
        print_info "5. 保存后重新运行此检查"
    elif echo "$response" | grep -q 'invalid appid'; then
        print_error "微信公众号 AppID 无效"
        print_info "请检查 config/.env 中的 WECHAT_APP_ID 是否正确"
    elif echo "$response" | grep -q 'invalid appsecret\|invalid secret'; then
        print_error "微信公众号 AppSecret 无效"
        print_info "请检查 config/.env 中的 WECHAT_APP_SECRET 是否正确"
    else
        print_warn "微信公众号 API 响应异常"
        print_info "响应内容: $response"
    fi
}

# ==================== 生成报告 ====================
print_summary() {
    echo ""
    echo "========================================"
    echo "           检查报告汇总"
    echo "========================================"
    echo ""
    echo -e "${GREEN}通过: $CHECK_PASSED${NC}"
    echo -e "${YELLOW}警告: $CHECK_WARN${NC}"
    echo -e "${RED}失败: $CHECK_FAILED${NC}"
    echo ""
    
    if [[ $CHECK_FAILED -eq 0 && $CHECK_WARN -eq 0 ]]; then
        echo -e "${GREEN}✓ 所有检查通过！Skill 已就绪，可以开始使用。${NC}"
        echo ""
        echo "使用方式: 直接说 '发布公众号' 或 '写篇文章'"
        return 0
    elif [[ $CHECK_FAILED -eq 0 ]]; then
        echo -e "${YELLOW}⚠ 基本可用，但有一些警告项。建议完善后再使用。${NC}"
        return 1
    else
        echo -e "${RED}✗ 存在必需项未配置，请先完成以下步骤：${NC}"
        echo ""
        echo "1. 安装必要环境（Bun、Python3）"
        echo "2. 配置微信公众号凭证（config/.env）"
        echo "3. 完善知识库文件（references/knowledge_base/）"
        echo ""
        echo "详细指南请查看 SKILL.md 的「前置条件」部分"
        return 2
    fi
}

# ==================== 交互式引导 ====================
interactive_setup() {
    echo ""
    echo -e "${BLUE}是否进入交互式配置引导？(y/n)${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo "========================================"
        echo "        交互式配置引导"
        echo "========================================"
        
        # 引导配置微信公众号
        echo ""
        echo "【步骤1】配置微信公众号凭证"
        echo "获取方式: 登录 mp.weixin.qq.com → 开发 → 基本配置"
        echo ""
        
        local config_file="$SKILL_DIR/config/.env"
        
        echo -n "请输入微信公众号 AppID: "
        read -r app_id
        echo -n "请输入微信公众号 AppSecret: "
        read -r app_secret
        
        if [[ -n "$app_id" && -n "$app_secret" ]]; then
            # 更新配置文件
            sed -i.bak "s/^WECHAT_APP_ID=.*/WECHAT_APP_ID=$app_id/" "$config_file" 2>/dev/null || \
            echo "WECHAT_APP_ID=$app_id" >> "$config_file"
            
            sed -i.bak "s/^WECHAT_APP_SECRET=.*/WECHAT_APP_SECRET=$app_secret/" "$config_file" 2>/dev/null || \
            echo "WECHAT_APP_SECRET=$app_secret" >> "$config_file"
            
            echo -e "${GREEN}✓ 微信公众号凭证已保存${NC}"
        fi
        
        # 引导配置 IMA（可选）
        echo ""
        echo "【步骤2】配置 IMA 笔记（可选）"
        echo "获取方式: https://ima.qq.com/agent-interface"
        echo ""
        echo -n "是否配置 IMA 笔记？(y/n): "
        read -r setup_ima
        
        if [[ "$setup_ima" =~ ^[Yy]$ ]]; then
            echo -n "请输入 IMA ClientID: "
            read -r ima_clientid
            echo -n "请输入 IMA APIKey: "
            read -r ima_apikey
            
            if [[ -n "$ima_clientid" ]]; then
                sed -i.bak "s/^IMA_OPENAPI_CLIENTID=.*/IMA_OPENAPI_CLIENTID=$ima_clientid/" "$config_file" 2>/dev/null || \
                echo "IMA_OPENAPI_CLIENTID=$ima_clientid" >> "$config_file"
            fi
            
            if [[ -n "$ima_apikey" ]]; then
                sed -i.bak "s/^IMA_OPENAPI_APIKEY=.*/IMA_OPENAPI_APIKEY=$ima_apikey/" "$config_file" 2>/dev/null || \
                echo "IMA_OPENAPI_APIKEY=$ima_apikey" >> "$config_file"
            fi
            
            echo -e "${GREEN}✓ IMA 凭证已保存${NC}"
        fi
        
        echo ""
        echo -e "${GREEN}配置完成！请重新运行初始化检查确认。${NC}"
    fi
}

# ==================== 主流程 ====================
main() {
    print_header
    
    check_environment
    check_python_deps
    check_config
    check_knowledge_base
    check_scripts
    check_network
    check_wechat_api
    
    local result
    print_summary
    result=$?
    
    # 如果有失败项，提供交互式引导
    if [[ $result -ne 0 ]]; then
        interactive_setup
    fi
    
    # 如果全部通过，创建初始化标记文件
    if [[ $result -eq 0 ]]; then
        touch "$MEMORY_FILE"
        echo "$(date +%Y-%m-%d)" > "$MEMORY_FILE"
        echo ""
        echo -e "${GREEN}✓ 初始化标记已创建，下次使用将跳过检查${NC}"
    fi
    
    return $result
}

# 执行主流程
main
