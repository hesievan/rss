#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
import sys
import os

# 添加 src 目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from content_filter import ContentFilter

class TestContentFilter(unittest.TestCase):
    
    def setUp(self):
        self.filter = ContentFilter()
        
        # 测试文章数据
        self.test_articles = [
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
            },
            {
                'title': 'ChatGPT 新功能发布',
                'summary': 'OpenAI 发布了 ChatGPT 的新功能',
                'source': 'AI 新闻',
                'published': datetime.now()
            }
        ]
    
    def test_filter_articles_with_keywords(self):
        """测试关键词筛选"""
        config = {
            'keywords': ['AI', '人工智能', 'ChatGPT'],
            'exclude_keywords': ['广告', '推广']
        }
        
        filtered = self.filter.filter_articles(self.test_articles, config)
        
        # 应该包含 AI 相关文章，排除广告文章
        self.assertEqual(len(filtered), 2)
        titles = [article['title'] for article in filtered]
        self.assertIn('AI 技术最新突破', titles)
        self.assertIn('ChatGPT 新功能发布', titles)
        self.assertNotIn('广告推广信息', titles)
    
    def test_filter_articles_with_exclude_keywords(self):
        """测试排除关键词筛选"""
        config = {
            'keywords': [],  # 不设置包含关键词
            'exclude_keywords': ['广告']
        }
        
        filtered = self.filter.filter_articles(self.test_articles, config)
        
        # 应该排除包含"广告"的文章
        self.assertEqual(len(filtered), 2)
        titles = [article['title'] for article in filtered]
        self.assertNotIn('广告推广信息', titles)
    
    def test_filter_by_source(self):
        """测试按来源筛选"""
        filtered = self.filter.filter_by_source(self.test_articles, '科技新闻')
        
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['source'], '科技新闻')
    
    def test_remove_duplicates(self):
        """测试去重功能"""
        duplicate_articles = self.test_articles + [
            {
                'title': 'AI 技术最新突破',  # 重复标题
                'summary': '人工智能领域取得重大进展',
                'source': '科技新闻',
                'published': datetime.now()
            }
        ]
        
        unique_articles = self.filter.remove_duplicates(duplicate_articles)
        
        self.assertEqual(len(unique_articles), 3)  # 应该去重后只有3篇
    
    def test_sort_by_priority(self):
        """测试优先级排序"""
        priority_keywords = ['AI', 'ChatGPT']
        
        sorted_articles = self.filter.sort_by_priority(self.test_articles, priority_keywords)
        
        # 包含更多关键词的文章应该排在前面
        self.assertEqual(sorted_articles[0]['title'], 'ChatGPT 新功能发布')
        self.assertEqual(sorted_articles[1]['title'], 'AI 技术最新突破')
    
    def test_filter_by_date_range(self):
        """测试日期范围筛选"""
        now = datetime.now()
        old_article = {
            'title': '旧文章',
            'published': now.replace(hour=now.hour - 25)
        }
        new_article = {
            'title': '新文章',
            'published': now.replace(hour=now.hour - 12)
        }
        
        articles = [old_article, new_article]
        
        # 筛选最近24小时的文章
        filtered = self.filter.filter_by_date_range(articles, 
                                                   start_date=now.replace(hour=now.hour - 24))
        
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['title'], '新文章')

if __name__ == '__main__':
    unittest.main() 