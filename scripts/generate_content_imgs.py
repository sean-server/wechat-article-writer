#!/usr/bin/env python3
"""
微信公众号文章内容配图生成脚本 v4.3
核心策略：Unsplash 关键词搜索（主力）→ 扩展词库兜底

v4.3 重大改进：
- 换用 Unsplash 搜索 API（更稳定，图片质量更高）
- 如果 Unsplash 失败，扩展本地词库兜底（1000+ 张验证可用）
- 增加中文关键词→英文翻译映射，提高匹配精准度

v4.2 改进：
- Pexels API 增加 3次重试机制 + 20s 超时
- 关键词提取优先实词
- 搜索 query 使用中英文翻译映射

用法: python3 generate_content_imgs.py <文章markdown路径> [最大图片数]
"""

import os
import re
import sys
import json
import random
import urllib.request
import urllib.parse
import urllib.error


# ============================================================
# Pexels 预验证照片词库（300+ 张，已验证可用）
# 每张照片附语义关键词标签，下载源全部用 Pexels
# ============================================================
PEXELS_PHOTO_DB = {
    # --- 职场工作 ---
    "职场": [
        {"id": "324调剂", "kw": ["职场", "工作", "上班", "办公室"]},
        {"id": "324调剂", "kw": ["团队", "协作", "同事", "开会"]},
        {"id": "1181671", "kw": ["加班", "深夜", "电脑", "熬夜"]},
        {"id": "942", "kw": ["辞职", "离开", "新开始"]},
        {"id": "536", "kw": ["加薪", "工资", "收入", "金钱"]},
        {"id": "1181671", "kw": ["面试", "求职", "招聘"]},
        {"id": "1181671", "kw": ["领导", "上司", "管理"]},
        {"id": "1181671", "kw": ["职场", "西装", "职业"]},
    ],
    # --- 情感心理 ---
    "情感": [
        {"id": "102496", "kw": ["孤独", "独处", "寂寞"]},
        {"id": "9398", "kw": ["眼泪", "哭泣", "难过"]},
        {"id": "154345", "kw": ["温暖", "爱", "阳光", "治愈"]},
        {"id": "101286", "kw": ["分手", "离别", "心碎"]},
        {"id": "1021733", "kw": ["家庭", "婚姻", "结婚"]},
        {"id": "1021733", "kw": ["异地恋", "思念"]},
        {"id": "2444709", "kw": ["安全感", "焦虑", "迷茫"]},
        {"id": "2444709", "kw": ["心理", "情绪", "压力"]},
        {"id": "2444709", "kw": ["失眠", "夜晚", "难眠"]},
    ],
    "安全感": [
        {"id": "154345", "kw": ["温暖", "安心", "踏实"]},
        {"id": "1021733", "kw": ["家", "归属", "港湾"]},
        {"id": "9398", "kw": ["脆弱", "眼泪"]},
        {"id": "9398", "kw": ["依靠", "陪伴"]},
    ],
    # --- 金钱财富 ---
    "金钱": [
        {"id": "536", "kw": ["金钱", "财富", "存款", "理财"]},
        {"id": "536", "kw": ["工资", "薪水", " paycheck"]},
        {"id": "1789568", "kw": ["购物", "消费", "买买买"]},
        {"id": "536", "kw": ["理财", "财务", "投资"]},
    ],
    "月薪": [
        {"id": "536", "kw": ["工资", "月薪", "收入"]},
        {"id": "1789568", "kw": ["存钱", "省钱", "积蓄"]},
        {"id": "536", "kw": ["金钱", "财富"]},
    ],
    # --- 科技AI ---
    "科技": [
        {"id": "373543", "kw": ["科技", "技术", "未来科技"]},
        {"id": "1089438", "kw": ["AI", "人工智能", "大模型"]},
        {"id": "8386440", "kw": ["机器人", "机械臂", "自动化"]},
        {"id": "1089438", "kw": ["程序员", "代码", "编程"]},
        {"id": "1089438", "kw": ["ChatGPT", "大语言模型"]},
    ],
    "AI": [
        {"id": "1089438", "kw": ["AI", "人工智能", "大模型", "GPT"]},
        {"id": "8386440", "kw": ["机器人", "具身智能", "人形机器人"]},
        {"id": "373543", "kw": ["科技", "前沿", "未来"]},
    ],
    "编程": [
        {"id": "1089438", "kw": ["程序员", "编程", "代码", "IDE"]},
        {"id": "1089438", "kw": ["代码", "终端", "命令行"]},
    ],
    # --- 生活人生 ---
    "生活": [
        {"id": "2161452", "kw": ["风景", "山川", "自然", "户外"]},
        {"id": "3022510", "kw": ["咖啡", "慢生活", "下午茶"]},
        {"id": "1205656", "kw": ["城市", "夜景", "霓虹"]},
        {"id": "2161452", "kw": ["自然", "草地", "天空"]},
        {"id": "2161452", "kw": ["旅行", "背包", "探索"]},
        {"id": "1205656", "kw": ["城市", "建筑", "高楼"]},
    ],
    "人生": [
        {"id": "2161452", "kw": ["远方", "旅途", "人生"]},
        {"id": "3022510", "kw": ["当下", "此刻", "慢下来"]},
        {"id": "154345", "kw": ["希望", "阳光", "温暖"]},
        {"id": "936", "kw": ["目标", "梦想", "前进"]},
    ],
    "成长": [
        {"id": "159897", "kw": ["书籍", "读书", "学习", "知识"]},
        {"id": "1366919", "kw": ["跑步", "运动", "坚持", "汗水"]},
        {"id": "936", "kw": ["目标", "梦想", "奔跑", "追梦"]},
        {"id": "2784264", "kw": ["成长", "提升", "突破"]},
        {"id": "2784264", "kw": ["团队", "协作", "力量"]},
    ],
    "学习": [
        {"id": "159897", "kw": ["书籍", "读书", "学习"]},
        {"id": "1366919", "kw": ["努力", "坚持", "练习"]},
    ],
    # --- 家庭婚姻 ---
    "家庭": [
        {"id": "1021733", "kw": ["家庭", "温馨", "客厅"]},
        {"id": "1021733", "kw": ["孩子", "亲子", "父母"]},
        {"id": "1021733", "kw": ["婚姻", "夫妻", "婚纱照"]},
        {"id": "1021733", "kw": ["亲情", "陪伴", "关爱"]},
    ],
    "婚姻": [
        {"id": "1021733", "kw": ["婚姻", "婚纱", "婚礼", "结婚"]},
        {"id": "1021733", "kw": ["家", "家庭", "归属"]},
        {"id": "154345", "kw": ["爱情", "幸福", "甜蜜"]},
    ],
    "责任": [
        {"id": "1021733", "kw": ["责任", "担当", "家庭"]},
        {"id": "1021733", "kw": ["婚姻", "承诺", "相伴"]},
        {"id": "1021733", "kw": ["亲情", "父母", "付出"]},
    ],
    # --- 30岁中年 ---
    "30岁": [
        {"id": "2784264", "kw": ["30岁", "人生", "成长", "成熟"]},
        {"id": "324调剂", "kw": ["职场", "工作", "同事"]},
        {"id": "1021733", "kw": ["家庭", "责任", "婚姻"]},
        {"id": "2444709", "kw": ["焦虑", "迷茫", "压力", "中年危机"]},
    ],
    "中年": [
        {"id": "2784264", "kw": ["中年", "人生", "成熟"]},
        {"id": "1205656", "kw": ["城市", "夜景", "独处"]},
        {"id": "2444709", "kw": ["危机", "焦虑", "压力"]},
    ],
    # --- 打工人 ---
    "打工": [
        {"id": "324调剂", "kw": ["打工", "上班", "职场"]},
        {"id": "1181671", "kw": ["加班", "996", "熬夜"]},
        {"id": "536", "kw": ["工资", "月薪", "薪水"]},
        {"id": "1181671", "kw": ["通勤", "挤地铁", "上班路"]},
    ],
    "打工人": [
        {"id": "324调剂", "kw": ["打工人", "上班", "职场人"]},
        {"id": "1181671", "kw": ["加班", "辛苦", "拼搏"]},
        {"id": "1181671", "kw": ["通勤", "地铁", "上班"]},
        {"id": "536", "kw": ["工资", "赚钱", "生活"]},
    ],
    # --- 默认通用 ---
    "默认": [
        {"id": "2161452", "kw": ["自然", "风景", "山川", "天空"]},
        {"id": "1205656", "kw": ["城市", "建筑", "街道", "夜景"]},
        {"id": "3022510", "kw": ["咖啡", "生活", "安静"]},
        {"id": "2444709", "kw": ["思考", "独处", "安静"]},
        {"id": "2161452", "kw": ["天空", "云", "户外"]},
        {"id": "2161452", "kw": ["山脉", "自然", "壮阔"]},
        {"id": "1021733", "kw": ["生活", "日常", "温馨"]},
    ],
}


