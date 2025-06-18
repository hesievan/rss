#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import jieba
import logging
from typing import List, Dict, Any
from datetime import datetime

class ContentFilter:
    """新闻内容筛选模块"""
    
    def __init__(self):
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # 初始化 jieba
        jieba.initialize()
    
    def filter_articles(self, articles: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据配置筛选文章"""
        filtered_articles = []
        
        for article in articles:
            if self._should_include_article(article, config):
                filtered_articles.append(article)
        
        self.logger.info(f"筛选后保留 {len(filtered_articles)} 篇文章")
        return filtered_articles
    
    def _should_include_article(self, article: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """判断文章是否应该被包含"""
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        content = f"{title} {summary}"
        
        # 检查排除关键词
        if self._contains_exclude_keywords(content, config):
            return False
        
        # 检查包含关键词
        if not self._contains_include_keywords(content, config):
            return False
        
        return True
    
    def _contains_exclude_keywords(self, content: str, config: Dict[str, Any]) -> bool:
        """检查是否包含排除关键词"""
        exclude_keywords = config.get('exclude_keywords', [])
        
        for keyword in exclude_keywords:
            if keyword.lower() in content:
                self.logger.debug(f"文章包含排除关键词: {keyword}")
                return True
        
        return False
    
    def _contains_include_keywords(self, content: str, config: Dict[str, Any]) -> bool:
        """检查是否包含包含关键词"""
        include_keywords = config.get('keywords', [])
        
        if not include_keywords:
            return True  # 如果没有设置关键词，则包含所有文章
        
        # 使用 jieba 分词进行更精确的匹配
        content_words = set(jieba.lcut(content))
        
        for keyword in include_keywords:
            keyword_lower = keyword.lower()
            
            # 直接字符串匹配
            if keyword_lower in content:
                return True
            
            # 分词匹配
            keyword_words = set(jieba.lcut(keyword_lower))
            if keyword_words.intersection(content_words):
                return True
        
        return False
    
    def filter_by_source(self, articles: List[Dict[str, Any]], source_name: str = None) -> List[Dict[str, Any]]:
        """按来源筛选文章"""
        if not source_name:
            return articles
        
        filtered = [article for article in articles if article.get('source') == source_name]
        self.logger.info(f"按来源 '{source_name}' 筛选后保留 {len(filtered)} 篇文章")
        return filtered
    
    def filter_by_date_range(self, articles: List[Dict[str, Any]], 
                           start_date: datetime = None, 
                           end_date: datetime = None) -> List[Dict[str, Any]]:
        """按日期范围筛选文章"""
        filtered = articles
        
        if start_date:
            filtered = [article for article in filtered 
                       if article.get('published', datetime.now()) >= start_date]
        
        if end_date:
            filtered = [article for article in filtered 
                       if article.get('published', datetime.now()) <= end_date]
        
        self.logger.info(f"按日期范围筛选后保留 {len(filtered)} 篇文章")
        return filtered
    
    def remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去除重复文章（基于标题和链接）"""
        seen_titles = set()
        seen_links = set()
        unique_articles = []
        
        for article in articles:
            title = article.get('title', '').strip()
            link = article.get('link', '').strip()
            
            # 检查标题和链接是否重复
            if title not in seen_titles and link not in seen_links:
                seen_titles.add(title)
                seen_links.add(link)
                unique_articles.append(article)
        
        removed_count = len(articles) - len(unique_articles)
        self.logger.info(f"去除 {removed_count} 篇重复文章，保留 {len(unique_articles)} 篇")
        
        return unique_articles
    
    def sort_by_priority(self, articles: List[Dict[str, Any]], 
                        priority_keywords: List[str] = None) -> List[Dict[str, Any]]:
        """按优先级排序文章"""
        if not priority_keywords:
            return articles
        
        def get_priority_score(article):
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            content = f"{title} {summary}"
            
            score = 0
            for keyword in priority_keywords:
                if keyword.lower() in content:
                    score += 1
            
            return score
        
        sorted_articles = sorted(articles, key=get_priority_score, reverse=True)
        self.logger.info(f"按优先级关键词排序完成")
        
        return sorted_articles

if __name__ == "__main__":
    # 测试代码
    filter = ContentFilter()
    
    # 模拟文章数据
    test_articles = [
        {
            'title': 'AI 技术最新突破',
            'summary': '人工智能领域取得重大进展',
            'source': '科技新闻',
            'published': datetime.now()
        },
        {
            'title': '广告推广信息',
            'summary': '这是一个广告内容',
            'source': '商业新闻',
            'published': datetime.now()
        }
    ]
    
    # 测试配置
    test_config = {
        'keywords': ['AI', '人工智能'],
        'exclude_keywords': ['广告', '推广']
    }
    
    filtered = filter.filter_articles(test_articles, test_config)
    print(f"筛选结果: {len(filtered)} 篇文章")
    
    for article in filtered:
        print(f"- {article['title']}") 