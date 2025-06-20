#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import feedparser
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import random
import os

class RSSFetcher:
    """RSS 数据获取模块"""
    
    def __init__(self, config_file: str = "config/rss_sources.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if not os.path.exists(self.config_file):
                self.logger.error(f"配置文件不存在: {self.config_file}")
                return {"sources": [], "global_settings": {}}
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            return {"sources": [], "global_settings": {}}
    
    def fetch_rss_feed(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取单个 RSS 源的数据"""
        try:
            self.logger.info(f"正在获取 RSS 源: {source['name']} - {source['url']}")
            
            # 添加随机延迟避免被限制
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(source['url'], timeout=30)
            response.raise_for_status()
            
            # 解析 RSS 内容
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                self.logger.warning(f"RSS 解析警告: {feed.bozo_exception}")
            
            articles = []
            max_items = source.get('max_items', 20)
            
            for entry in feed.entries[:max_items]:
                try:
                    # 解析发布时间
                    published_time = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_time = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_time = datetime(*entry.updated_parsed[:6])
                    else:
                        published_time = None
                    
                    article = {
                        'title': entry.title,
                        'link': entry.link,
                        'published': published_time if published_time else datetime.now(),
                        'summary': getattr(entry, 'summary', ''),
                        'source': source['name'],
                        'source_url': source['url']
                    }
                    articles.append(article)
                    
                except Exception as e:
                    self.logger.error(f"解析文章失败: {e}")
                    continue
            
            self.logger.info(f"成功获取 {len(articles)} 篇文章来自 {source['name']}")
            return articles
            
        except Exception as e:
            self.logger.error(f"获取 RSS 源失败 {source['name']}: {e}")
            return []
    
    def fetch_all_feeds(self) -> List[Dict[str, Any]]:
        """获取所有 RSS 源的数据"""
        all_articles = []
        
        for source in self.config.get('sources', []):
            articles = self.fetch_rss_feed(source)
            all_articles.extend(articles)
        
        # 按发布时间排序
        all_articles.sort(key=lambda x: x['published'], reverse=True)
        
        self.logger.info(f"总共获取到 {len(all_articles)} 篇文章")
        return all_articles
    
    def filter_recent_articles(self, articles: List[Dict[str, Any]], hours: int = 24) -> List[Dict[str, Any]]:
        """筛选最近指定小时内的文章"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_articles = [
            article for article in articles 
            if article['published'] >= cutoff_time
        ]
        
        self.logger.info(f"筛选出最近 {hours} 小时内的 {len(recent_articles)} 篇文章")
        return recent_articles

if __name__ == "__main__":
    # 测试代码
    fetcher = RSSFetcher()
    articles = fetcher.fetch_all_feeds()
    recent_articles = fetcher.filter_recent_articles(articles, 24)
    
    print(f"获取到 {len(articles)} 篇文章")
    print(f"最近24小时内有 {len(recent_articles)} 篇文章")
    
    for article in recent_articles[:5]:
        print(f"- {article['title']} ({article['source']})") 