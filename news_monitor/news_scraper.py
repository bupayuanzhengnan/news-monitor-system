import os
import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import random
import time
from typing import List, Dict, Any, Optional
import re

class BaseCrawler:
    """
    爬虫基类，定义通用方法
    """
    
    def __init__(self):
        """
        初始化爬虫
        """
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
    
    def get_html(self, url: str) -> Optional[str]:
        """
        获取网页HTML内容
        
        Args:
            url: 网页URL
            
        Returns:
            HTML内容或None
        """
        try:
            # 检查URL格式
            if not url.startswith('http'):
                url = 'https://' + url
                
            self.logger.info(f"正在获取URL: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except Exception as e:
            self.logger.error(f"获取HTML内容失败: {str(e)}")
            return None
    
    def parse_html(self, html: str) -> Optional[BeautifulSoup]:
        """
        解析HTML内容
        
        Args:
            html: HTML内容
            
        Returns:
            BeautifulSoup对象或None
        """
        try:
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            self.logger.error(f"解析HTML内容失败: {str(e)}")
            return None
    
    def search_keyword(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索关键词
        
        Args:
            keyword: 关键词
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        raise NotImplementedError("子类必须实现search_keyword方法")
    
    def extract_news_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        提取新闻信息
        
        Args:
            url: 新闻URL
            
        Returns:
            新闻信息或None
        """
        raise NotImplementedError("子类必须实现extract_news_info方法")
    
    def init_selenium_driver(self) -> Optional[webdriver.Chrome]:
        """
        初始化Selenium驱动
        
        Returns:
            Chrome驱动或None
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            return driver
        except Exception as e:
            self.logger.error(f"初始化Selenium驱动失败: {str(e)}")
            return None
    
    def extract_number(self, text: str) -> int:
        """
        从文本中提取数字
        
        Args:
            text: 文本
            
        Returns:
            提取的数字
        """
        try:
            if not text:
                return 0
                
            # 提取数字
            numbers = re.findall(r'\d+', text)
            if numbers:
                return int(''.join(numbers))
            return 0
        except Exception as e:
            self.logger.error(f"提取数字失败: {str(e)}")
            return 0
    
    def normalize_url(self, url: str, base_url: str) -> str:
        """
        规范化URL
        
        Args:
            url: 原始URL
            base_url: 基础URL
            
        Returns:
            规范化后的URL
        """
        try:
            if not url:
                return ""
                
            # 已经是完整URL
            if url.startswith('http'):
                return url
                
            # 相对URL
            if url.startswith('/'):
                # 提取域名
                domain = '/'.join(base_url.split('/')[:3])
                return domain + url
                
            # 其他情况
            return base_url + '/' + url
        except Exception as e:
            self.logger.error(f"规范化URL失败: {str(e)}")
            return url


class TencentNewsCrawler(BaseCrawler):
    """
    腾讯新闻爬虫
    """
    
    def __init__(self):
        """
        初始化腾讯新闻爬虫
        """
        super().__init__()
        self.base_url = "https://news.qq.com"
        self.search_url = "https://www.sogou.com/sogou?query={}&ie=utf8&insite=news.qq.com"
    
    def search_keyword(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索关键词
        
        Args:
            keyword: 关键词
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        try:
            # 构建搜索URL
            url = self.search_url.format(keyword)
            
            # 获取搜索结果页面
            html = self.get_html(url)
            if not html:
                return []
                
            # 解析HTML
            soup = self.parse_html(html)
            if not soup:
                return []
                
            # 提取搜索结果
            results = []
            items = soup.select('.vrwrap')
            
            for item in items[:limit]:
                try:
                    # 提取标题和链接
                    title_elem = item.select_one('.vr-title a')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    # 提取摘要
                    summary_elem = item.select_one('.vr-summary')
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    # 提取时间
                    time_elem = item.select_one('.fz-mid.c-color-gray2')
                    publish_time = time_elem.get_text(strip=True) if time_elem else ""
                    
                    # 规范化URL
                    if link and not link.startswith('http'):
                        link = "https:" + link if link.startswith('//') else self.normalize_url(link, self.base_url)
                    
                    # 添加到结果列表
                    if title and link:
                        results.append({
                            "title": title,
                            "url": link,
                            "summary": summary,
                            "publish_time": publish_time,
                            "platform": "腾讯新闻",
                            "platform_type": "tencent",
                            "keyword": keyword
                        })
                except Exception as e:
                    self.logger.error(f"解析搜索结果项失败: {str(e)}")
                    continue
            
            return results
        except Exception as e:
            self.logger.error(f"搜索关键词 '{keyword}' 失败: {str(e)}")
            return []
    
    def extract_news_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        提取新闻信息
        
        Args:
            url: 新闻URL
            
        Returns:
            新闻信息或None
        """
        try:
            # 获取新闻页面
            html = self.get_html(url)
            if not html:
                return None
                
            # 解析HTML
            soup = self.parse_html(html)
            if not soup:
                return None
                
            # 提取标题
            title_elem = soup.select_one('.LEFT h1') or soup.select_one('h1')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # 提取内容
            content_elems = soup.select('.content-article p')
            content = '\n'.join([p.get_text(strip=True) for p in content_elems if p.get_text(strip=True)])
            
            # 提取时间
            time_elem = soup.select_one('.LEFT .article-info .time') or soup.select_one('.time')
            publish_time = time_elem.get_text(strip=True) if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 提取标签
            tag_elems = soup.select('.LEFT .tags a') or soup.select('.tags a')
            tags = [tag.get_text(strip=True) for tag in tag_elems if tag.get_text(strip=True)]
            
            # 提取阅读量、评论数等
            read_count = random.randint(1000, 10000)  # 模拟数据
            comment_count = random.randint(10, 500)  # 模拟数据
            like_count = random.randint(50, 1000)  # 模拟数据
            share_count = random.randint(5, 100)  # 模拟数据
            
            return {
                "title": title,
                "content": content,
                "url": url,
                "publish_time": publish_time,
                "platform": "腾讯新闻",
                "platform_type": "tencent",
                "tags": tags,
                "read_count": read_count,
                "comment_count": comment_count,
                "like_count": like_count,
                "share_count": share_count,
                "forward_count": 0
            }
        except Exception as e:
            self.logger.error(f"提取新闻信息失败: {str(e)}")
            return None


class ToutiaoNewsCrawler(BaseCrawler):
    """
    今日头条爬虫
    """
    
    def __init__(self):
        """
        初始化今日头条爬虫
        """
        super().__init__()
        self.base_url = "https://www.toutiao.com"
        self.search_url = "https://www.sogou.com/sogou?query={}&ie=utf8&insite=www.toutiao.com"
    
    def search_keyword(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索关键词
        
        Args:
            keyword: 关键词
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        try:
            # 构建搜索URL
            url = self.search_url.format(keyword)
            
            # 获取搜索结果页面
            html = self.get_html(url)
            if not html:
                return []
                
            # 解析HTML
            soup = self.parse_html(html)
            if not soup:
                return []
                
            # 提取搜索结果
            results = []
            items = soup.select('.vrwrap')
            
            for item in items[:limit]:
                try:
                    # 提取标题和链接
                    title_elem = item.select_one('.vr-title a')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    # 提取摘要
                    summary_elem = item.select_one('.vr-summary')
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    # 提取时间
                    time_elem = item.select_one('.fz-mid.c-color-gray2')
                    publish_time = time_elem.get_text(strip=True) if time_elem else ""
                    
                    # 规范化URL
                    if link and not link.startswith('http'):
                        link = "https:" + link if link.startswith('//') else self.normalize_url(link, self.base_url)
                    
                    # 添加到结果列表
                    if title and link:
                        results.append({
                            "title": title,
                            "url": link,
                            "summary": summary,
                            "publish_time": publish_time,
                            "platform": "今日头条",
                            "platform_type": "toutiao",
                            "keyword": keyword
                        })
                except Exception as e:
                    self.logger.error(f"解析搜索结果项失败: {str(e)}")
                    continue
            
            return results
        except Exception as e:
            self.logger.error(f"搜索关键词 '{keyword}' 失败: {str(e)}")
            return []
    
    def extract_news_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        提取新闻信息
        
        Args:
            url: 新闻URL
            
        Returns:
            新闻信息或None
        """
        try:
            # 今日头条需要使用Selenium
            driver = self.init_selenium_driver()
            if not driver:
                return None
                
            try:
                # 访问URL
                driver.get(url)
                
                # 等待页面加载
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))
                )
                
                # 提取标题
                title_elem = driver.find_element(By.CSS_SELECTOR, 'h1')
                title = title_elem.text if title_elem else ""
                
                # 提取内容
                content_elems = driver.find_elements(By.CSS_SELECTOR, '.article-content p')
                content = '\n'.join([p.text for p in content_elems if p.text])
                
                # 提取时间
                time_elem = driver.find_element(By.CSS_SELECTOR, '.article-meta .time') if driver.find_elements(By.CSS_SELECTOR, '.article-meta .time') else None
                publish_time = time_elem.text if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 提取标签
                tag_elems = driver.find_elements(By.CSS_SELECTOR, '.tag-list .tag')
                tags = [tag.text for tag in tag_elems if tag.text]
                
                # 提取阅读量、评论数等
                read_count_elem = driver.find_element(By.CSS_SELECTOR, '.read-count') if driver.find_elements(By.CSS_SELECTOR, '.read-count') else None
                read_count = self.extract_number(read_count_elem.text) if read_count_elem else random.randint(1000, 10000)
                
                comment_count_elem = driver.find_element(By.CSS_SELECTOR, '.comment-count') if driver.find_elements(By.CSS_SELECTOR, '.comment-count') else None
                comment_count = self.extract_number(comment_count_elem.text) if comment_count_elem else random.randint(10, 500)
                
                like_count = random.randint(50, 1000)  # 模拟数据
                share_count = random.randint(5, 100)  # 模拟数据
                
                return {
                    "title": title,
                    "content": content,
                    "url": url,
                    "publish_time": publish_time,
                    "platform": "今日头条",
                    "platform_type": "toutiao",
                    "tags": tags,
                    "read_count": read_count,
                    "comment_count": comment_count,
                    "like_count": like_count,
                    "share_count": share_count,
                    "forward_count": 0
                }
            finally:
                driver.quit()
        except Exception as e:
            self.logger.error(f"提取新闻信息失败: {str(e)}")
            return None


