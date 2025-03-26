import os
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
from wordcloud import WordCloud
import jieba

class TrendAnalyzer:
    """
    趋势分析类，提供舆情趋势分析和可视化功能
    """
    
    def __init__(self, news_data_manager, static_dir):
        """
        初始化趋势分析器
        
        Args:
            news_data_manager: 新闻数据管理器
            static_dir: 静态文件目录
        """
        self.news_data_manager = news_data_manager
        self.static_dir = static_dir
        self.images_dir = os.path.join(static_dir, "images")
        self.logger = logging.getLogger(__name__)
        
        # 确保图片目录存在
        os.makedirs(self.images_dir, exist_ok=True)
    
    def analyze_trend(self, keyword: str, days: int = 30) -> Dict[str, Any]:
        """
        分析关键词趋势
        
        Args:
            keyword: 关键词
            days: 天数
            
        Returns:
            趋势分析结果
        """
        try:
            self.logger.info(f"开始分析关键词 '{keyword}' 的趋势")
            
            # 获取关键词相关新闻
            news_list = self.news_data_manager.get_news_by_keyword(keyword)
            
            if not news_list:
                self.logger.warning(f"未找到关键词 '{keyword}' 的相关新闻")
                return {}
            
            # 生成趋势图
            trend_chart_path = self.generate_trend_chart(keyword, news_list, days)
            
            # 计算热度变化
            heat_change = self.calculate_heat_change(news_list)
            
            # 分析起源
            origin_analysis = self.analyze_origin(keyword, news_list)
            
            # 分析标签分布
            tag_distribution = self.news_data_manager.get_tag_distribution_by_keyword(keyword)
            tag_chart_path = self.generate_tag_chart(keyword, tag_distribution)
            
            # 生成词云
            wordcloud_path = self.generate_wordcloud(keyword, news_list)
            
            # 情感分析
            sentiment_analysis = self.analyze_sentiment(news_list)
            sentiment_chart_path = self.generate_sentiment_chart(keyword, sentiment_analysis)
            
            # 平台分布
            platform_distribution = self.news_data_manager.get_platform_distribution_by_keyword(keyword)
            platform_chart_path = self.generate_platform_chart(keyword, platform_distribution)
            
            # 互动数据
            interaction_data = self.news_data_manager.get_interaction_data_by_keyword(keyword)
            interaction_chart_path = self.generate_interaction_chart(keyword, interaction_data)
            
            # 生成分析结论
            conclusion = self.generate_conclusion(keyword, heat_change, sentiment_analysis, platform_distribution)
            
            # 返回分析结果
            return {
                "keyword": keyword,
                "days": days,
                "trend_chart_path": trend_chart_path,
                "heat_change": heat_change,
                "origin_analysis": origin_analysis,
                "tag_distribution": tag_distribution,
                "tag_chart_path": tag_chart_path,
                "wordcloud_path": wordcloud_path,
                "sentiment_analysis": sentiment_analysis,
                "sentiment_chart_path": sentiment_chart_path,
                "platform_distribution": platform_distribution,
                "platform_chart_path": platform_chart_path,
                "interaction_data": interaction_data,
                "interaction_chart_path": interaction_chart_path,
                "conclusion": conclusion
            }
            
        except Exception as e:
            self.logger.error(f"分析关键词趋势时发生错误: {str(e)}")
            return {}
    
    def generate_trend_chart(self, keyword: str, news_list: List[Dict[str, Any]], days: int = 30) -> str:
        """
        生成趋势图
        
        Args:
            keyword: 关键词
            news_list: 新闻列表
            days: 天数
            
        Returns:
            趋势图路径
        """
        try:
            # 生成日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 初始化日期计数
            date_counts = {}
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                date_counts[date_str] = 0
                current_date += timedelta(days=1)
            
            # 统计每天的新闻数量
            for item in news_list:
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
            
            # 准备数据
            dates = list(date_counts.keys())
            counts = list(date_counts.values())
            
            # 创建图表
            plt.figure(figsize=(10, 6))
            plt.plot(dates, counts, marker='o', linestyle='-', color='#3498db', linewidth=2)
            plt.fill_between(dates, counts, color='#3498db', alpha=0.2)
            
            # 设置标题和标签
            plt.title(f"关键词 '{keyword}' 的热度趋势", fontsize=16)
            plt.xlabel("日期", fontsize=12)
            plt.ylabel("新闻数量", fontsize=12)
            
            # 设置x轴标签
            plt.xticks(rotation=45)
            
            # 设置网格
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            chart_filename = f"trend_chart_{keyword}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            chart_path = os.path.join(self.images_dir, chart_filename)
            plt.savefig(chart_path)
            plt.close()
            
            # 返回相对路径
            return f"/static/images/{chart_filename}"
            
        except Exception as e:
            self.logger.error(f"生成趋势图时发生错误: {str(e)}")
            return "/static/images/trend_chart_default.png"
    
    def calculate_heat_change(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算热度变化
        
        Args:
            news_list: 新闻列表
            
        Returns:
            热度变化数据
        """
        try:
            # 按发布时间排序
            sorted_news = sorted(
                news_list,
                key=lambda x: datetime.strptime(x.get("publish_time", "9999-12-31 23:59:59"), "%Y-%m-%d %H:%M:%S")
            )
            
            if not sorted_news:
                return {
                    "24h_change": 0,
                    "24h_change_rate": 0.0,
                    "7d_change": 0,
                    "7d_change_rate": 0.0,
                    "trend_direction": "稳定"
                }
            
            # 获取当前时间
            now = datetime.now()
            
            # 计算24小时内的新闻数量
            news_24h = [
                item for item in sorted_news
                if (now - datetime.strptime(item.get("publish_time", ""), "%Y-%m-%d %H:%M:%S")).total_seconds() <= 24 * 3600
            ]
            
            # 计算24-48小时内的新闻数量
            news_24h_48h = [
                item for item in sorted_news
                if 24 * 3600 < (now - datetime.strptime(item.get("publish_time", ""), "%Y-%m-%d %H:%M:%S")).total_seconds() <= 48 * 3600
            ]
            
            # 计算7天内的新闻数量
            news_7d = [
                item for item in sorted_news
                if (now - datetime.strptime(item.get("publish_time", ""), "%Y-%m-%d %H:%M:%S")).total_seconds() <= 7 * 24 * 3600
            ]
            
            # 计算7-14天内的新闻数量
            news_7d_14d = [
                item for item in sorted_news
                if 7 * 24 * 3600 < (now - datetime.strptime(item.get("publish_time", ""), "%Y-%m-%d %H:%M:%S")).total_seconds() <= 14 * 24 * 3600
            ]
            
            # 计算变化
            count_24h = len(news_24h)
            count_24h_48h = len(news_24h_48h)
            count_7d = len(news_7d)
            count_7d_14d = len(news_7d_14d)
            
            # 计算24小时变化
            change_24h = count_24h - count_24h_48h
            change_rate_24h = (change_24h / count_24h_48h * 100) if count_24h_48h > 0 else 0.0
            
            # 计算7天变化
            change_7d = count_7d - count_7d_14d
            change_rate_7d = (change_7d / count_7d_14d * 100) if count_7d_14d > 0 else 0.0
            
            # 判断趋势方向
            if change_rate_24h > 50:
                trend_direction = "显著上升"
            elif change_rate_24h > 20:
                trend_direction = "缓慢上升"
            elif change_rate_24h < -50:
                trend_direction = "显著下降"
            elif change_rate_24h < -20:
                trend_direction = "缓慢下降"
            else:
                trend_direction = "稳定"
            
            return {
                "24h_change": change_24h,
                "24h_change_rate": round(change_rate_24h, 2),
                "7d_change": change_7d,
                "7d_change_rate": round(change_rate_7d, 2),
                "trend_direction": trend_direction
            }
            
        except Exception as e:
            self.logger.error(f"计算热度变化时发生错误: {str(e)}")
            return {
                "24h_change": 0,
                "24h_change_rate": 0.0,
                "7d_change": 0,
                "7d_change_rate": 0.0,
                "trend_direction": "稳定"
            }
    
    def analyze_origin(self, keyword: str, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析起源
        
        Args:
            keyword: 关键词
            news_list: 新闻列表
            
        Returns:
            起源分析结果
        """
        try:
            # 获取最早的新闻
            earliest_news = self.news_data_manager.get_earliest_news_by_keyword(keyword)
            
            if not earliest_news:
                return {
                    "earliest_news": {},
                    "earliest_date": "",
                    "origin_platform": "",
                    "possible_causes": []
                }
            
            # 获取最早日期和平台
            earliest_date = earliest_news.get("publish_time", "").split(" ")[0]
            origin_platform = earliest_news.get("platform", "")
            
            # 生成可能原因
            possible_causes = [
                f"由于{keyword}相关事件的突发性，引发了公众关注",
                f"{keyword}领域的最新研究成果公布",
                f"权威媒体对{keyword}进行了深度报道"
            ]
            
            return {
                "earliest_news": earliest_news,
                "earliest_date": earliest_date,
                "origin_platform": origin_platform,
                "possible_causes": possible_causes
            }
            
        except Exception as e:
            self.logger.error(f"分析起源时发生错误: {str(e)}")
            return {
                "earliest_news": {},
                "earliest_date": "",
                "origin_platform": "",
                "possible_causes": []
            }
    
    def generate_tag_chart(self, keyword: str, tag_distribution: Dict[str, int]) -> str:
        """
        生成标签分布图
        
        Args:
            keyword: 关键词
            tag_distribution: 标签分布
            
        Returns:
            标签分布图路径
        """
        try:
            if not tag_distribution:
                return "/static/images/tag_chart_default.png"
            
            # 准备数据
            tags = list(tag_distribution.keys())
            counts = list(tag_distribution.values())
            
            # 创建图表
            plt.figure(figsize=(10, 6))
            bars = plt.bar(tags, counts, color='#2ecc71')
            
            # 添加数值标签
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            # 设置标题和标签
            plt.title(f"关键词 '{keyword}' 的标签分布", fontsize=16)
            plt.xlabel("标签", fontsize=12)
            plt.ylabel("数量", fontsize=12)
            
            # 设置x轴标签
            plt.xticks(rotation=45)
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            chart_filename = f"tag_chart_{keyword}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            chart_path = os.path.join(self.images_dir, chart_filename)
            plt.savefig(chart_path)
            plt.close()
            
            # 返回相对路径
            return f"/static/images/{chart_filename}"
            
        except Exception as e:
            self.logger.error(f"生成标签分布图时发生错误: {str(e)}")
            return "/static/images/tag_chart_default.png"
    
    def generate_wordcloud(self, keyword: str, news_list: List[Dict[str, Any]]) -> str:
        """
        生成词云
        
        Args:
            keyword: 关键词
            news_list: 新闻列表
            
        Returns:
            词云图路径
        """
        try:
            if not news_list:
                return "/static/images/wordcloud_default.png"
            
            # 提取所有标题和内容
            text = ""
            for item in news_list:
                title = item.get("title", "")
                content = item.get("content", "")
                text += title + " " + content + " "
            
            # 分词
            words = jieba.cut(text)
            word_space_split = " ".join(words)
            
            # 创建词云
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                max_words=100,
                max_font_size=150,
                random_state=42
            ).generate(word_space_split)
            
            # 创建图表
            plt.figure(figsize=(10, 6))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            
            # 保存图表
            chart_filename = f"wordcloud_{keyword}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            chart_path = os.path.join(self.images_dir, chart_filename)
            plt.savefig(chart_path)
            plt.close()
            
            # 返回相对路径
            return f"/static/images/{chart_filename}"
            
        except Exception as e:
            self.logger.error(f"生成词云时发生错误: {str(e)}")
            return "/static/images/wordcloud_default.png"
    
    def analyze_sentiment(self, news_list: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        情感分析
        
        Args:
            news_list: 新闻列表
            
        Returns:
            情感分析结果
        """
        try:
            # 模拟情感分析结果
            total = len(news_list)
            if total == 0:
                return {"正面": 0, "中性": 0, "负面": 0}
            
            # 随机生成情感分布
            positive = random.randint(int(total * 0.3), int(total * 0.6))
            negative = random.randint(int(total * 0.1), int(total * 0.3))
            neutral = total - positive - negative
            
            return {
                "正面": positive,
                "中性": neutral,
                "负面": negative
            }
            
        except Exception as e:
            self.logger.error(f"情感分析时发生错误: {str(e)}")
            return {"正面": 0, "中性": 0, "负面": 0}
    
    def generate_sentiment_chart(self, keyword: str, sentiment_analysis: Dict[str, int]) -> str:
        """
        生成情感分析图
        
        Args:
            keyword: 关键词
            sentiment_analysis: 情感分析结果
            
        Returns:
            情感分析图路径
        """
        try:
            if not sentiment_analysis:
                return "/static/images/sentiment_chart_default.png"
            
            # 准备数据
            labels = list(sentiment_analysis.keys())
            sizes = list(sentiment_analysis.values())
            colors = ['#2ecc71', '#3498db', '#e74c3c']
            
            # 创建图表
            plt.figure(figsize=(8, 8))
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, shadow=True)
            plt.axis('equal')
            
            # 设置标题
            plt.title(f"关键词 '{keyword}' 的情感分析", fontsize=16)
            
            # 保存图表
            chart_filename = f"sentiment_chart_{keyword}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            chart_path = os.path.join(self.images_dir, chart_filename)
            plt.savefig(chart_path)
            plt.close()
            
            # 返回相对路径
            return f"/static/images/{chart_filename}"
            
        except Exception as e:
            self.logger.error(f"生成情感分析图时发生错误: {str(e)}")
            return "/static/images/sentiment_chart_default.png"
    
    def generate_platform_chart(self, keyword: str, platform_distribution: Dict[str, int]) -> str:
        """
        生成平台分布图
        
        Args:
            keyword: 关键词
            platform_distribution: 平台分布
            
        Returns:
            平台分布图路径
        """
        try:
            if not platform_distribution:
                return "/static/images/platform_chart_default.png"
            
            # 准备数据
            platforms = list(platform_distribution.keys())
            counts = list(platform_distribution.values())
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
            
            # 创建图表
            plt.figure(figsize=(8, 8))
            plt.pie(counts, labels=platforms, colors=colors[:len(platforms)], autopct='%1.1f%%', startangle=90, shadow=True)
            plt.axis('equal')
            
            # 设置标题
            plt.title(f"关键词 '{keyword}' 的平台分布", fontsize=16)
            
            # 保存图表
            chart_filename = f"platform_chart_{keyword}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            chart_path = os.path.join(self.images_dir, chart_filename)
            plt.savefig(chart_path)
            plt.close()
            
            # 返回相对路径
            return f"/static/images/{chart_filename}"
            
        except Exception as e:
            self.logger.error(f"生成平台分布图时发生错误: {str(e)}")
            return "/static/images/platform_chart_default.png"
    
    def generate_interaction_chart(self, keyword: str, interaction_data: Dict[str, int]) -> str:
        """
        生成互动数据图
        
        Args:
            keyword: 关键词
            interaction_data: 互动数据
            
        Returns:
            互动数据图路径
        """
        try:
            if not interaction_data:
                return "/static/images/interaction_chart_default.png"
            
            # 准备数据
            labels = ["阅读量", "评论数", "点赞数", "分享数", "转发数"]
            values = [
                interaction_data.get("read_count", 0),
                interaction_data.get("comment_count", 0),
                interaction_data.get("like_count", 0),
                interaction_data.get("share_count", 0),
                interaction_data.get("forward_count", 0)
            ]
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
            
            # 创建图表
            plt.figure(figsize=(10, 6))
            bars = plt.bar(labels, values, color=colors)
            
            # 添加数值标签
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            # 设置标题和标签
            plt.title(f"关键词 '{keyword}' 的互动数据", fontsize=16)
            plt.xlabel("互动类型", fontsize=12)
            plt.ylabel("数量", fontsize=12)
            
            # 设置y轴范围
            plt.ylim(0, max(values) * 1.2)
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            chart_filename = f"interaction_chart_{keyword}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            chart_path = os.path.join(self.images_dir, chart_filename)
            plt.savefig(chart_path)
            plt.close()
            
            # 返回相对路径
            return f"/static/images/{chart_filename}"
            
        except Exception as e:
            self.logger.error(f"生成互动数据图时发生错误: {str(e)}")
            return "/static/images/interaction_chart_default.png"
    
    def generate_conclusion(self, keyword: str, heat_change: Dict[str, Any], sentiment_analysis: Dict[str, int], platform_distribution: Dict[str, int]) -> str:
        """
        生成分析结论
        
        Args:
            keyword: 关键词
            heat_change: 热度变化
            sentiment_analysis: 情感分析结果
            platform_distribution: 平台分布
            
        Returns:
            分析结论
        """
        try:
            # 热度评估
            trend_direction = heat_change.get("trend_direction", "稳定")
            change_rate_24h = heat_change.get("24h_change_rate", 0.0)
            
            # 热度评估
            if change_rate_24h > 50:
                heat_assessment = "较高，引起广泛关注"
            elif change_rate_24h > 20:
                heat_assessment = "中等，有一定关注度"
            else:
                heat_assessment = "较低，关注度有限"
            
            # 24小时热度变化
            if change_rate_24h > 50:
                heat_24h = "24小时内热度大幅上升，需密切关注"
            elif change_rate_24h > 20:
                heat_24h = "24小时内热度明显上升，建议关注"
            elif change_rate_24h > -20:
                heat_24h = "24小时内热度变化不大，保持稳定"
            elif change_rate_24h > -50:
                heat_24h = "24小时内热度明显下降，关注度减弱"
            else:
                heat_24h = "24小时内热度大幅下降，话题可能即将结束"
            
            # 互动评估
            total_sentiment = sum(sentiment_analysis.values())
            if total_sentiment > 100:
                interaction_assessment = "很高，引发热烈讨论"
            elif total_sentiment > 50:
                interaction_assessment = "较高，有较多讨论"
            else:
                interaction_assessment = "一般，讨论度有限"
            
            # 情感倾向
            positive = sentiment_analysis.get("正面", 0)
            neutral = sentiment_analysis.get("中性", 0)
            negative = sentiment_analysis.get("负面", 0)
            
            if positive > negative * 2:
                sentiment_tendency = "整体情感倾向积极正面，正面评价占主导"
            elif negative > positive * 2:
                sentiment_tendency = "整体情感倾向消极负面，负面评价较多"
            elif positive > negative:
                sentiment_tendency = "情感倾向偏正面，但也有一定负面声音"
            elif negative > positive:
                sentiment_tendency = "情感倾向偏负面，但也有一定正面评价"
            else:
                sentiment_tendency = "情感倾向中性，正负面评价较为平衡"
            
            # 建议1：热度相关
            if trend_direction == "显著上升" or trend_direction == "缓慢上升":
                suggestion1 = "话题热度上升，建议加强监控，及时跟进最新动态"
            elif trend_direction == "显著下降" or trend_direction == "缓慢下降":
                suggestion1 = "话题热度下降，可适当减少关注频率"
            else:
                suggestion1 = "保持常规监控，关注话题是否有新的发展"
            
            # 建议2：平台相关
            suggestion2 = "关注重点平台的讨论情况，把握舆论走向"
            
            # 建议3：情感相关
            if negative > positive:
                suggestion3 = "负面情绪较多，建议关注负面言论，及时应对可能的舆情风险"
            elif positive > negative * 2:
                suggestion3 = "正面评价占主导，可适当引导扩大正面影响"
            else:
                suggestion3 = "情感倾向较为平衡，需关注是否有情绪变化趋势"
            
            # 生成结论
            conclusion = f"""关键词 '{keyword}' 的舆情分析结论：

1. 热度评估：该话题热度{heat_assessment}。

2. 趋势判断：话题热度呈{trend_direction}趋势，{heat_24h}。

3. 互动评估：话题互动率{interaction_assessment}。

4. 情感倾向：话题{sentiment_tendency}。

5. 建议：
- {suggestion1}
- {suggestion2}
- {suggestion3}
"""
            
            return conclusion
            
        except Exception as e:
            self.logger.error(f"生成分析结论时发生错误: {str(e)}")
            return f"关键词 '{keyword}' 的舆情分析结论生成失败。"
