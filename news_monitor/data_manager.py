import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class NewsDataManager:
    """
    新闻数据管理类，提供新闻数据的存储、查询和分析功能
    """
    
    def __init__(self, storage):
        """
        初始化新闻数据管理器
        
        Args:
            storage: 文件存储对象
        """
        self.storage = storage
        self.news_file = "news_data"
        self.logger = logging.getLogger(__name__)
    
    def save_news(self, news_items: List[Dict[str, Any]]) -> bool:
        """
        保存新闻数据
        
        Args:
            news_items: 新闻数据列表
            
        Returns:
            是否成功保存
        """
        try:
            # 获取现有数据
            existing_news = self.get_all_news()
            
            # 添加新数据
            for item in news_items:
                # 检查是否已存在相同URL的新闻
                if not any(existing["url"] == item["url"] for existing in existing_news):
                    existing_news.append(item)
            
            # 保存到文件
            result = self.storage.save_json(existing_news, self.news_file)
            
            if result:
                self.logger.info(f"成功保存 {len(news_items)} 条新闻数据")
            else:
                self.logger.error("保存新闻数据失败")
                
            return result
        except Exception as e:
            self.logger.error(f"保存新闻数据时发生错误: {str(e)}")
            return False
    
    def get_all_news(self) -> List[Dict[str, Any]]:
        """
        获取所有新闻数据
        
        Returns:
            新闻数据列表
        """
        try:
            return self.storage.load_json(self.news_file, [])
        except Exception as e:
            self.logger.error(f"获取所有新闻数据时发生错误: {str(e)}")
            return []
    
    def get_news_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        根据关键词获取新闻数据
        
        Args:
            keyword: 关键词
            
        Returns:
            新闻数据列表
        """
        try:
            all_news = self.get_all_news()
            return [item for item in all_news if item.get("keyword") == keyword]
        except Exception as e:
            self.logger.error(f"根据关键词获取新闻数据时发生错误: {str(e)}")
            return []
    
    def get_news_by_platform(self, platform_type: str) -> List[Dict[str, Any]]:
        """
        根据平台类型获取新闻数据
        
        Args:
            platform_type: 平台类型
            
        Returns:
            新闻数据列表
        """
        try:
            all_news = self.get_all_news()
            return [item for item in all_news if item.get("platform_type") == platform_type]
        except Exception as e:
            self.logger.error(f"根据平台类型获取新闻数据时发生错误: {str(e)}")
            return []
    
    def get_news_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        根据日期范围获取新闻数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            新闻数据列表
        """
        try:
            all_news = self.get_all_news()
            filtered_news = []
            
            for item in all_news:
                try:
                    publish_time = item.get("publish_time", "")
                    if publish_time:
                        publish_date = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
                        if start_date <= publish_date <= end_date:
                            filtered_news.append(item)
                except Exception as e:
                    self.logger.warning(f"解析新闻发布时间失败: {str(e)}")
                    continue
            
            return filtered_news
        except Exception as e:
            self.logger.error(f"根据日期范围获取新闻数据时发生错误: {str(e)}")
            return []
    
    def get_news_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """
        根据标签获取新闻数据
        
        Args:
            tags: 标签列表
            
        Returns:
            新闻数据列表
        """
        try:
            all_news = self.get_all_news()
            filtered_news = []
            
            for item in all_news:
                item_tags = item.get("tags", [])
                if any(tag in item_tags for tag in tags):
                    filtered_news.append(item)
            
            return filtered_news
        except Exception as e:
            self.logger.error(f"根据标签获取新闻数据时发生错误: {str(e)}")
            return []
    
    def get_hot_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取热门新闻
        
        Args:
            limit: 结果数量限制
            
        Returns:
            热门新闻列表
        """
        try:
            all_news = self.get_all_news()
            
            # 计算热度分数
            for item in all_news:
                read_count = item.get("read_count", 0)
                comment_count = item.get("comment_count", 0)
                like_count = item.get("like_count", 0)
                share_count = item.get("share_count", 0)
                forward_count = item.get("forward_count", 0)
                
                # 热度计算公式
                hot_score = read_count + comment_count * 5 + like_count * 2 + share_count * 3 + forward_count * 3
                item["hot_score"] = hot_score
            
            # 按热度排序
            sorted_news = sorted(all_news, key=lambda x: x.get("hot_score", 0), reverse=True)
            
            return sorted_news[:limit]
        except Exception as e:
            self.logger.error(f"获取热门新闻时发生错误: {str(e)}")
            return []
    
    def get_news_count_by_platform(self) -> Dict[str, int]:
        """
        获取各平台新闻数量
        
        Returns:
            平台新闻数量字典
        """
        try:
            all_news = self.get_all_news()
            platform_counts = {}
            
            for item in all_news:
                platform = item.get("platform", "未知平台")
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            return platform_counts
        except Exception as e:
            self.logger.error(f"获取各平台新闻数量时发生错误: {str(e)}")
            return {}
    
    def get_news_count_by_date(self, days: int = 30) -> Dict[str, int]:
        """
        获取指定天数内每天的新闻数量
        
        Args:
            days: 天数
            
        Returns:
            日期新闻数量字典
        """
        try:
            all_news = self.get_all_news()
            date_counts = {}
            
            # 生成日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 初始化日期计数
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                date_counts[date_str] = 0
                current_date += timedelta(days=1)
            
            # 统计每天的新闻数量
            for item in all_news:
                try:
                    publish_time = item.get("publish_time", "")
                    if publish_time:
                        publish_date = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
                        date_str = publish_date.strftime("%Y-%m-%d")
                        
                        if date_str in date_counts:
                            date_counts[date_str] += 1
                except Exception as e:
                    self.logger.warning(f"解析新闻发布时间失败: {str(e)}")
                    continue
            
            return date_counts
        except Exception as e:
            self.logger.error(f"获取每天新闻数量时发生错误: {str(e)}")
            return {}
    
    def get_earliest_news_by_keyword(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        获取关键词最早的新闻
        
        Args:
            keyword: 关键词
            
        Returns:
            最早的新闻或None
        """
        try:
            news_list = self.get_news_by_keyword(keyword)
            if not news_list:
                return None
            
            # 按发布时间排序
            sorted_news = sorted(
                news_list,
                key=lambda x: datetime.strptime(x.get("publish_time", "9999-12-31 23:59:59"), "%Y-%m-%d %H:%M:%S")
            )
            
            return sorted_news[0] if sorted_news else None
        except Exception as e:
            self.logger.error(f"获取关键词最早新闻时发生错误: {str(e)}")
            return None
    
    def get_tag_distribution_by_keyword(self, keyword: str) -> Dict[str, int]:
        """
        获取关键词的标签分布
        
        Args:
            keyword: 关键词
            
        Returns:
            标签分布字典
        """
        try:
            news_list = self.get_news_by_keyword(keyword)
            tag_counts = {}
            
            for item in news_list:
                tags = item.get("tags", [])
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            return tag_counts
        except Exception as e:
            self.logger.error(f"获取关键词标签分布时发生错误: {str(e)}")
            return {}
    
    def get_platform_distribution_by_keyword(self, keyword: str) -> Dict[str, int]:
        """
        获取关键词的平台分布
        
        Args:
            keyword: 关键词
            
        Returns:
            平台分布字典
        """
        try:
            news_list = self.get_news_by_keyword(keyword)
            platform_counts = {}
            
            for item in news_list:
                platform = item.get("platform", "未知平台")
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            return platform_counts
        except Exception as e:
            self.logger.error(f"获取关键词平台分布时发生错误: {str(e)}")
            return {}
    
    def get_interaction_data_by_keyword(self, keyword: str) -> Dict[str, int]:
        """
        获取关键词的互动数据
        
        Args:
            keyword: 关键词
            
        Returns:
            互动数据字典
        """
        try:
            news_list = self.get_news_by_keyword(keyword)
            
            read_count = 0
            comment_count = 0
            like_count = 0
            share_count = 0
            forward_count = 0
            
            for item in news_list:
                read_count += item.get("read_count", 0)
                comment_count += item.get("comment_count", 0)
                like_count += item.get("like_count", 0)
                share_count += item.get("share_count", 0)
                forward_count += item.get("forward_count", 0)
            
            return {
                "read_count": read_count,
                "comment_count": comment_count,
                "like_count": like_count,
                "share_count": share_count,
                "forward_count": forward_count
            }
        except Exception as e:
            self.logger.error(f"获取关键词互动数据时发生错误: {str(e)}")
            return {
                "read_count": 0,
                "comment_count": 0,
                "like_count": 0,
                "share_count": 0,
                "forward_count": 0
            }