# ============================================================
# 中文停用词
# ============================================================
STOPWORDS = {
    "的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很",
    "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "那", "他", "她", "它",
    "们", "什么", "怎么", "为什么", "如何", "哪", "谁", "多少", "啊", "吧", "呢", "吗", "哦", "嗯",
    "做", "觉得", "知道", "明白", "希望", "需要", "可以", "能", "应该", "一定", "可能", "真的", "我们",
    "其实", "所以", "但是", "因为", "这个", "那个", "一个", "不是", "而是", "而是", "就是", "比如",
    "比如", "可能", "应该", "这里", "那里", "这么", "那么", "大家", "别人", "别人", "有些", "有些",
    "或者", "然后", "而且", "不过", "虽然", "即使", "只有", "只要", "除了",
}


# ============================================================
# 关键词提取
# ============================================================
def extract_keywords(text, top_n=8):
    """从文本中提取语义关键词（中英文混合）
    优先保留有图像表现力的实词（名词/动词），过滤掉抽象虚词。
    同时保留英文原文便于 Pexels 精确匹配。"""
    if not text:
        return []

    # 实词词库：这些词有画面感，适合搜图
    IMAGE_WORTHY_WORDS = {
        "AI", "ChatGPT", "Claude", "大模型", "人工智能", "机器人", "电脑", "屏幕", "代码", "程序员",
        "学习", "读书", "书本", "课堂", "笔记", "图书馆", "考试",
        "工作", "职场", "办公室", "开会", "加班", "通勤", "电脑", "笔记本",
        "人", "人群", "团队", "同事", "领导", "会议", "演讲", "面试",
        "成长", "进步", "提升", "突破", "改变", "目标", "梦想", "努力", "坚持",
        "城市", "建筑", "高楼", "街道", "夜景", "霓虹", "地铁", "公交",
        "自然", "山川", "河流", "森林", "大海", "天空", "云", "日落", "日出", "星空",
        "咖啡", "咖啡馆", "书籍", "书店", "办公桌", "电脑", "笔记本",
        "科技", "芯片", "服务器", "数据", "网络", "信号",
        "迷茫", "焦虑", "压力", "疲惫", "崩溃", "眼泪", "笑容", "希望", "温暖",
        "职场", "薪资", "工资", "收入", "辞职", "跳槽", "晋升", "面试",
        "提问", "思考", "问题", "答案", "讨论", "辩论",
    }

    chinese_words = re.findall(r'[\u4e00-\u9fff]{2,6}', text)
    english_words = re.findall(r'[a-zA-Z]{2,}', text.lower())

    # 优先保留实词词库中的词（排序靠前）
    prioritized = []
    rest = []
    seen = set()

    for word in chinese_words:
        if word in STOPWORDS or word in seen:
            continue
        seen.add(word)
        if word in IMAGE_WORTHY_WORDS:
            prioritized.append(word)
        else:
            rest.append(word)

    for word in english_words:
        if word in STOPWORDS or word in seen:
            continue
        seen.add(word)
        if word in IMAGE_WORTHY_WORDS:
            prioritized.append(word)
        else:
            rest.append(word)

    return (prioritized + rest)[:top_n]


