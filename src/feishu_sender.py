#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class FeishuSender:
    """飞书消息发送模块"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.session = requests.Session()
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def send_text_message(self, content: str, webhook_url: str = None) -> bool:
        """发送文本消息"""
        url = webhook_url or self.webhook_url
        if not url:
            self.logger.error("未配置飞书 Webhook URL")
            return False
        
        try:
            payload = {
                "msg_type": "text",
                "content": {
                    "text": content
                }
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 0:
                self.logger.info("飞书文本消息发送成功")
                return True
            else:
                self.logger.error(f"飞书消息发送失败: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"发送飞书消息失败: {e}")
            return False
    
    def send_markdown_message(self, content: str, webhook_url: str = None) -> bool:
        """发送 Markdown 消息"""
        url = webhook_url or self.webhook_url
        if not url:
            self.logger.error("未配置飞书 Webhook URL")
            return False
        
        try:
            payload = {
                "msg_type": "post",
                "content": {
                    "post": {
                        "zh_cn": {
                            "title": "📰 科技日报",
                            "content": self._parse_markdown_to_feishu(content)
                        }
                    }
                }
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 0:
                self.logger.info("飞书 Markdown 消息发送成功")
                return True
            else:
                self.logger.error(f"飞书消息发送失败: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"发送飞书消息失败: {e}")
            return False
    
    def send_interactive_message(self, report: Dict[str, Any], webhook_url: str = None) -> bool:
        """发送交互式消息卡片"""
        url = webhook_url or self.webhook_url
        if not url:
            self.logger.error("未配置飞书 Webhook URL")
            return False
        
        try:
            # 构建卡片内容
            card_content = self._build_interactive_card(report)
            
            payload = {
                "msg_type": "interactive",
                "card": card_content
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 0:
                self.logger.info("飞书交互式消息发送成功")
                return True
            else:
                self.logger.error(f"飞书消息发送失败: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"发送飞书消息失败: {e}")
            return False
    
    def _parse_markdown_to_feishu(self, markdown_content: str) -> list:
        """将 Markdown 内容转换为飞书 post 格式"""
        lines = markdown_content.split('\n')
        content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('# '):
                content.append([{"tag": "text", "text": line[2:], "style": ["bold", "large"]}])
            elif line.startswith('## '):
                content.append([{"tag": "text", "text": line[3:], "style": ["bold"]}])
            elif line.startswith('### '):
                content.append([{"tag": "text", "text": line[4:], "style": ["bold"]}])
            elif line.startswith('- **'):
                # 处理列表项
                text = line[4:-2]  # 移除 "- **" 和 "**"
                content.append([{"tag": "text", "text": "• " + text, "style": ["bold"]}])
            elif line.startswith('- '):
                content.append([{"tag": "text", "text": "• " + line[2:]}])
            elif line.startswith('> '):
                content.append([{"tag": "text", "text": line[2:], "style": ["italic"]}])
            elif line.startswith('---'):
                content.append([{"tag": "hr"}])
            else:
                content.append([{"tag": "text", "text": line}])
        
        return content
    
    def _build_interactive_card(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """构建交互式消息卡片"""
        # 构建摘要文本
        summary_text = report.get('summary', '今日暂无重要资讯')
        
        # 构建文章列表
        articles_text = ""
        for section in report.get('sections', []):
            articles_text += f"\n**{section['title']}**\n"
            for article in section['articles'][:3]:  # 每个来源最多显示3篇
                articles_text += f"• {article['title']}\n"
        
        # 构建卡片
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": report.get('title', '科技日报')
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**📋 今日摘要**\n{summary_text}"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**📊 数据统计**\n• 总文章数：{report.get('statistics', {}).get('total_articles', 0)} 篇"
                    }
                }
            ]
        }
        
        # 如果有文章，添加文章列表
        if articles_text:
            card["elements"].append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**📰 精选文章**{articles_text}"
                }
            })
        
        # 添加时间戳
        card["elements"].append({
            "tag": "note",
            "elements": [
                {
                    "tag": "text",
                    "content": f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        })
        
        return card
    
    def send_daily_report(self, report: Dict[str, Any], webhook_url: str = None) -> bool:
        """发送日报（自动选择最佳格式）"""
        # 首先尝试发送交互式卡片
        if self.send_interactive_message(report, webhook_url):
            return True
        
        # 如果交互式卡片失败，尝试发送 Markdown 消息
        self.logger.warning("交互式消息发送失败，尝试发送 Markdown 消息")
        if self.send_markdown_message(self._format_report_for_markdown(report), webhook_url):
            return True
        
        # 最后尝试发送纯文本消息
        self.logger.warning("Markdown 消息发送失败，尝试发送文本消息")
        return self.send_text_message(self._format_report_for_text(report), webhook_url)
    
    def _format_report_for_markdown(self, report: Dict[str, Any]) -> str:
        """格式化报告为 Markdown"""
        content = f"# {report.get('title', '科技日报')}\n\n"
        content += f"## 📋 今日摘要\n{report.get('summary', '今日暂无重要资讯')}\n\n"
        
        # 添加统计信息
        stats = report.get('statistics', {})
        content += f"## 📊 数据统计\n"
        content += f"- 总文章数：{stats.get('total_articles', 0)} 篇\n"
        if stats.get('top_sources'):
            content += f"- 主要来源：{', '.join([f'{source}({count})' for source, count in stats['top_sources']])}\n"
        content += "\n"
        
        # 添加各章节内容
        for section in report.get('sections', []):
            content += f"## {section['title']}\n"
            for article in section['articles']:
                content += f"- **{article['title']}** [{article['published']}]\n"
                content += f"  {article['link']}\n"
                if article.get('summary'):
                    content += f"  > {article['summary']}\n"
                content += "\n"
        
        content += f"---\n*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return content
    
    def _format_report_for_text(self, report: Dict[str, Any]) -> str:
        """格式化报告为纯文本"""
        content = f"{report.get('title', '科技日报')}\n\n"
        content += f"📋 今日摘要\n{report.get('summary', '今日暂无重要资讯')}\n\n"
        
        # 添加统计信息
        stats = report.get('statistics', {})
        content += f"📊 数据统计\n"
        content += f"总文章数：{stats.get('total_articles', 0)} 篇\n"
        if stats.get('top_sources'):
            content += f"主要来源：{', '.join([f'{source}({count})' for source, count in stats['top_sources']])}\n"
        content += "\n"
        
        # 添加各章节内容
        for section in report.get('sections', []):
            content += f"{section['title']}\n"
            for article in section['articles']:
                content += f"- {article['title']} [{article['published']}]\n"
                content += f"  {article['link']}\n"
                if article.get('summary'):
                    content += f"  {article['summary']}\n"
                content += "\n"
        
        content += f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return content

if __name__ == "__main__":
    # 测试代码
    sender = FeishuSender()
    
    # 模拟报告数据
    test_report = {
        'title': '📰 科技日报 - 2024年01月01日',
        'summary': '今日共筛选出 5 篇重要资讯，来自 3 个信息源。',
        'sections': [
            {
                'title': '📊 36氪',
                'articles': [
                    {
                        'title': 'OpenAI 发布 GPT-5 模型',
                        'link': 'https://example.com/1',
                        'published': '09:30',
                        'summary': 'OpenAI 发布了最新的 GPT-5 模型'
                    }
                ]
            }
        ],
        'statistics': {
            'total_articles': 5,
            'top_sources': [('36氪', 3), ('虎嗅网', 2)]
        }
    }
    
    # 测试发送（需要配置 webhook_url）
    # success = sender.send_daily_report(test_report)
    # print(f"发送结果: {'成功' if success else '失败'}")
    
    # 测试格式化
    markdown_content = sender._format_report_for_markdown(test_report)
    print("Markdown 格式:")
    print(markdown_content) 