# RSS 热点聚合日报

## 项目简介

本项目为**RSS 热点聚合分析工具**，自动抓取配置的 RSS 源，按自定义关键词分组统计，生成 TrendRadar 风格的分组报告，并通过飞书推送。

- 仅支持 RSS 源
- 关键词分组、+必须词、!排除词配置（见 frequency_words.txt）
- 输出分组统计，格式与 [TrendRadar](https://github.com/hesievan/TrendRadar) 一致
- 支持飞书推送

---

## 配置说明

### 1. RSS 源配置

编辑 `config/rss_sources.json`，示例：
```json
{
  "sources": [
    {"name": "36氪", "url": "https://36kr.com/feed"},
    {"name": "虎嗅网", "url": "https://www.huxiu.com/rss/0.xml"}
  ]
}
```

### 2. 关键词分组配置

在项目根目录新建或编辑 `frequency_words.txt`，每个分组用空行分隔，支持：
- 普通关键词：直接写词
- 必须词：以 `+` 开头，表示该组每条必须包含
- 排除词：以 `!` 开头，表示该组排除包含这些词的内容

示例：
```
华为
任正非
鸿蒙
+手机

哪吒
饺子
!汽车
!食品

AI
人工智能
+技术
!绘画
```

---

## 运行方法

1. 安装依赖
```bash
pip install -r requirements.txt
```
2. 设置飞书 webhook 环境变量
```bash
export FEISHU_WEBHOOK_URL="你的飞书群机器人webhook地址"
```
3. 运行主程序
```bash
python src/main.py
```

---

## 输出示例

```
🔥 华为、任正非、鸿蒙、+手机 : 3 条
  1. [36氪] 华为手机市场份额领先 - 09:30
  2. [虎嗅网] 鸿蒙手机用户破亿 - 10:15

🔥 AI、人工智能、+技术、!绘画 : 2 条
  1. [36氪] AI技术助力医疗诊断 - 11:00

...（每组分开统计）
```

---

## 其他说明
- 仅支持 RSS 源，不再支持其他平台
- 所有分组统计结果均通过飞书推送
- 配置灵活，分组、必须词、排除词均可自由组合

---

如有问题请提 issue 或联系作者。 