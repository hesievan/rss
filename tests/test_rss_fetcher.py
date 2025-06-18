#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os

# 添加 src 目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rss_fetcher import RSSFetcher

class TestRSSFetcher(unittest.TestCase):
    
    def setUp(self):
        self.fetcher = RSSFetcher()
    
    def test_load_config(self):
        """测试配置文件加载"""
        config = self.fetcher._load_config()
        self.assertIsInstance(config, dict)
        self.assertIn('sources', config)
        self.assertIn('global_settings', config)
    
    @patch('requests.Session.get')
    def test_fetch_rss_feed(self, mock_get):
        """测试 RSS 源获取"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.content = '''
        <?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>测试 RSS</title>
                <item>
                    <title>测试文章标题</title>
                    <link>https://example.com/test</link>
                    <description>测试文章描述</description>
                    <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 测试源配置
        test_source = {
            'name': '测试源',
            'url': 'https://example.com/feed.xml',
            'keywords': ['测试'],
            'max_items': 10
        }
        
        articles = self.fetcher.fetch_rss_feed(test_source)
        
        self.assertIsInstance(articles, list)
        if articles:  # 如果有文章
            article = articles[0]
            self.assertIn('title', article)
            self.assertIn('link', article)
            self.assertIn('published', article)
            self.assertIn('source', article)
    
    def test_filter_recent_articles(self):
        """测试最近文章筛选"""
        # 创建测试文章
        now = datetime.now()
        old_article = {
            'title': '旧文章',
            'published': now.replace(hour=now.hour - 25)  # 25小时前
        }
        new_article = {
            'title': '新文章',
            'published': now.replace(hour=now.hour - 12)  # 12小时前
        }
        
        articles = [old_article, new_article]
        recent_articles = self.fetcher.filter_recent_articles(articles, hours=24)
        
        self.assertEqual(len(recent_articles), 1)
        self.assertEqual(recent_articles[0]['title'], '新文章')

if __name__ == '__main__':
    unittest.main() 