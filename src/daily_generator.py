#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict
from word_group_parser import WordGroupParser

class DailyGenerator:
    """日报生成模块"""
    
    def __init__(self):
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def generate_daily_report(self, articles: List[Dict[str, Any]], 
                            max_items: int = 50) -> Dict[str, Any]:
        """生成日报内容"""
        if not articles:
            return self._generate_empty_report()
        
        # 限制文章数量
        articles = articles[:max_items]
        
        # 按来源分组
        articles_by_source = self._group_by_source(articles)
        
        # 生成报告
        report = {
            'title': self._generate_title(),
            'summary': self._generate_summary(articles),
            'sections': self._generate_sections(articles_by_source),
            'statistics': self._generate_statistics(articles),
            'generated_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"生成日报完成，包含 {len(articles)} 篇文章")
        return report
    
    def _generate_title(self) -> str:
        """生成日报标题"""
        today = datetime.now().strftime('%Y年%m月%d日')
        return f"📰 科技日报 - {today}"
    
    def _generate_summary(self, articles: List[Dict[str, Any]]) -> str:
        """生成日报摘要"""
        total_articles = len(articles)
        sources = set(article.get('source', '') for article in articles)
        
        summary = f"今日共筛选出 {total_articles} 篇重要资讯，"
        summary += f"来自 {len(sources)} 个信息源。"
        
        if total_articles > 0:
            # 统计热门关键词
            keyword_stats = self._analyze_keywords(articles)
            if keyword_stats:
                top_keywords = list(keyword_stats.items())[:3]
                keyword_str = "、".join([f"{kw}({count})" for kw, count in top_keywords])
                summary += f" 热门话题：{keyword_str}。"
        
        return summary
    
    def _generate_sections(self, articles_by_source: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """生成日报章节"""
        sections = []
        
        for source_name, articles in articles_by_source.items():
            section = {
                'title': f"📊 {source_name}",
                'articles': []
            }
            
            for article in articles:
                article_item = {
                    'title': article.get('title', ''),
                    'link': article.get('link', ''),
                    'published': article.get('published').strftime('%H:%M') if article.get('published') else '',
                    'summary': self._truncate_summary(article.get('summary', ''), 100)
                }
                section['articles'].append(article_item)
            
            sections.append(section)
        
        return sections
    
    def _generate_statistics(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成统计信息"""
        sources = defaultdict(int)
        hours = defaultdict(int)
        
        for article in articles:
            sources[article.get('source', '')] += 1
            published = article.get('published')
            if published:
                hour = published.hour
                hours[f"{hour:02d}:00"] += 1
        
        return {
            'total_articles': len(articles),
            'source_distribution': dict(sources),
            'hourly_distribution': dict(hours),
            'top_sources': sorted(sources.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    def _group_by_source(self, articles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按来源分组文章"""
        grouped = defaultdict(list)
        for article in articles:
            grouped[article['source']].append(article)
        return dict(grouped)
    
    def _analyze_keywords(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """分析关键词频率"""
        keyword_count = defaultdict(int)
        
        # 常见科技关键词
        tech_keywords = [
            'AI', '人工智能', '机器学习', 'ChatGPT', '大模型', '科技', '创新',
            '创业', '投资', '融资', 'IPO', '上市', '收购', '合并', '裁员',
            '芯片', '半导体', '新能源', '电动车', '元宇宙', 'Web3', '区块链'
        ]
        
        for article in articles:
            title = article['title'].lower()
            summary = article.get('summary', '').lower()
            content = f"{title} {summary}"
            
            for keyword in tech_keywords:
                if keyword.lower() in content:
                    keyword_count[keyword] += 1
        
        return dict(sorted(keyword_count.items(), key=lambda x: x[1], reverse=True))
    
    def _truncate_summary(self, summary: str, max_length: int) -> str:
        """截断摘要"""
        if len(summary) <= max_length:
            return summary
        return summary[:max_length] + "..."
    
    def _generate_empty_report(self) -> Dict[str, Any]:
        """生成空报告"""
        return {
            'title': self._generate_title(),
            'summary': "今日暂无重要资讯。",
            'sections': [],
            'statistics': {
                'total_articles': 0,
                'source_distribution': {},
                'hourly_distribution': {},
                'top_sources': []
            },
            'generated_at': datetime.now().isoformat()
        }
    
    def format_for_feishu(self, report: Dict[str, Any]) -> str:
        """格式化为飞书消息格式"""
        content = f"# {report['title']}\n\n"
        content += f"## 📋 今日摘要\n{report['summary']}\n\n"
        
        # 添加统计信息
        stats = report['statistics']
        content += f"## 📊 数据统计\n"
        content += f"- 总文章数：{stats['total_articles']} 篇\n"
        if stats['top_sources']:
            content += f"- 主要来源：{', '.join([f'{source}({count})' for source, count in stats['top_sources']])}\n"
        content += "\n"
        
        # 添加各章节内容
        for section in report['sections']:
            content += f"## {section['title']}\n"
            for article in section['articles']:
                content += f"- **{article['title']}** [{article['published']}]\n"
                content += f"  {article['link']}\n"
                if article['summary']:
                    content += f"  > {article['summary']}\n"
                content += "\n"
        
        content += f"---\n*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return content
    
    def format_for_markdown(self, report: Dict[str, Any]) -> str:
        """格式化为 Markdown 格式"""
        return self.format_for_feishu(report)
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """保存报告到文件"""
        if not filename:
            today = datetime.now().strftime('%Y%m%d')
            filename = f"reports/daily_report_{today}.json"
        
        try:
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"报告已保存到: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"保存报告失败: {e}")
            return ""
    
    def generate_trendar_style_report(self, group_results: list) -> str:
        """
        生成 TrendRadar 风格的分组统计文本。
        group_results: ContentFilter.filter_by_groups 的输出
        """
        lines = []
        for idx, group_result in enumerate(group_results, 1):
            group = group_result['group']
            articles = group_result['matched_articles']
            # 组描述
            desc = []
            desc += group.get('keywords', [])
            desc += [f"+{w}" for w in group.get('must_keywords', [])]
            desc += [f"!{w}" for w in group.get('exclude_keywords', [])]
            desc_str = '、'.join(desc)
            lines.append(f"🔥 {desc_str} : {len(articles)} 条\n")
            # 组内文章统计
            # 按来源+标题去重+统计出现次数
            stat_map = {}
            for art in articles:
                key = (art.get('source', ''), art.get('title', ''))
                if key not in stat_map:
                    stat_map[key] = {
                        'article': art,
                        'count': 1,
                        'first_time': art.get('published'),
                        'last_time': art.get('published')
                    }
                else:
                    stat_map[key]['count'] += 1
                    # 更新时间范围
                    if art.get('published') < stat_map[key]['first_time']:
                        stat_map[key]['first_time'] = art.get('published')
                    if art.get('published') > stat_map[key]['last_time']:
                        stat_map[key]['last_time'] = art.get('published')
            # 排序：出现次数多、时间新优先
            stat_list = sorted(stat_map.values(), key=lambda x: (-x['count'], x['first_time']))
            for i, stat in enumerate(stat_list, 1):
                art = stat['article']
                src = art.get('source', '')
                title = art.get('title', '')
                # 时间格式
                ft = stat['first_time'].strftime('%H:%M') if stat['first_time'] else ''
                lt = stat['last_time'].strftime('%H:%M') if stat['last_time'] else ''
                time_str = f"{ft}" if ft == lt else f"{ft} ~ {lt}"
                count_str = f"({stat['count']}次)" if stat['count'] > 1 else ''
                lines.append(f"  {i}. [{src}] {title} - {time_str} {count_str}")
            lines.append("")
        return '\n'.join(lines)

if __name__ == "__main__":
    # 测试代码
    generator = DailyGenerator()
    
    # 模拟文章数据
    test_articles = [
        {
            'title': 'OpenAI 发布 GPT-5 模型',
            'link': 'https://example.com/1',
            'published': datetime.now(),
            'summary': 'OpenAI 发布了最新的 GPT-5 模型，性能大幅提升',
            'source': '36氪'
        },
        {
            'title': '特斯拉发布新款电动车',
            'link': 'https://example.com/2',
            'published': datetime.now(),
            'summary': '特斯拉发布了全新的电动车产品线',
            'source': '虎嗅网'
        }
    ]
    
    # 生成报告
    report = generator.generate_daily_report(test_articles)
    
    # 格式化为飞书消息
    feishu_content = generator.format_for_feishu(report)
    print("飞书消息格式:")
    print(feishu_content)
    
    # 保存报告
    generator.save_report(report) 