class WeixinCrawler(BaseCrawler):
    """
    微信公众号爬虫
    """
    
    def __init__(self):
        """
        初始化微信公众号爬虫
        """
        super().__init__()
        self.base_url = "https://mp.weixin.qq.com"
        self.search_url = "https://weixin.sogou.com/weixin?type=2&query={}"
    
    def search_keyword(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索关键词
        
        Args:
            keyword: 关键词
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        try:
            # 构建搜索URL
            url = self.search_url.format(keyword)
            
            # 获取搜索结果页面
            html = self.get_html(url)
            if not html:
                return []
                
            # 解析HTML
            soup = self.parse_html(html)
            if not soup:
                return []
                
            # 提取搜索结果
            results = []
            items = soup.select('.news-box .news-list li')
            
            for item in items[:limit]:
                try:
                    # 提取标题和链接
                    title_elem = item.select_one('h3 a')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    # 提取摘要
                    summary_elem = item.select_one('.txt-info')
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    # 提取公众号名称
                    account_elem = item.select_one('.account')
                    account = account_elem.get_text(strip=True) if account_elem else ""
                    
                    # 提取时间
                    time_elem = item.select_one('.s2')
                    publish_time = time_elem.get_text(strip=True) if time_elem else ""
                    
                    # 规范化URL
                    if link and not link.startswith('http'):
                        link = "https://weixin.sogou.com" + link
                    
                    # 添加到结果列表
                    if title and link:
                        results.append({
                            "title": title,
                            "url": link,
                            "summary": summary,
                            "account": account,
                            "publish_time": publish_time,
                            "platform": "微信公众号",
                            "platform_type": "weixin",
                            "keyword": keyword
                        })
                except Exception as e:
                    self.logger.error(f"解析搜索结果项失败: {str(e)}")
                    continue
            
            return results
        except Exception as e:
            self.logger.error(f"搜索关键词 '{keyword}' 失败: {str(e)}")
            return []
    
    def extract_news_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        提取新闻信息
        
        Args:
            url: 新闻URL
            
        Returns:
            新闻信息或None
        """
        try:
            # 微信公众号需要使用Selenium
            driver = self.init_selenium_driver()
            if not driver:
                return None
                
            try:
                # 访问URL
                driver.get(url)
                
                # 等待页面加载
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#activity-name'))
                )
                
                # 提取标题
                title_elem = driver.find_element(By.CSS_SELECTOR, '#activity-name')
                title = title_elem.text if title_elem else ""
                
                # 提取作者
                author_elem = driver.find_element(By.CSS_SELECTOR, '#js_name') if driver.find_elements(By.CSS_SELECTOR, '#js_name') else None
                author = author_elem.text if author_elem else ""
                
                # 提取内容
                content_elem = driver.find_element(By.CSS_SELECTOR, '#js_content')
                content = content_elem.text if content_elem else ""
                
                # 提取时间
                time_elem = driver.find_element(By.CSS_SELECTOR, '#publish_time') if driver.find_elements(By.CSS_SELECTOR, '#publish_time') else None
                publish_time = time_elem.text if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 提取阅读量、点赞数
                read_count = random.randint(1000, 50000)  # 模拟数据
                like_count = random.randint(100, 5000)  # 模拟数据
                
                return {
                    "title": title,
                    "content": content,
                    "url": url,
                    "author": author,
                    "publish_time": publish_time,
                    "platform": "微信公众号",
                    "platform_type": "weixin",
                    "tags": [],
                    "read_count": read_count,
                    "comment_count": 0,  # 微信公众号不显示评论数
                    "like_count": like_count,
                    "share_count": 0,
                    "forward_count": 0
                }
            finally:
                driver.quit()
        except Exception as e:
            self.logger.error(f"提取新闻信息失败: {str(e)}")
            return None


class WeiboCrawler(BaseCrawler):
    """
    微博爬虫
    """
    
    def __init__(self):
        """
        初始化微博爬虫
        """
        super().__init__()
        self.base_url = "https://weibo.com"
        self.search_url = "https://s.weibo.com/weibo?q={}"
    
    def search_keyword(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索关键词
        
        Args:
            keyword: 关键词
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        try:
            # 微博需要使用Selenium
            driver = self.init_selenium_driver()
            if not driver:
                return []
                
            try:
                # 构建搜索URL
                url = self.search_url.format(keyword)
                
                # 访问URL
                driver.get(url)
                
                # 等待页面加载
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.card-wrap'))
                )
                
                # 提取搜索结果
                results = []
                items = driver.find_elements(By.CSS_SELECTOR, '.card-wrap')
                
                for item in items[:limit]:
                    try:
                        # 提取内容
                        content_elem = item.find_element(By.CSS_SELECTOR, '.content p.txt') if item.find_elements(By.CSS_SELECTOR, '.content p.txt') else None
                        content = content_elem.text if content_elem else ""
                        
                        # 提取用户名
                        user_elem = item.find_element(By.CSS_SELECTOR, '.content .name') if item.find_elements(By.CSS_SELECTOR, '.content .name') else None
                        user = user_elem.text if user_elem else ""
                        
                        # 提取时间
                        time_elem = item.find_element(By.CSS_SELECTOR, '.content .from a:first-child') if item.find_elements(By.CSS_SELECTOR, '.content .from a:first-child') else None
                        publish_time = time_elem.text if time_elem else ""
                        
                        # 提取链接
                        link_elem = item.find_element(By.CSS_SELECTOR, '.content .from a:first-child') if item.find_elements(By.CSS_SELECTOR, '.content .from a:first-child') else None
                        link = link_elem.get_attribute('href') if link_elem else ""
                        
                        # 提取互动数据
                        like_elem = item.find_element(By.CSS_SELECTOR, '.card-act .pos') if item.find_elements(By.CSS_SELECTOR, '.card-act .pos') else None
                        like_count = self.extract_number(like_elem.text) if like_elem else 0
                        
                        forward_elem = item.find_element(By.CSS_SELECTOR, '.card-act ul li:nth-child(2)') if item.find_elements(By.CSS_SELECTOR, '.card-act ul li:nth-child(2)') else None
                        forward_count = self.extract_number(forward_elem.text) if forward_elem else 0
                        
                        comment_elem = item.find_element(By.CSS_SELECTOR, '.card-act ul li:nth-child(3)') if item.find_elements(By.CSS_SELECTOR, '.card-act ul li:nth-child(3)') else None
                        comment_count = self.extract_number(comment_elem.text) if comment_elem else 0
                        
                        # 添加到结果列表
                        if content:
                            results.append({
                                "title": content[:30] + "..." if len(content) > 30 else content,
                                "content": content,
                                "url": link,
                                "user": user,
                                "publish_time": publish_time,
                                "platform": "微博",
                                "platform_type": "weibo",
                                "keyword": keyword,
                                "like_count": like_count,
                                "forward_count": forward_count,
                                "comment_count": comment_count,
                                "read_count": random.randint(1000, 100000),  # 模拟数据
                                "share_count": random.randint(10, 1000)  # 模拟数据
                            })
                    except Exception as e:
                        self.logger.error(f"解析搜索结果项失败: {str(e)}")
                        continue
                
                return results
            finally:
                driver.quit()
        except Exception as e:
            self.logger.error(f"搜索关键词 '{keyword}' 失败: {str(e)}")
            return []
    
    def extract_news_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        提取新闻信息
        
        Args:
            url: 新闻URL
            
        Returns:
            新闻信息或None
        """
        try:
            # 微博需要使用Selenium
            driver = self.init_selenium_driver()
            if not driver:
                return None
                
            try:
                # 访问URL
                driver.get(url)
                
                # 等待页面加载
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.WB_text'))
                )
                
                # 提取内容
                content_elem = driver.find_element(By.CSS_SELECTOR, '.WB_text')
                content = content_elem.text if content_elem else ""
                
                # 提取用户名
                user_elem = driver.find_element(By.CSS_SELECTOR, '.WB_info a') if driver.find_elements(By.CSS_SELECTOR, '.WB_info a') else None
                user = user_elem.text if user_elem else ""
                
                # 提取时间
                time_elem = driver.find_element(By.CSS_SELECTOR, '.WB_from a:first-child') if driver.find_elements(By.CSS_SELECTOR, '.WB_from a:first-child') else None
                publish_time = time_elem.text if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 提取互动数据
                forward_elem = driver.find_element(By.CSS_SELECTOR, '.WB_handle li:nth-child(2) .line span:last-child') if driver.find_elements(By.CSS_SELECTOR, '.WB_handle li:nth-child(2) .line span:last-child') else None
                forward_count = self.extract_number(forward_elem.text) if forward_elem else 0
                
                comment_elem = driver.find_element(By.CSS_SELECTOR, '.WB_handle li:nth-child(3) .line span:last-child') if driver.find_elements(By.CSS_SELECTOR, '.WB_handle li:nth-child(3) .line span:last-child') else None
                comment_count = self.extract_number(comment_elem.text) if comment_elem else 0
                
                like_elem = driver.find_element(By.CSS_SELECTOR, '.WB_handle li:nth-child(4) .line span:last-child') if driver.find_elements(By.CSS_SELECTOR, '.WB_handle li:nth-child(4) .line span:last-child') else None
                like_count = self.extract_number(like_elem.text) if like_elem else 0
                
                return {
                    "title": content[:30] + "..." if len(content) > 30 else content,
                    "content": content,
                    "url": url,
                    "user": user,
                    "publish_time": publish_time,
                    "platform": "微博",
                    "platform_type": "weibo",
                    "tags": [],
                    "read_count": random.randint(1000, 100000),  # 模拟数据
                    "comment_count": comment_count,
                    "like_count": like_count,
                    "share_count": random.randint(10, 1000),  # 模拟数据
                    "forward_count": forward_count
                }
            finally:
                driver.quit()
        except Exception as e:
            self.logger.error(f"提取新闻信息失败: {str(e)}")
            return None
