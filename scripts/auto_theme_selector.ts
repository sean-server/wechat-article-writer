#!/usr/bin/env bun
/**
 * 智能主题推荐系统
 * 根据文章内容自动推荐最合适的排版主题
 * 
 * 主题命名规则：
 * - 4种基础主题 × 12种颜色 = 48种视觉风格
 * - 每种组合有一个有创意的名称
 */

interface ThemeRecommendation {
  theme: string;
  color: string;
  name: string;
  description: string;
  reason: string;
}

// 主题风格库
const THEMES = {
  // 现代简洁风
  modern: {
    name: '现代简洁',
    description: '大圆角、胶囊标题、宽松行距',
    bestFor: ['干货方法', '职场成长', '科技趋势']
  },
  // 优雅精致风
  grace: {
    name: '优雅精致',
    description: '文字阴影、圆角卡片、精美引用',
    bestFor: ['情感故事', '生活感悟', '深度分析']
  },
  // 经典传统风
  default: {
    name: '经典传统',
    description: '居中标题、底部边框、H2彩色背景',
    bestFor: ['热点评论', '清单盘点', '观点输出']
  },
  // 简约极简风
  simple: {
    name: '简约极简',
    description: '不对称圆角、大量留白、现代简约',
    bestFor: ['故事感悟', '轻松话题', '周末休闲']
  }
};

// 颜色调性库
const COLORS: Record<string, { name: string; vibe: string; emotions: string[] }> = {
  'red': { name: '中国红', vibe: '传统、正式、喜庆', emotions: ['热血', '激情', '传统'] },
  'blue': { name: '藏蓝', vibe: '专业、稳重、信任', emotions: ['专业', '理性', '严肃'] },
  'emerald': { name: '翡翠绿', vibe: '自然、生机、成长', emotions: ['希望', '成长', '自然'] },
  'vermilion': { name: '朱砂红', vibe: '活力、热情、醒目', emotions: ['活力', '热情', '冲动'] },
  'yellow': { name: '柠檬黄', vibe: '明快、活泼、年轻', emotions: ['轻松', '愉快', '年轻'] },
  'purple': { name: '薰衣草紫', vibe: '浪漫、优雅、神秘', emotions: ['浪漫', '优雅', '感性'] },
  'sky': { name: '天空蓝', vibe: '清新、自由、开阔', emotions: ['自由', '清新', '梦想'] },
  'rose': { name: '玫瑰金', vibe: '温柔、精致、时尚', emotions: ['温柔', '精致', '浪漫'] },
  'olive': { name: '橄榄绿', vibe: '自然、低调、质感', emotions: ['自然', '质感', '低调'] },
  'black': { name: '石墨黑', vibe: '高级、酷感、现代', emotions: ['高级', '酷感', '现代'] },
  'gray': { name: '烟灰色', vibe: '中性、优雅、百搭', emotions: ['优雅', '中性', '百搭'] },
  'pink': { name: '樱花粉', vibe: '甜美、温柔、少女', emotions: ['甜美', '温柔', '少女'] },
  'orange': { name: '暖橙色', vibe: '温暖、活力、友好', emotions: ['温暖', '活力', '友好'] }
};

