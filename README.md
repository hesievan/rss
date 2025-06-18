# RSS 智能推送系统

基于 GitHub Actions 的自动化 RSS 新闻筛选和飞书推送系统。

## 功能特性

- 🔄 定时从多个 RSS 源获取新闻
- 🎯 智能关键词筛选和内容过滤
- 📰 自动生成格式化的日报内容
- 📱 飞书机器人推送提醒
- ⚙️ 灵活的配置管理
- 📊 执行日志和状态监控

## 系统架构

```
RSS源 → 数据获取 → 内容筛选 → 日报生成 → 飞书推送
```

## 快速开始

1. Fork 本仓库
2. 配置 RSS 源和筛选规则（编辑 `config/rss_sources.json`）
3. 设置飞书机器人 Webhook（在 GitHub Secrets 中配置）
4. 启用 GitHub Actions 定时任务

## 配置说明

### RSS 源配置
在 `config/rss_sources.json` 中配置您的 RSS 源：

```json
{
  "sources": [
    {
      "name": "科技新闻",
      "url": "https://example.com/feed.xml",
      "keywords": ["AI", "人工智能", "机器学习"],
      "exclude_keywords": ["广告", "推广"]
    }
  ]
}
```

### 飞书机器人配置
1. 在飞书中创建机器人
2. 获取 Webhook URL
3. 在 GitHub 仓库的 Settings → Secrets 中添加：
   - `FEISHU_WEBHOOK_URL`: 飞书机器人 Webhook 地址

## 定时任务

系统默认每天上午 9:00 执行一次，您可以在 `.github/workflows/rss_daily.yml` 中修改执行时间。

## 许可证

MIT License 