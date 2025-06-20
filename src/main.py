#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any

# 添加 src 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rss_fetcher import RSSFetcher
from content_filter import ContentFilter
from daily_generator import DailyGenerator
from feishu_sender import FeishuSender
from word_group_parser import WordGroupParser

class RSSDailyProcessor:
    """RSS 日报处理主程序"""
    
    def __init__(self):
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/rss_daily.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 创建日志目录
        try:
            os.makedirs('logs', exist_ok=True)
            os.makedirs('reports', exist_ok=True)
        except Exception as e:
            self.logger.error(f"创建日志或报告目录失败: {e}")
            print("❌ 无法创建 logs 或 reports 目录，请检查写入权限！")
            sys.exit(1)
        
        # 初始化各个模块
        self.fetcher = RSSFetcher()
        self.filter = ContentFilter()
        self.generator = DailyGenerator()
        self.sender = FeishuSender()
    
    def process_daily_report(self, webhook_url: str = None) -> bool:
        """处理日报生成和发送的完整流程（分组统计+飞书推送）"""
        try:
            self.logger.info("开始处理日报生成流程（分组统计模式）")
            # 1. 获取 RSS 数据
            all_articles = self.fetcher.fetch_all_feeds()
            if not all_articles:
                self.logger.warning("未获取到任何文章")
                return self._send_empty_report(webhook_url)
            # 2. 筛选最近的文章
            recent_articles = self.fetcher.filter_recent_articles(all_articles, hours=24)
            if not recent_articles:
                self.logger.warning("最近24小时内没有文章")
                return self._send_empty_report(webhook_url)
            # 3. 读取分组配置
            parser = WordGroupParser()
            groups = parser.parse()
            # 4. 分组过滤统计
            group_results = self.filter.filter_by_groups(recent_articles, groups)
            # 5. 生成分组统计文本
            trendar_text = self.generator.generate_trendar_style_report(group_results)
            if not trendar_text.strip():
                self.logger.warning("分组统计后无内容")
                return self._send_empty_report(webhook_url)
            # 6. 发送到飞书
            success = self.sender.send_text_message(trendar_text, webhook_url)
            if success:
                self.logger.info("日报处理完成，发送成功")
            else:
                self.logger.error("日报发送失败")
            return success
        except Exception as e:
            self.logger.error(f"处理日报时发生错误: {e}", exc_info=True)
            return False
    
    def _send_empty_report(self, webhook_url: str = None) -> bool:
        """发送空报告（分组统计模式）"""
        try:
            empty_text = "今日暂无重要资讯。"
            return self.sender.send_text_message(empty_text, webhook_url)
        except Exception as e:
            self.logger.error(f"发送空报告失败: {e}")
            return False
    
    def test_connection(self, webhook_url: str) -> bool:
        """测试飞书连接"""
        try:
            test_message = "🔧 RSS 日报系统连接测试\n\n如果您看到这条消息，说明飞书机器人配置正确！"
            return self.sender.send_text_message(test_message, webhook_url)
        except Exception as e:
            self.logger.error(f"连接测试失败: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        try:
            # 获取今天的报告文件
            today = datetime.now().strftime('%Y%m%d')
            report_file = f"reports/daily_report_{today}.json"
            
            if os.path.exists(report_file):
                import json
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                return report.get('statistics', {})
            else:
                return {"total_articles": 0, "message": "今日暂无报告"}
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {"error": str(e)}

def main():
    """主函数"""
    # 从环境变量获取飞书 Webhook URL
    webhook_url = os.getenv('FEISHU_WEBHOOK_URL')
    
    if not webhook_url:
        print("错误: 未设置 FEISHU_WEBHOOK_URL 环境变量")
        print("请在 GitHub Secrets 或本地环境变量中设置 FEISHU_WEBHOOK_URL")
        sys.exit(1)
    
    # 创建处理器
    processor = RSSDailyProcessor()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'test':
            # 测试连接
            print("测试飞书连接...")
            success = processor.test_connection(webhook_url)
            print(f"连接测试: {'成功' if success else '失败'}")
            sys.exit(0 if success else 1)
        
        elif command == 'stats':
            # 获取统计信息
            stats = processor.get_statistics()
            print("统计信息:")
            print(f"总文章数: {stats.get('total_articles', 0)}")
            if stats.get('top_sources'):
                print("主要来源:")
                for source, count in stats['top_sources']:
                    print(f"  - {source}: {count} 篇")
            sys.exit(0)
        
        elif command == 'help':
            print("RSS 日报系统使用说明:")
            print("  python main.py          - 生成并发送日报")
            print("  python main.py test     - 测试飞书连接")
            print("  python main.py stats    - 查看统计信息")
            print("  python main.py help     - 显示帮助信息")
            sys.exit(0)
    
    # 默认执行日报处理
    print("开始处理 RSS 日报...")
    success = processor.process_daily_report(webhook_url)
    
    if success:
        print("✅ 日报处理完成，发送成功")
        sys.exit(0)
    else:
        print("❌ 日报处理失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 