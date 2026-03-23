# wechat-article-writer

🚀 **一键创作并发布微信公众号文章的 WorkBuddy Skill**

自动化完成从选题到发布的完整工作流：选题建议 → 文章创作（2000字+）→ 封面生成 → 内容配图 → 发布到公众号草稿箱 → 存入 IMA 笔记。

---

## ✨ 功能特性

- **📝 智能选题**：根据内容日历和日期自动推荐选题
- **🤖 AI 创作**：基于个人知识库创作 2000+ 字深度文章
- **🎨 自动配图**：Unsplash/Pexels 语义搜索，每章节自动配图
- **📱 一键发布**：直接发布到微信公众号草稿箱
- **💾 自动存档**：文章自动存入 IMA 笔记备份
- **📦 开箱即用**：零外部依赖，完整自包含设计

---

## 🚀 快速开始

### 1. 安装 Skill

```bash
# 复制到 WorkBuddy skills 目录
cp -r wechat-article-writer ~/.workbuddy/skills/
```

### 2. 运行初始化检查

```bash
cd ~/.workbuddy/skills/wechat-article-writer
./scripts/init-check.sh
```

> **注意**：skill 使用相对路径，可以放在任意目录。初始化检查会自动检测当前位置。

脚本会自动检测环境并引导配置：
- ✅ 运行环境（Bun、Python3）
- ✅ 配置文件（微信公众号凭证）
- ✅ 知识库文件（用户画像、写作风格）

### 3. 开始使用

在 WorkBuddy 中直接说：
- `"发布公众号"` - 获取选题建议并创作发布
- `"写篇文章"` - 同上
- `"今天发什么好"` - 仅获取选题建议

---

## 📋 前置要求

| 项目 | 必需 | 说明 |
|------|------|------|
| Bun | ✅ | `curl -fsSL https://bun.sh/install \| bash` |
| Python3 | ✅ | macOS 自带或官网下载 |
| 微信公众号 | ✅ | 需配置 AppID 和 AppSecret |
| IMA 笔记 | ⬜ | 可选，用于自动存档 |

详细配置指南请查看 [SKILL.md](./SKILL.md)

---

## 📁 项目结构

```
wechat-article-writer/
├── SKILL.md                    # 详细使用文档
├── README.md                   # 本文件
├── config/
│   ├── .env.example           # 配置模板
│   └── .env                   # 你的凭证（不提交到 git）
├── scripts/
│   ├── init-check.sh          # 初始化检查脚本 ⭐
│   ├── publish.sh             # 发布脚本
│   ├── auto_publish.sh        # 自动发布（推荐主题）
│   ├── wechat-api.ts          # 微信公众号 API
│   ├── md-to-wechat.ts        # Markdown 转微信格式
│   ├── generate_cover.py      # 封面生成
│   ├── generate_content_imgs.py # 内容配图
│   └── ima-api.sh             # IMA 笔记 API
├── references/knowledge_base/  # 知识库
│   ├── 01_用户画像.md
│   ├── 02_个人自传.md
│   ├── 03_写作风格指南.md
│   ├── 05_文案框架库.md
│   └── 07_内容日历.md
└── outputs/                    # 文章输出目录
```

---

## 🎯 使用示例

### 示例 1：完整流程

```
用户：发布公众号

AI：📅 今日话题：职场成长

    🔥 推荐选题：
    1. 为什么老板总是不记得我的功劳？
    2. 同事升职了，为什么不是我？
    3. 如何优雅地拒绝加班？

用户：选第一个

AI：开始创作... [自动生成文章]
     [生成封面图]
     [生成内容配图]
     [发布到公众号草稿箱]
     [存入 IMA 笔记]

    ✅ 发布完成！
    📝 文章信息
    - 标题：为什么老板总是不记得我的功劳？
    - 字数：~2300 字
    - 章节数：7 个
```

### 示例 2：快速发布

```
用户：发布公众号，选题是职场沟通

AI：直接开始创作「职场沟通」主题文章...
```

---

## 🔧 配置说明

### 微信公众号凭证

1. 登录 [微信公众平台](https://mp.weixin.qq.com)
2. 开发 → 基本配置 → 获取 AppID 和 AppSecret
3. 填写到 `config/.env`

### IMA 笔记凭证（可选）

1. 访问 https://ima.qq.com/agent-interface
2. 获取 Client ID 和 API Key
3. 填写到 `config/.env`

### 知识库配置

编辑 `references/knowledge_base/` 下的文件：
- `01_用户画像.md` - 你的目标读者信息
- `02_个人自传.md` - 你的真实故事和经历
- `03_写作风格指南.md` - 你的写作风格偏好

---

## 📝 文章规范

- **字数**：2000+ 字（干货类 2500-3000 字）
- **章节**：至少 6 个主要章节
- **结构**：开头钩子 → 主体内容 → 结语总结 → 互动引导 → 参考来源
- **配图**：每章节 1 张，封面 1 张
- **结尾**：必须包含内容总结、互动引导、参考来源三模块

---

## 🐛 故障排查

| 问题 | 解决 |
|------|------|
| `bun: command not found` | 安装 Bun：`curl -fsSL https://bun.sh/install \| bash` |
| `ModuleNotFoundError` | `pip3 install Pillow requests` |
| 获取 access_token 失败 | 检查微信公众号 AppID 和 AppSecret |
| 文章没有配图 | 检查网络连接，脚本会自动降级处理 |

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

---

> **核心理念**：让用户说一句话，就能完成一篇文章的创作和发布。