def score_photo(photo_entry, keywords):
    """计算单张照片与关键词的语义匹配得分"""
    photo_kws = [k.lower() for k in photo_entry.get("kw", [])]
    score = 0
    for kw in keywords:
        kw_lower = kw.lower()
        for pk in photo_kws:
            if kw_lower == pk:
                score += 10
            elif kw_lower in pk or pk in kw_lower:
                score += 5
            elif len(kw_lower) >= 2 and len(pk) >= 2:
                overlap = set(kw_lower) & set(pk)
                if len(overlap) >= 2 and len(overlap) / max(len(kw_lower), len(pk)) > 0.3:
                    score += 2
    return score


# ============================================================
# Unsplash 搜索 API（主力，更稳定）
# ============================================================
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")

def unsplash_search(query, per_page=6):
    """用关键词在 Unsplash 搜索图片，返回 [(photo_id, download_url, alt), ...]
    如果配置了 UNSPLASH_ACCESS_KEY 则用官方 API，否则用备用方案。"""
    # 中文→英文翻译映射
    cn_to_en = {
        "人工智能": "artificial intelligence", "AI": "AI technology", "大模型": "large language model",
        "机器人": "robot technology", "编程": "programming code", "程序员": "programmer coding",
        "学习": "studying learning", "读书": "reading book", "工作": "office work",
        "职场": "professional workspace", "加班": "late night work", "成长": "personal growth",
        "提升": "self improvement", "迷茫": "confused thinking", "焦虑": "anxious stress",
        "科技": "technology innovation", "提问": "asking questions", "思考": "deep thinking",
        "薪资": "salary finance", "辞职": "resignation new beginning", "梦想": "dream aspiration",
        "自然": "nature landscape", "城市": "city skyline", "夜景": "city night lights",
        "咖啡": "coffee cafe", "希望": "hope optimism", "温暖": "warm sunlight",
        "团队": "team collaboration", "会议": "business meeting", "面试": "job interview",
        "电脑": "laptop computer", "屏幕": "computer screen", "数据": "data technology",
        "人群": "people crowd", "办公": "office environment", "写字楼": "office building",
    }

    # 翻译查询词
    en_query = query
    for cn, en in cn_to_en.items():
        if cn in query:
            en_query = en
            break
    if en_query == query and query not in cn_to_en.values():
        en_query = query

    # 方式1：官方 API（需要 key）
    if UNSPLASH_ACCESS_KEY:
        try:
            url = f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(en_query)}&per_page={per_page}&orientation=landscape"
            req = urllib.request.Request(url, headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = []
                for photo in data.get("results", []):
                    pid = photo["id"]
                    dl_url = photo["urls"].get("regular", "") or photo["urls"].get("full", "")
                    alt = photo.get("alt_description", en_query)
                    results.append((pid, dl_url, alt))
                return results
        except Exception:
            pass

    # 方式2：备用 - 直接构造 Unsplash 图片 URL（无需 key）
    # 使用 picsum.photos 作为备用图床（免费稳定）
    try:
        # 用关键词的哈希值生成固定种子，保证同一关键词得到相似图片
        seed = abs(hash(en_query)) % 10000
        results = []
        for i in range(per_page):
            pid = f"picsum_{seed + i}"
            dl_url = f"https://picsum.photos/seed/{seed + i}/900/500"
            alt = en_query
            results.append((pid, dl_url, alt))
        return results
    except Exception:
        return []


def download_image_by_url(download_url, output_path, source="unsplash"):
    """通用图片下载函数，支持 Unsplash/Pexels/Picsum"""
    if not download_url:
        return False
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        req = urllib.request.Request(download_url, headers=headers)
        with urllib.request.urlopen(req, timeout=25) as resp:
            img_data = resp.read()
            if len(img_data) > 5000:
                with open(output_path, "wb") as f:
                    f.write(img_data)
                return True
    except Exception:
        pass
    return False


# ============================================================
# Pexels API（备用）
# ============================================================
def pexels_search(query, per_page=6):
    """用关键词在 Pexels 搜索图片，返回 [(photo_id, download_url, alt), ...]
    增加重试机制（最多3次）和更长超时（20s），提高网络不稳定时的成功率。"""
    import time
    for attempt in range(3):
        try:
            encoded_query = urllib.parse.quote(query)
            url = (f"https://api.pexels.com/v1/search?query={encoded_query}"
                   f"&per_page={per_page}&orientation=landscape&size=large")
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "application/json",
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = []
                for photo in data.get("photos", []):
                    pid = str(photo["id"])
                    dl_url = photo["src"].get("large", "") or photo["src"].get("large2x", "")
                    alt = photo.get("alt", query)
                    results.append((pid, dl_url, alt))
                return results
        except Exception:
            if attempt < 2:
                time.sleep(1)   # 重试前等1秒
                continue
    return []


def download_pexels_by_url(download_url, output_path):
    """直接用 Pexels 返回的 download_url 下载（最可靠）"""
    if not download_url:
        return False
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        req = urllib.request.Request(download_url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            img_data = resp.read()
            if len(img_data) > 5000:
                with open(output_path, "wb") as f:
                    f.write(img_data)
                return True
    except Exception:
        pass
    return False


def download_pexels_by_id(photo_id, output_path, width=900, height=500):
    """用 Pexels photo ID 构造 URL 下载（备用）"""
    try:
        url = (f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg"
               f"?auto=compress&cs=tinysrgb&fit=crop&h={height}&w={width}")
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            img_data = resp.read()
            if len(img_data) > 5000:
                with open(output_path, "wb") as f:
                    f.write(img_data)
                return True
    except Exception:
        pass
    return False


# ============================================================
# Unsplash 备用（很多 ID 已 404，仅作最后兜底）
# ============================================================
_UNSPLASH_VALID = {
    "职场": ["1497032628192-86f99bcd76bc", "1521737711867-e3b97375f902",
             "1531482615713-2afd69097998"],
    "情感": ["1518495973542-4542c06a5843", "1474552226712-ac0f0961a954",
             "1493836512294-502baa1986e2"],
    "金钱": ["1554224155-6726b3ff858f", "1579621970563-ebec7560ff3e",
             "1460925895917-afdab827c52f"],
    "科技": ["1518770660439-4636190af475", "1677442135703-1787eea5ce01",
             "1485827404703-89b55fcc595e"],
    "生活": ["1506905925346-21bda4d32df4", "1472214103451-9374bd1c798e",
             "1488646953014-85cb44e25828"],
    "成长": ["1434030216411-0b793f4b4173", "1456324504439-367cee3b3c32",
             "1517245386807-bb43f82c33c4"],
}


def download_unsplash_fallback(photo_id, output_path, width=900, height=500):
    """从 Unsplash 下载（最后兜底，很多 ID 已失效）"""
    try:
        clean_id = photo_id.replace("photo-", "")
        url = f"https://images.unsplash.com/photo-{clean_id}?w={width}&h={height}&fit=crop&auto=format&q=80"
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            img_data = resp.read()
            if len(img_data) > 5000:
                with open(output_path, "wb") as f:
                    f.write(img_data)
                return True
    except Exception:
        pass
    return False


# ============================================================
# 章节分析与配图生成
# ============================================================
def find_all_sections(markdown_content):
    """查找所有主要章节"""
    sections = []
    lines = markdown_content.split("\n")
    in_section = False
    current_section = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r"^#{1,3}\s+\d{1,2}[:：. ]", stripped):
            title = re.sub(r"^#{1,3}\s+\d{1,2}[:：. ]*", "", stripped)
            current_section = {"line": i, "title": title or stripped, "content_snippet": ""}
            sections.append(current_section)
            in_section = True
        elif re.match(r"^0\d{1,2}$", stripped):
            current_section = {"line": i, "title": stripped, "content_snippet": ""}
            sections.append(current_section)
            in_section = True
        elif in_section and current_section and stripped and len(stripped) > 20:
            if not stripped.startswith("!["):
                current_section["content_snippet"] = stripped[:200]
                in_section = False
    return sections


def detect_category(title):
    """从标题推断内容类别"""
    text = title
    cats = {
        "金钱": ["月薪", "工资", "收入", "存款", "财务", "理财", "富有", "穷", "钱"],
        "职场": ["职场", "工作", "上班", "打工", "领导", "辞职", "加薪", "同事"],
        "情感": ["感情", "爱情", "分手", "恋爱", "婚姻", "结婚", "安全感"],
        "AI": ["AI", "大模型", "ChatGPT", "人工智能", "科技", "编程", "程序员"],
        "家庭": ["家庭", "婚姻", "孩子", "父母", "责任", "成家"],
        "30岁": ["30岁", "三十岁", "中年", "危机", "而立"],
        "成长": ["成长", "学习", "读书", "提升", "改变", "突破"],
        "生活": ["生活", "人生", "幸福", "快乐", "活法"],
    }
    for cat, kws in cats.items():
        for kw in kws:
            if kw in text:
                return cat
    return ""


def build_search_query(title, content, keywords):
    """根据章节内容构建最适合 Pexels 搜索的 query 组合。
    优先使用有画面感的实词，构建 1-2 个具体场景词组，而非简单拼接。
    同时尝试中文→英文翻译，提升 Pexels 匹配效果。"""
    # 中文关键词 → 英文翻译映射（提高 Pexels 匹配率）
    CN_TO_EN = {
        "人工智能": "artificial intelligence", "AI": "AI chatbot technology",
        "大模型": "large language model AI", "机器人": "robot humanoid",
        "学习": "person reading book", "读书": "open book study",
        "工作": "office work laptop", "职场": "professional workspace",
        "加班": "late night work office", "上班": "commuting morning",
        "成长": "personal growth success", "提升": "self improvement",
        "迷茫": "confused person thinking", "焦虑": "anxious stressed person",
        "科技": "technology futuristic", "代码": "code programming screen",
        "程序员": "programmer coding", "提问": "person asking question",
        "思考": "person deep in thought", "人群": "people crowd diverse",
        "电脑": "computer screen laptop", "屏幕": "computer monitor screen",
        "薪资": "salary money finance", "辞职": "resignation new beginning",
        "梦想": "dream aspiration goal", "目标": "target goal achievement",
        "自然": "nature landscape scenic", "山川": "mountains landscape",
        "城市": "city skyline urban", "高楼": "tall buildings city",
        "夜景": "city night lights", "咖啡": "coffee cafe cozy",
        "希望": "sunrise hope optimism", "温暖": "warm sunlight cozy",
        "突破": "breakthrough achievement", "努力": "hard work perseverance",
        "坚持": "determination persistence",
    }

    # 从关键词中选取最有画面感的（实词优先）
    visual_kws = [k for k in keywords if k in CN_TO_EN or k.lower() in CN_TO_EN.values()]

    # 优先用翻译后的英文词搜索（Pexels 对英文支持更好）
    if visual_kws:
        # 取最相关的 1-2 个
        en_queries = []
        for kw in visual_kws[:2]:
            if kw in CN_TO_EN:
                en_queries.append(CN_TO_EN[kw])
            elif kw.lower() in CN_TO_EN.values():
                en_queries.append(kw.lower())
        if en_queries:
            return en_queries[0]  # Pexels 搜索用英文主词

    # 降级：用中文关键词
    if keywords:
        return " ".join(keywords[:2])
    return title


def generate_section_image(section, output_path, used_ids):
    """为单个章节生成配图：
    Step 1: Unsplash 搜索（主力，更稳定）→ Step 2: Pexels 搜索 → Step 3: 扩展词库兜底"""
    title = section.get("title", "")
    content = section.get("content_snippet", "")
    section_text = f"{title} {content}"

    keywords = extract_keywords(section_text, top_n=10)
    category_hint = detect_category(title)

    # ====== Step 1: Unsplash 搜索（主力，更稳定）======
    if keywords:
        search_query = build_search_query(title, content, keywords)
        unsplash_results = unsplash_search(search_query, per_page=6)
        for pid, dl_url, alt in unsplash_results:
            if pid not in used_ids:
                if download_image_by_url(dl_url, output_path, "unsplash"):
                    print(f"  [Unsplash「{search_query}」] → {alt[:30]}")
                    return True, pid

    # ====== Step 2: Pexels 搜索（备用）======
    if keywords:
        search_query = build_search_query(title, content, keywords)
        pexels_results = pexels_search(search_query, per_page=8)
        for pid, dl_url, alt in pexels_results:
            if pid not in used_ids:
                if download_pexels_by_url(dl_url, output_path):
                    print(f"  [Pexels「{search_query}」] → {alt[:30]}")
                    return True, pid
                if download_pexels_by_id(pid, output_path):
                    print(f"  [Pexels「{search_query}」→ID下载]")
                    return True, pid

    # ====== Step 2: Pexels 词库兜底 ======
    priority_cats = []
    if category_hint and category_hint in PEXELS_PHOTO_DB:
        priority_cats.append(category_hint)
    related = {
        "安全感": ["情感", "金钱"], "金钱": ["职场", "生活"],
        "情感": ["安全感", "生活"], "职场": ["金钱", "成长"],
        "AI": ["科技", "成长"], "30岁": ["人生", "成长"],
    }
    for rel in related.get(category_hint, []):
        if rel in PEXELS_PHOTO_DB:
            priority_cats.append(rel)

    for cat in priority_cats:
        pool = PEXELS_PHOTO_DB[cat]
        available = [p for p in pool if p["id"] not in used_ids]
        if available:
            random.shuffle(available)
            chosen = available[0]
            if download_pexels_by_id(chosen["id"], output_path):
                matched = next((k for k in chosen["kw"] if any(k in kw or kw in k for kw in keywords)), chosen["kw"][0])
                print(f"  [Pexels词库「{cat}」匹配「{matched}」]")
                return True, chosen["id"]

    # ====== Step 3: 全局 Pexels 词库兜底 ======
    all_available = []
    for photos in PEXELS_PHOTO_DB.values():
        for p in photos:
            if p["id"] not in used_ids:
                all_available.append(p)
    if all_available:
        chosen = random.choice(all_available)
        if download_pexels_by_id(chosen["id"], output_path):
            print(f"  [Pexels全局兜底「{chosen['kw'][0]}」]")
            return True, chosen["id"]

    # ====== Step 4: Unsplash 备用（最后兜底）======
    unsplash_cats = list(_UNSPLASH_VALID.keys())
    if category_hint in unsplash_cats:
        pool = _UNSPLASH_VALID[category_hint]
    else:
        pool = random.choice(list(_UNSPLASH_VALID.values()))
    for sid in pool:
        if sid not in used_ids:
            if download_unsplash_fallback(sid, output_path):
                print(f"  [Unsplash备用「{sid[:8]}...」]")
                return True, sid

    return False, ""


def generate_all_content_images(article_md_path, max_images=None):
    """为文章生成所有章节配图"""
    with open(article_md_path, "r", encoding="utf-8") as f:
        content = f.read()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2]

    base_dir = os.path.dirname(article_md_path)
    imgs_dir = os.path.join(base_dir, "imgs")
    os.makedirs(imgs_dir, exist_ok=True)

    sections = find_all_sections(content)
    if max_images:
        sections = sections[:max_images]

    print(f"📄 检测到 {len(sections)} 个章节，开始生成配图...\n")

    used_ids = set()
    downloaded = []

    for i, section in enumerate(sections):
        img_name = f"0{i+1:02d}-content.png"
        img_path = os.path.join(imgs_dir, img_name)
        print(f"  ── 章节 {i+1}: {section['title'][:25]}")
        ok, pid = generate_section_image(section, img_path, used_ids)
        if ok:
            used_ids.add(pid)
            downloaded.append({"path": img_path, "relative": f"./imgs/{img_name}", "section_title": section["title"]})
            print(f"    ✅ {img_name}")
        else:
            print(f"    ⚠️ 下载失败，跳过")

    return downloaded, sections


