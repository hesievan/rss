#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RSS 日报系统测试脚本
用于验证系统各个模块的功能
"""

import sys
import os
import json
from datetime import datetime

# 添加 src 目录到路径
sys.path.append('src')

def test_config_loading():
    """测试配置文件加载"""
    print("🔧 测试配置文件加载...")
    
    try:
        with open('config/rss_sources.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"✅ 配置文件加载成功")
        print(f"   - 配置了 {len(config.get('sources', []))} 个 RSS 源")
        print(f"   - 全局设置: {config.get('global_settings', {})}")
        return True
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False

def test_rss_fetcher():
    """测试 RSS 获取模块"""
    print("\n📡 测试 RSS 获取模块...")
    
    try:
        from rss_fetcher import RSSFetcher
        fetcher = RSSFetcher()
        
        # 测试配置加载
        config = fetcher._load_config()
        print(f"✅ RSS 获取模块初始化成功")
        print(f"   - 加载了 {len(config.get('sources', []))} 个源配置")
        
        return True
    except Exception as e:
        print(f"❌ RSS 获取模块测试失败: {e}")
        return False

def test_content_filter():
    """测试内容筛选模块"""
    print("\n🎯 测试内容筛选模块...")
    
    try:
        from content_filter import ContentFilter
        filter = ContentFilter()
        
        # 测试文章筛选
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
        
        test_config = {
            'keywords': ['AI', '人工智能'],
            'exclude_keywords': ['广告', '推广']
        }
        
        filtered = filter.filter_articles(test_articles, test_config)
        print(f"✅ 内容筛选模块测试成功")
        print(f"   - 原始文章数: {len(test_articles)}")
        print(f"   - 筛选后文章数: {len(filtered)}")
        
        return True
    except Exception as e:
        print(f"❌ 内容筛选模块测试失败: {e}")
        return False

def test_daily_generator():
    """测试日报生成模块"""
    print("\n📰 测试日报生成模块...")
    
    try:
        from daily_generator import DailyGenerator
        generator = DailyGenerator()
        
        # 测试报告生成
        test_articles = [
            {
                'title': 'OpenAI 发布 GPT-5 模型',
                'link': 'https://example.com/1',
                'published': datetime.now(),
                'summary': 'OpenAI 发布了最新的 GPT-5 模型',
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
        
        report = generator.generate_daily_report(test_articles)
        print(f"✅ 日报生成模块测试成功")
        print(f"   - 报告标题: {report.get('title', 'N/A')}")
        print(f"   - 文章数量: {report.get('statistics', {}).get('total_articles', 0)}")
        
        # 测试格式化
        markdown_content = generator.format_for_feishu(report)
        print(f"   - Markdown 内容长度: {len(markdown_content)} 字符")
        
        return True
    except Exception as e:
        print(f"❌ 日报生成模块测试失败: {e}")
        return False

def test_feishu_sender():
    """测试飞书发送模块"""
    print("\n📱 测试飞书发送模块...")
    
    try:
        from feishu_sender import FeishuSender
        sender = FeishuSender()
        
        # 测试消息格式化
        test_report = {
            'title': '📰 科技日报 - 测试',
            'summary': '这是一个测试报告',
            'sections': [],
            'statistics': {'total_articles': 0}
        }
        
        markdown_content = sender._format_report_for_markdown(test_report)
        text_content = sender._format_report_for_text(test_report)
        
        print(f"✅ 飞书发送模块测试成功")
        print(f"   - Markdown 格式长度: {len(markdown_content)} 字符")
        print(f"   - 文本格式长度: {len(text_content)} 字符")
        
        return True
    except Exception as e:
        print(f"❌ 飞书发送模块测试失败: {e}")
        return False

def test_main_processor():
    """测试主处理模块"""
    print("\n⚙️ 测试主处理模块...")
    
    try:
        from main import RSSDailyProcessor
        processor = RSSDailyProcessor()
        
        print(f"✅ 主处理模块初始化成功")
        
        # 测试统计信息获取
        stats = processor.get_statistics()
        print(f"   - 统计信息: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ 主处理模块测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖包"""
    print("\n📦 测试依赖包...")
    
    required_packages = [
        'feedparser',
        'requests',
        'beautifulsoup4',
        'lxml',
        'python-dateutil',
        'jieba'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🚀 RSS 日报系统测试开始")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_config_loading,
        test_rss_fetcher,
        test_content_filter,
        test_daily_generator,
        test_feishu_sender,
        test_main_processor
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用。")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查相关配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 