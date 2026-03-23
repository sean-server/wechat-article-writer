#!/usr/bin/env python3
"""
微信公众号文章封面图生成脚本
支持两种模式：
1. 下载 Unsplash 真实照片（优先）
2. PIL 备用生成（无网络时）

用法: python3 generate_cover.py <标题> <输出路径> [副标题]
"""

from PIL import Image, ImageDraw, ImageFont
import os
import sys
import random

# Unsplash Source API - 免认证获取免费图片
UNSPLASH_COVER_COLLECTIONS = {
    "职场": ["photo-1497032628192-86f99bcd76bc", "photo-1521737711867-e3b97375f902"],
    "情感": ["photo-1516589178581-6cd7833ae3b2", "photo-1474552226712-ac0f0961a954"],
    "科技": ["photo-1518770660439-4636190af475", "photo-1485827404703-89b55fcc595e"],
    "生活": ["photo-1506905925346-21bda4d32df4", "photo-1507003211169-0a1dd7228f2d"],
    "成长": ["photo-1434030216411-0b793f4b4173", "photo-1488190211105-8b0bb65f13e5"],
    "默认": ["photo-1507003211169-0a1dd7228f2d", "photo-1516589178581-6cd7833ae3b2"],
}

FALLBACK_COVER_COLLECTIONS = {
    "职场": (40, 60, 100),
    "情感": (120, 60, 80),
    "科技": (30, 60, 100),
    "生活": (50, 80, 60),
    "成长": (80, 60, 40),
    "默认": (60, 60, 90),
}

def detect_category(title):
    """根据标题关键词判断类别"""
    categories = {
        "职场": ["职场", "工作", "领导", "同事", "辞职", "加薪", "面试", "同事", "开会", "工资", "打工"],
        "情感": ["感情", "爱情", "分手", "恋爱", "异地恋", "婚姻", "家庭", "结婚", "另一半", "崩溃", "焦虑", "安全感", "眼泪", "委屈", "心累"],
        "科技": ["AI", "科技", "技术", "互联网", "创业", "程序员", "数据", "智能", "未来"],
        "成长": ["成长", "学习", "读书", "提升", "改变", "突破", "认知", "思维", "努力", "坚持"],
        "生活": ["生活", "人生", "活法", "幸福", "快乐", "朋友", "社交", "孤独"],
    }
    title_lower = title.lower()
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in title:
                return cat
    return "默认"


def download_unsplash_cover(title, output_path, subtitle="萧十一说"):
    """从 Unsplash 下载真实照片作为封面"""
    import urllib.request
    import urllib.error

    category = detect_category(title)
    photos = UNSPLASH_COVER_COLLECTIONS.get(category, UNSPLASH_COVER_COLLECTIONS["默认"])

    for photo_id in photos:
        try:
            # photo_id 格式为 "photo-1507003211169-0a1dd7228f2d"，需要去掉前缀
            clean_id = photo_id.replace("photo-", "")
            url = f"https://images.unsplash.com/photo-{clean_id}?w=1280&h=720&fit=crop&auto=format&q=80"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                img_data = response.read()
                if len(img_data) > 10000:  # 确保图片有效
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(img_data)
                    print(f"封面图已下载（{category}）: {output_path}")
                    return True
        except Exception as e:
            continue

    return False