// 文章类型关键词映射
const ARTICLE_TYPE_KEYWORDS = {
  '职场成长': {
    keywords: ['职场', '工作', '领导', '同事', '辞职', '加薪', '面试', '开会', '工资', '打工', '晋升', '跳槽', '职业', '技能', '效率', '时间管理', '学习', '成长', '改变', '突破', '认知', '思维', '努力', '坚持', '习惯', '目标', '迷茫', '焦虑', '沟通', '汇报', '方案', 'KPI', '绩效', '裁员', '招聘', 'HR', '入职', '离职', '加班', '下班', '出差'],
    theme: 'modern',
    colors: ['blue', 'emerald', 'black']
  },
  '情感故事': {
    keywords: ['感情', '爱情', '恋爱', '分手', '异地恋', '婚姻', '家庭', '结婚', '另一半', '崩溃', '焦虑', '安全感', '眼泪', '委屈', '心累', '孤独', '陪伴', '理解', '沟通', '珍惜', '遗憾', '后悔', '眼泪', '温暖', '幸福'],
    theme: 'grace',
    colors: ['#B76E79', '#FFB7C5', '#92617E']
  },
  '科技趋势': {
    keywords: ['AI', '科技', '技术', '互联网', '创业', '程序员', '数据', '智能', '未来', '数字化', '算法', '模型', 'ChatGPT', '大模型', '机器人', '自动化', '创新', '趋势', '行业', '产品'],
    theme: 'modern',
    colors: ['blue', '#55C9EA', '#333333']
  },
  '热点评论': {
    keywords: ['热点', '新闻', '事件', '热搜', '话题', '现象', '讨论', '观点', '看法', '角度', '解读', '分析', '真相', '内幕', '揭秘', '为什么', '怎么回事'],
    theme: 'default',
    colors: ['red', '#FA5151', '#D97757']
  },
  '生活休闲': {
    keywords: ['生活', '人生', '活法', '幸福', '快乐', '朋友', '社交', '旅行', '周末', '休息', '放松', '爱好', '兴趣', '美食', '运动', '健康', '睡眠', '习惯'],
    theme: 'simple',
    colors: ['orange', 'yellow', 'emerald']
  },
  '干货方法': {
    keywords: ['方法', '技巧', '攻略', '秘诀', '绝招', '步骤', '流程', '清单', '指南', '建议', '教你', '如何', '怎么', '必备', '收藏', '干货'],
    theme: 'modern',
    colors: ['blue', 'emerald', 'olive']
  },
  '清单盘点': {
    keywords: ['盘点', '总结', '清单', 'Top', '10个', '5个', '8个', '排行榜', '最值', '必看', '必读', '合集', '汇总'],
    theme: 'default',
    colors: ['#FA5151', '#D97757', '#FECE00']
  },
  '故事感悟': {
    keywords: ['故事', '经历', '感悟', '体会', '顿悟', '明白', '想通', '曾经', '那年', '后来', '现在', '当时', '回忆', '过去', '成长'],
    theme: 'simple',
    colors: ['#B76E79', '#A9A9A9', '#92617E']
  },
  '深度分析': {
    keywords: ['分析', '研究', '原因', '本质', '底层', '逻辑', '为什么', '是什么', '探讨', '解读', '思考', '认知', '洞察', '理解', '解密'],
    theme: 'grace',
    colors: ['blue', '#333333', '#556B2F']
  },
  '轻松话题': {
    keywords: ['轻松', '有趣', '好玩', '搞笑', '幽默', '段子', '笑', '开心', '快乐', '娱乐', '八卦', '吐槽', '调侃'],
    theme: 'simple',
    colors: ['#FECE00', '#FFB7C5', '#D97757']
  }
};

// 根据文章内容分析文章类型
function analyzeArticleType(content: string): { type: string; score: number }[] {
  const scores: { type: string; score: number }[] = [];
  
  for (const [type, config] of Object.entries(ARTICLE_TYPE_KEYWORDS)) {
    let score = 0;
    for (const keyword of config.keywords) {
      // 统计关键词出现次数
      const regex = new RegExp(keyword, 'gi');
      const matches = content.match(regex);
      if (matches) {
        score += matches.length;
      }
    }
    if (score > 0) {
      scores.push({ type, score });
    }
  }
  
  // 按得分排序
  return scores.sort((a, b) => b.score - a.score);
}

// 颜色别名到 hex 的映射
const COLOR_ALIAS_TO_HEX: Record<string, string> = {
  'red': '#A93226',
  'blue': '#0F4C81',
  'emerald': '#009874',
  'vermilion': '#FA5151',
  'yellow': '#FECE00',
  'purple': '#92617E',
  'sky': '#55C9EA',
  'rose': '#B76E79',
  'olive': '#556B2F',
  'black': '#333333',
  'gray': '#A9A9A9',
  'pink': '#FFB7C5',
  'orange': '#D97757'
};

// 获取实际使用的颜色（可能是 hex 或别名）
function getActualColor(color: string): string {
  return COLOR_ALIAS_TO_HEX[color] || color;
}

// 获取主题风格名称
function getThemeStyleName(theme: string, color: string): string {
  const themeStyles: Record<string, Record<string, string>> = {
    modern: {
      'emerald': '🌿 清新自然风',
      'blue': '💙 理性科技风',
      'black': '⚫ 高级极客风',
      'vermilion': '❤️ 活力醒目风',
      'orange': '🧡 温暖生活风',
      'yellow': '💛 明亮快活风',
      'purple': '💜 神秘优雅风',
      'sky': '💙 天空自由风',
      'rose': '💖 温柔玫瑰风',
      'olive': '🫒 质感森系风',
      'gray': '⚪ 低调简约风',
      'pink': '🌸 甜美清新风'
    },
    grace: {
      'rose': '🌹 优雅玫瑰风',
      'pink': '🌸 温柔樱花风',
      'purple': '💜 神秘紫罗兰风',
      'blue': '💎 沉稳蓝宝石风',
      'black': '🖤 酷感黑曜石风',
      'emerald': '💚 翡翠意境风',
      'vermilion': '🔴 热情石榴风',
      'orange': '🍊 暖阳秋日风',
      'sky': '💙 清新薄荷风',
      'olive': '🌲 森林静谧风',
      'gray': '🤍 优雅灰珍珠风',
      'yellow': '🌻 向日葵田园风'
    },
    default: {
      'red': '🏮 经典中国风',
      'vermilion': '🔥 热血复古风',
      'orange': '🍂 复古暖色风',
      'yellow': '☀️ 明亮复古风',
      'blue': '📘 传统蓝调风',
      'emerald': '🏵️ 古典绿韵风',
      'black': '📰 报纸怀旧风',
      'purple': '🎭 复古文艺风',
      'rose': '💄 复古玫瑰风',
      'sky': '🌊 清新海洋风',
      'gray': '📜 复古纸质感风',
      'olive': '🍃 复古绿植风'
    },
    simple: {
      'black': '⚫ 极简黑武士风',
      'gray': '⚪ 极简水泥风',
      'emerald': '🌿 极简森呼吸风',
      'sky': '💨 极简天空风',
      'orange': '🧡 极简暖阳风',
      'pink': '🌸 极简樱花风',
      'blue': '🔵 极简蓝天风',
      'yellow': '🌟 极简明快风',
      'vermilion': '❤️ 极简醒目风',
      'purple': '💜 极简紫罗兰风',
      'rose': '💖 极简玫瑰风',
      'olive': '🌲 极简森林风'
    }
  };
  
  return themeStyles[theme]?.[color] || `${theme}-${color}`;
}