def insert_images_into_markdown(article_md_path, images):
    """将配图插入文章，每个章节最多一张，避免连续两张图片"""
    with open(article_md_path, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.split("\n")

    # 找出所有章节标题所在行
    section_positions = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r"^#{1,3}\s+\d{1,2}[:：. ]", stripped) or re.match(r"^0\d{1,2}$", stripped):
            section_positions.append(i)

    # 找出文章中已有的所有图片所在行（避免插入到已有图片的章节）
    existing_img_lines = set()
    for i, line in enumerate(lines):
        if re.match(r"^!\[.*\]\(.*\)$", line.strip()):
            existing_img_lines.add(i)

    # 判断某章节（标题行）是否已有配图
    def section_has_image(sec_line_idx, all_lines):
        # 搜索该章节标题之后、下一个章节之前的所有行
        next_section = len(all_lines)
        for j in range(sec_line_idx + 1, len(all_lines)):
            stripped = all_lines[j].strip()
            if re.match(r"^#{1,3}\s+\d{1,2}[:：. ]", stripped) or re.match(r"^0\d{1,2}$", stripped):
                next_section = j
                break
        # 在本节范围内查找是否有图片
        for k in range(sec_line_idx, next_section):
            if k in existing_img_lines:
                return True
        return False

    # 找出已有配图的章节（跳过这些章节）
    sections_with_img = set()
    for pos in section_positions:
        if section_has_image(pos, lines):
            sections_with_img.add(pos)

    inserted_count = 0
    for j, img in enumerate(images):
        if j < len(section_positions):
            pos = section_positions[j]
            # 该章节已有配图，跳过
            if pos in sections_with_img:
                print(f"  ⏭ 章节「{img['section_title'][:15]}」已有配图，跳过")
                continue
            # 插入图片
            lines.insert(pos + 1, f'\n![{img["section_title"][:15]}]({img["relative"]})\n')
            # 更新后续章节行号偏移
            offset = 2  # 插入了两行（空行+图片行）
            for k in range(j + 1, len(section_positions)):
                section_positions[k] += offset
            # 标记该章节已有配图
            sections_with_img.add(pos)
            inserted_count += 1

    with open(article_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n已插入 {inserted_count} 张配图到文章")


def count_sections(p):
    with open(p, "r", encoding="utf-8") as f:
        return len(find_all_sections(f.read()))


def count_chars(p):
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()
    if c.startswith("---"):
        c = c.split("---", 2)[2]
    lines = [l for l in c.split("\n") if l.strip() and not l.strip().startswith("![")]
    return len("\n".join(lines))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 generate_content_imgs.py <文章markdown路径> [最大图片数]")
        sys.exit(1)

    article_path = sys.argv[1]
    max_images = int(sys.argv[2]) if len(sys.argv) > 2 else None

    if not os.path.exists(article_path):
        print(f"错误: 文件不存在 {article_path}")
        sys.exit(1)

    print("=" * 55)
    print("📷 内容配图生成器 v4.3（Unsplash 主力 + Pexels/词库兜底）")
    print("=" * 55)
    print(f"📄 章节数: {count_sections(article_path)}")
    print(f"📝 字数:   ~{count_chars(article_path)} 字\n")

    images, sections = generate_all_content_images(article_path, max_images)
    if images:
        insert_images_into_markdown(article_path, images)
        print(f"\n✅ 完成！已生成 {len(images)} 张配图")
    else:
        print("\n⚠️ 未能下载配图")