def generate_text_cover(title, output_path, subtitle="萧十一说"):
    """用 PIL 生成图文叠加封面（备用方案）"""

    random.seed(hash(title) % 2**32)

    # 颜色配置
    category = detect_category(title)
    bg_color = FALLBACK_COVER_COLLECTIONS.get(category, FALLBACK_COVER_COLLECTIONS["默认"])

    colors = {
        'bg': bg_color,
        'text': (255, 255, 255),
        'subtitle': (220, 220, 240),
        'author': (160, 170, 190),
        'accent': (bg_color[0]+30, bg_color[1]+30, bg_color[2]+30) if bg_color[0] < 200 else (bg_color[0]-30, bg_color[1]-30, bg_color[2]-30),
    }

    width, height = 1280, 720
    img = Image.new('RGB', (width, height), color=colors['bg'])
    draw = ImageDraw.Draw(img)

    # 加载字体
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 72)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 36)
        small_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 28)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # 绘制装饰线（顶部）
    draw.rectangle([0, 0, width, 3], fill=(255, 255, 255))

    # 绘制装饰元素 - 圆形光晕
    center_x, center_y = width // 2, height // 2 + 30
    for i in range(4):
        radius = 280 - i * 50
        alpha = 20 + i * 8
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            fill=(colors['accent'][0]//3, colors['accent'][1]//3, colors['accent'][2]//3)
        )

    # 绘制标题文字（居中，最多两行）
    max_width = width - 160
    if len(title) > 12:
        mid = len(title) // 2
        for i in range(mid, len(title)):
            if title[i] in '，、。！？：；「」（）《》':
                mid = i + 1
                break
        title1 = title[:mid]
        title2 = title[mid:]

        bbox1 = draw.textbbox((0, 0), title1, font=title_font)
        draw.text(((width - (bbox1[2] - bbox1[0])) // 2, 220), title1,
                  fill=colors['text'], font=title_font)

        bbox2 = draw.textbbox((0, 0), title2, font=title_font)
        draw.text(((width - (bbox2[2] - bbox2[0])) // 2, 320), title2,
                  fill=colors['text'], font=title_font)
    else:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        draw.text(((width - (bbox[2] - bbox[0])) // 2, 260), title,
                  fill=colors['text'], font=title_font)

    # 绘制副标题（底部）
    if subtitle:
        bbox_sub = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        draw.text(((width - (bbox_sub[2] - bbox_sub[0])) // 2, height - 120),
                  subtitle, fill=colors['author'], font=subtitle_font)

    # 底部装饰线
    draw.rectangle([0, height - 3, width, height], fill=(255, 255, 255))

    # 左侧装饰条
    draw.rectangle([50, 180, 56, height - 180], fill=(255, 255, 255))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"封面图已生成（备用模式）: {output_path}")


def generate_cover(title, output_path, subtitle="萧十一说"):
    """生成封面图：优先下载 Unsplash，失败则用 PIL"""

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 优先尝试下载 Unsplash 真实照片
    if download_unsplash_cover(title, output_path, subtitle):
        return

    # 备用：PIL 生成
    generate_text_cover(title, output_path, subtitle)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 generate_cover.py <标题> <输出路径> [副标题]")
        print("示例: python3 generate_cover.py \"我的标题\" \"../outputs/2026-03-21/文章标题/imgs/cover.png\"")
        sys.exit(1)

    title = sys.argv[1]
    second_arg = sys.argv[2]
    subtitle = sys.argv[3] if len(sys.argv) > 3 else "萧十一说"

    # 智能判断：如果是完整路径（包含 .png 或英文路径），直接使用
    # 否则认为是类别名称，自动查找 outputs 目录
    is_english_path = any(c.isascii() and c not in '/\\。，、？（）【】' for c in second_arg)
    if '.png' in second_arg or is_english_path:
        output_path = second_arg
    else:
        # 如果是类别名称，自动拼接到当前目录下的 cover.png
        # 尝试查找 outputs 目录下的 imgs 文件夹
        import os
        current_dir = os.getcwd()
        # 检查是否在 scripts 目录
        if current_dir.endswith('scripts'):
            base_dir = os.path.dirname(current_dir)
        else:
            base_dir = current_dir
        
        # 查找最新的 outputs 目录
        outputs_dir = os.path.join(base_dir, 'outputs')
        if os.path.exists(outputs_dir):
            # 找最新的日期目录
            date_dirs = [d for d in os.listdir(outputs_dir) if os.path.isdir(os.path.join(outputs_dir, d))]
            if date_dirs:
                latest_date = sorted(date_dirs)[-1]
                article_dirs = os.path.join(outputs_dir, latest_date)
                if os.path.exists(article_dirs):
                    # 找文章目录
                    article_list = [d for d in os.listdir(article_dirs) if os.path.isdir(os.path.join(article_dirs, d))]
                    if article_list:
                        latest_article = sorted(article_list)[-1]
                        imgs_dir = os.path.join(article_dirs, latest_article, 'imgs')
                        os.makedirs(imgs_dir, exist_ok=True)
                        output_path = os.path.join(imgs_dir, 'cover.png')
                        print(f"自动检测到输出路径: {output_path}")
                    else:
                        output_path = os.path.join(article_dirs, 'imgs', 'cover.png')
                else:
                    output_path = "cover.png"
            else:
                output_path = "cover.png"
        else:
            output_path = "cover.png"
        print(f"已自动设置输出路径: {output_path}")

    generate_cover(title, output_path, subtitle)