// 主推荐函数
export function recommendTheme(articlePath: string): ThemeRecommendation {
  // 读取文章内容
  const fs = require('fs');
  const content = fs.readFileSync(articlePath, 'utf-8');
  
  // 提取正文（去掉 frontmatter）
  const bodyMatch = content.match(/^---\n[\s\S]*?\n---\n([\s\S]*)$/);
  const body = bodyMatch ? bodyMatch[1] : content;
  
  // 分析文章类型
  const typeScores = analyzeArticleType(body);
  
  if (typeScores.length === 0) {
    // 默认推荐
    return {
      theme: 'modern',
      color: 'blue',
      name: '💙 理性科技风',
      description: THEMES.modern.description,
      reason: '未能识别文章类型，使用默认推荐'
    };
  }
  
  // 获取最主要的类型
  const mainType = typeScores[0].type;
  const typeConfig = ARTICLE_TYPE_KEYWORDS[mainType];
  
  // 根据类型选择主题和颜色
  const theme = typeConfig.theme;
  let colors = [...typeConfig.colors];  // 复制数组避免修改原数据
  
  // 如果有多个类型，分数接近时可以考虑组合
  let colorIndex = 0;
  if (typeScores.length > 1 && typeScores[1].score > typeScores[0].score * 0.6) {
    // 第二个类型得分超过60%，使用第二个类型的颜色倾向
    const secondType = typeScores[1].type;
    const secondColors = ARTICLE_TYPE_KEYWORDS[secondType].colors;
    // 混合两种颜色倾向
    colors.push(...secondColors.slice(0, 2));
  }
  
  // 选择颜色：优先使用第一个推荐颜色（更稳定），只有当颜色列表变长时才轮换
  // 只有当混合了多个类型的颜色后才使用 hash 轮换
  if (colors.length > 3) {
    const titleMatch = content.match(/^title:\s*(.+)$/m);
    const title = titleMatch ? titleMatch[1] : '';
    const hash = title.split('').reduce((a, b) => ((a << 5) - a + b.charCodeAt(0)) | 0, 0);
    colorIndex = Math.abs(hash) % colors.length;
  } else {
    colorIndex = 0;
  }
  const colorAlias = colors[colorIndex];
  const actualColor = getActualColor(colorAlias);
  
  // 生成推荐结果
  const recommendation: ThemeRecommendation = {
    theme,
    color: actualColor,  // 传递给 baoyu-md 的实际颜色
    name: getThemeStyleName(theme, colorAlias),  // 显示给用户的中文名称
    description: THEMES[theme as keyof typeof THEMES].description,
    reason: `根据文章类型"${mainType}"推荐`
  };
  
  return recommendation;
}

// CLI 入口
if (import.meta.main) {
  const articlePath = Bun.argv[2];
  
  if (!articlePath) {
    console.log('用法: bun auto_theme_selector.ts <文章路径>');
    console.log('示例: bun auto_theme_selector.ts ../outputs/2026-03-21/旅行/imgs/article.md');
    process.exit(1);
  }
  
  const result = recommendTheme(articlePath);
  
  console.log('\n🎨 智能主题推荐结果\n');
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`📌 推荐主题: ${result.name}`);
  console.log(`🎯 主题风格: ${result.description}`);
  console.log(`🔧 主题参数: --theme ${result.theme} --color ${result.color}`);
  console.log(`💡 推荐理由: ${result.reason}`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
  
  // 输出 JSON 格式供脚本调用
  console.log(JSON.stringify({
    theme: result.theme,
    color: result.color,
    name: result.name
  }));
}
