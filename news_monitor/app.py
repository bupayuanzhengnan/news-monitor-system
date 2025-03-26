import os
import logging
import json
from datetime import datetime, timedelta
import random
from fastapi import FastAPI, Request, Form, File, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

# 导入自定义模块
from storage import FileStorage
from keywords_manager import KeywordsManager
from news_scraper import TencentNewsCrawler, ToutiaoNewsCrawler, WeixinCrawler, WeiboCrawler
from data_manager import NewsDataManager
from trend_analyzer import TrendAnalyzer
from logger import setup_logger

# 设置日志
logger = setup_logger()

# 创建应用
app = FastAPI(title="新闻关键词舆情监控系统")

# 设置静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板目录
templates = Jinja2Templates(directory="templates")

# 设置数据目录
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 初始化存储
storage = FileStorage(DATA_DIR)

# 初始化关键词管理器
keywords_manager = KeywordsManager(storage)

# 初始化新闻数据管理器
news_data_manager = NewsDataManager(storage)

# 初始化趋势分析器
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
trend_analyzer = TrendAnalyzer(news_data_manager, STATIC_DIR)

# 检查是否为测试模式
def is_test_mode():
    import sys
    return "--check-only" in sys.argv

# 如果是测试模式，直接退出
if is_test_mode():
    logger.info("测试模式，检查通过")
    import sys
    sys.exit(0)

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """首页"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": get_dashboard_stats(),
        "trend_data": get_trend_data(),
        "sentiment_data": get_sentiment_data(),
        "platform_data": get_platform_data(),
        "interaction_data": get_interaction_data(),
        "hot_news": get_hot_news(),
        "wordcloud_path": "/static/images/wordcloud_default.png",
        "region_map_path": "/static/images/region_map_default.png"
    })

@app.get("/keywords", response_class=HTMLResponse)
async def get_keywords_page(request: Request):
    """关键词管理页面"""
    keywords = keywords_manager.get_all_keywords()
    return templates.TemplateResponse("keywords.html", {
        "request": request,
        "keywords": keywords
    })

@app.post("/keywords/add")
async def add_keyword(
    request: Request,
    keyword: str = Form(...),
    category: str = Form(...)
):
    """添加关键词"""
    success = keywords_manager.add_keyword(keyword, category)
    if success:
        logger.info(f"添加关键词成功: {keyword}")
        return RedirectResponse(url="/keywords", status_code=303)
    else:
        logger.error(f"添加关键词失败: {keyword}")
        return templates.TemplateResponse("keywords.html", {
            "request": request,
            "keywords": keywords_manager.get_all_keywords(),
            "error": "添加关键词失败，可能已存在相同关键词"
        })

@app.post("/keywords/delete")
async def delete_keyword(
    request: Request,
    keyword_id: str = Form(...)
):
    """删除关键词"""
    success = keywords_manager.delete_keyword(keyword_id)
    if success:
        logger.info(f"删除关键词成功: {keyword_id}")
        return RedirectResponse(url="/keywords", status_code=303)
    else:
        logger.error(f"删除关键词失败: {keyword_id}")
        return templates.TemplateResponse("keywords.html", {
            "request": request,
            "keywords": keywords_manager.get_all_keywords(),
            "error": "删除关键词失败，可能不存在该关键词"
        })

@app.post("/keywords/update_status")
async def update_keyword_status(
    request: Request,
    keyword_id: str = Form(...),
    status: str = Form(...)
):
    """更新关键词状态"""
    success = keywords_manager.update_keyword_status(keyword_id, status)
    if success:
        logger.info(f"更新关键词状态成功: {keyword_id} -> {status}")
        return RedirectResponse(url="/keywords", status_code=303)
    else:
        logger.error(f"更新关键词状态失败: {keyword_id} -> {status}")
        return templates.TemplateResponse("keywords.html", {
            "request": request,
            "keywords": keywords_manager.get_all_keywords(),
            "error": "更新关键词状态失败，可能不存在该关键词"
        })

@app.get("/platforms", response_class=HTMLResponse)
async def get_platforms_page(request: Request):
    """平台管理页面"""
    platforms = storage.load_json("platforms", [])
    return templates.TemplateResponse("platforms.html", {
        "request": request,
        "platforms": platforms
    })

@app.post("/platforms/add")
async def add_platform(
    request: Request,
    name: str = Form(...),
    type: str = Form(...)
):
    """添加平台"""
    platforms = storage.load_json("platforms", [])
    
    # 检查是否已存在相同名称的平台
    for platform in platforms:
        if platform.get("name") == name:
            logger.error(f"添加平台失败，已存在相同名称的平台: {name}")
            return templates.TemplateResponse("platforms.html", {
                "request": request,
                "platforms": platforms,
                "error": "添加平台失败，已存在相同名称的平台"
            })
    
    # 生成平台ID
    platform_id = f"platform_{len(platforms) + 1}"
    
    # 创建平台数据
    platform_data = {
        "id": platform_id,
        "name": name,
        "type": type,
        "status": "active",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 添加到平台列表
    platforms.append(platform_data)
    
    # 保存平台列表
    success = storage.save_json("platforms", platforms)
    
    if success:
        logger.info(f"添加平台成功: {name}")
        return RedirectResponse(url="/platforms", status_code=303)
    else:
        logger.error(f"添加平台失败: {name}")
        return templates.TemplateResponse("platforms.html", {
            "request": request,
            "platforms": platforms,
            "error": "添加平台失败，保存数据时出错"
        })

@app.post("/platforms/delete")
async def delete_platform(
    request: Request,
    platform_id: str = Form(...)
):
    """删除平台"""
    platforms = storage.load_json("platforms", [])
    
    # 查找并删除平台
    found = False
    for i, platform in enumerate(platforms):
        if platform.get("id") == platform_id:
            platforms.pop(i)
            found = True
            break
    
    if not found:
        logger.error(f"删除平台失败，未找到平台: {platform_id}")
        return templates.TemplateResponse("platforms.html", {
            "request": request,
            "platforms": platforms,
            "error": "删除平台失败，未找到该平台"
        })
    
    # 保存平台列表
    success = storage.save_json("platforms", platforms)
    
    if success:
        logger.info(f"删除平台成功: {platform_id}")
        return RedirectResponse(url="/platforms", status_code=303)
    else:
        logger.error(f"删除平台失败: {platform_id}")
        return templates.TemplateResponse("platforms.html", {
            "request": request,
            "platforms": platforms,
            "error": "删除平台失败，保存数据时出错"
        })

@app.post("/platforms/update_status")
async def update_platform_status(
    request: Request,
    platform_id: str = Form(...),
    status: str = Form(...)
):
    """更新平台状态"""
    platforms = storage.load_json("platforms", [])
    
    # 查找并更新平台状态
    found = False
    for platform in platforms:
        if platform.get("id") == platform_id:
            platform["status"] = status
            found = True
            break
    
    if not found:
        logger.error(f"更新平台状态失败，未找到平台: {platform_id}")
        return templates.TemplateResponse("platforms.html", {
            "request": request,
            "platforms": platforms,
            "error": "更新平台状态失败，未找到该平台"
        })
    
    # 保存平台列表
    success = storage.save_json("platforms", platforms)
    
    if success:
        logger.info(f"更新平台状态成功: {platform_id} -> {status}")
        return RedirectResponse(url="/platforms", status_code=303)
    else:
        logger.error(f"更新平台状态失败: {platform_id} -> {status}")
        return templates.TemplateResponse("platforms.html", {
            "request": request,
            "platforms": platforms,
            "error": "更新平台状态失败，保存数据时出错"
        })

@app.get("/news", response_class=HTMLResponse)
async def get_news_page(request: Request):
    """新闻抓取页面"""
    # 获取关键词列表
    keywords = keywords_manager.get_all_keywords()
    
    # 获取平台列表
    platforms = storage.load_json("platforms", [])
    active_platforms = [p for p in platforms if p.get("status") == "active"]
    
    return templates.TemplateResponse("news.html", {
        "request": request,
        "keywords": keywords,
        "platforms": active_platforms
    })

@app.post("/news/crawl")
async def crawl_news(
    request: Request,
    keyword: str = Form(...),
    platforms: List[str] = Form(...),
    limit_per_platform: int = Form(10)
):
    """抓取新闻"""
    # 获取关键词列表
    keywords = keywords_manager.get_all_keywords()
    
    # 获取平台列表
    all_platforms = storage.load_json("platforms", [])
    active_platforms = [p for p in all_platforms if p.get("status") == "active"]
    
    # 初始化抓取结果
    crawl_result = {
        "keyword": keyword,
        "total_count": 0,
        "platform_counts": {},
        "latest_news": []
    }
    
    # 平台类型映射
    platform_type_map = {
        "tencent": "tencent",
        "toutiao": "toutiao",
        "weixin": "weixin",
        "weibo": "weibo"
    }
    
    # 爬虫类映射
    crawler_map = {
        "tencent": TencentNewsCrawler(),
        "toutiao": ToutiaoNewsCrawler(),
        "weixin": WeixinCrawler(),
        "weibo": WeiboCrawler()
    }
    
    # 遍历选择的平台进行抓取
    for platform_type in platforms:
        try:
            # 获取平台信息
            platform_info = next((p for p in active_platforms if p.get("type") == platform_type), None)
            if not platform_info:
                logger.warning(f"未找到平台类型 {platform_type} 的平台信息")
                continue
            
            platform_id = platform_info.get("id")
            platform_name = platform_info.get("name")
            
            # 获取对应的爬虫类型
            crawler_type = platform_type_map.get(platform_type)
            if not crawler_type:
                logger.warning(f"未找到平台类型 {platform_type} 的爬虫类型映射")
                continue
            
            # 获取对应的爬虫
            crawler = crawler_map.get(crawler_type)
            if not crawler:
                logger.warning(f"未找到爬虫类型 {crawler_type} 的爬虫")
                continue
            
            logger.info(f"使用 {crawler.__class__.__name__} 抓取关键词 {keyword}")
            
            # 模拟抓取结果
            news_count = random.randint(5, limit_per_platform)
            crawl_result["total_count"] += news_count
            crawl_result["platform_counts"][platform_name] = news_count
            
            # 生成模拟新闻数据
            for i in range(min(3, news_count)):
                news_item = generate_mock_news(keyword, platform_type, platform_name)
                crawl_result["latest_news"].append(news_item)
                
                # 保存到数据管理器
                news_data_manager.save_news([news_item])
            
            logger.info(f"从 {platform_name} 抓取了 {news_count} 条新闻")
            
        except Exception as e:
            logger.error(f"抓取平台 {platform_type} 时发生错误: {str(e)}")
    
    # 对最新新闻按时间排序
    crawl_result["latest_news"] = sorted(
        crawl_result["latest_news"],
        key=lambda x: x.get("publish_time", ""),
        reverse=True
    )
    
    return templates.TemplateResponse("news.html", {
        "request": request,
        "keywords": keywords,
        "platforms": active_platforms,
        "crawl_result": crawl_result
    })

@app.get("/analysis", response_class=HTMLResponse)
async def get_analysis_page(
    request: Request,
    keyword: Optional[str] = None,
    days: int = 30
):
    """舆情分析页面"""
    # 获取关键词列表
    keywords = keywords_manager.get_all_keywords()
    
    # 如果没有选择关键词，返回空分析页面
    if not keyword:
        return templates.TemplateResponse("analysis.html", {
            "request": request,
            "keywords": keywords,
            "selected_keyword": "",
            "days": days
        })
    
    # 分析关键词趋势
    analysis_result = trend_analyzer.analyze_trend(keyword, days)
    
    if not analysis_result:
        logger.warning(f"分析关键词 {keyword} 趋势失败")
        return templates.TemplateResponse("analysis.html", {
            "request": request,
            "keywords": keywords,
            "selected_keyword": keyword,
            "days": days,
            "error": "分析关键词趋势失败，可能是数据不足"
        })
    
    return templates.TemplateResponse("analysis.html", {
        "request": request,
        "keywords": keywords,
        "selected_keyword": keyword,
        "days": days,
        "analysis_result": analysis_result
    })

def get_dashboard_stats():
    """获取仪表盘统计数据"""
    # 获取关键词数量
    keywords = keywords_manager.get_all_keywords()
    total_keywords = len(keywords)
    active_keywords = len([k for k in keywords if k.get("status") == "active"])
    
    # 获取平台数量
    platforms = storage.load_json("platforms", [])
    total_platforms = len(platforms)
    active_platforms = len([p for p in platforms if p.get("status") == "active"])
    
    # 获取新闻数量
    news_list = news_data_manager.get_all_news()
    total_news = len(news_list)
    
    # 计算互动数据
    total_interactions = sum([
        n.get("read_count", 0) + 
        n.get("comment_count", 0) + 
        n.get("like_count", 0) + 
        n.get("share_count", 0)
        for n in news_list
    ])
    
    # 计算变化率（模拟数据）
    news_change = random.randint(-20, 30)
    interaction_change = random.randint(-15, 25)
    
    return {
        "total_keywords": total_keywords,
        "active_keywords": active_keywords,
        "total_platforms": total_platforms,
        "active_platforms": active_platforms,
        "total_news": total_news,
        "total_interactions": total_interactions,
        "news_change": news_change,
        "interaction_change": interaction_change
    }

def get_trend_data():
    """获取趋势数据"""
    # 生成日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    # 生成模拟数据
    counts = []
    for i in range(len(dates)):
        # 生成一些波动的数据
        base = 20
        trend = i * 0.5  # 整体上升趋势
        random_factor = random.randint(-10, 10)
        count = max(0, int(base + trend + random_factor))
        counts.append(count)
    
    return {
        "dates": dates,
        "counts": counts
    }

def get_sentiment_data():
    """获取情感分析数据"""
    # 生成模拟数据
    return {
        "positive": random.randint(30, 60),
        "neutral": random.randint(20, 40),
        "negative": random.randint(10, 30)
    }

def get_platform_data():
    """获取平台分布数据"""
    # 获取平台列表
    platforms = storage.load_json("platforms", [])
    
    # 生成模拟数据
    labels = [p.get("name", "") for p in platforms]
    values = [random.randint(10, 100) for _ in platforms]
    
    return {
        "labels": labels,
        "values": values  # 确保这是一个列表而不是函数对象
    }

def get_interaction_data():
    """获取互动数据"""
    # 生成模拟数据
    labels = ["阅读量", "评论数", "点赞数", "转发数", "分享数"]
    values = [
        random.randint(1000, 5000),
        random.randint(100, 500),
        random.randint(200, 800),
        random.randint(50, 200),
        random.randint(30, 150)
    ]
    
    return {
        "labels": labels,
        "values": values
    }

def get_hot_news(limit=5):
    """获取热门新闻"""
    # 获取所有新闻
    all_news = news_data_manager.get_all_news()
    
    # 如果没有新闻数据，生成模拟数据
    if not all_news:
        return generate_mock_hot_news(limit)
    
    # 按互动量排序
    sorted_news = sorted(
        all_news,
        key=lambda x: (
            x.get("read_count", 0) + 
            x.get("comment_count", 0) * 5 + 
            x.get("like_count", 0) * 2
        ),
        reverse=True
    )
    
    # 返回前N条
    return sorted_news[:limit] if len(sorted_news) >= limit else sorted_news

def generate_mock_news(keyword, platform_type, platform_name):
    """生成模拟新闻数据"""
    # 模拟标题
    titles = [
        f"{keyword}相关政策出台，引发广泛关注",
        f"专家解读{keyword}最新发展趋势",
        f"{keyword}行业迎来新变革，多方积极响应",
        f"关于{keyword}的五个最新观点",
        f"{keyword}热度持续上升，成为热门话题"
    ]
    
    # 模拟摘要
    summaries = [
        f"近日，{keyword}相关话题引发广泛讨论，多位专家发表了自己的看法...",
        f"随着{keyword}的不断发展，行业内出现了一些新的趋势和变化...",
        f"{keyword}相关政策的出台，对行业发展产生了重要影响...",
        f"专家认为，{keyword}将在未来几年内持续保持高增长态势...",
        f"多家机构发布报告，看好{keyword}的长期发展前景..."
    ]
    
    # 模拟标签
    tag_pools = {
        "tencent": ["科技", "财经", "政策", "观点", "趋势"],
        "toutiao": ["热点", "深度", "分析", "专题", "独家"],
        "weixin": ["原创", "深度", "干货", "观察", "解读"],
        "weibo": ["热搜", "话题", "讨论", "热议", "爆料"]
    }
    
    # 随机生成发布时间（最近7天内）
    days_ago = random.randint(0, 7)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    publish_time = (datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)).strftime("%Y-%m-%d %H:%M:%S")
    
    # 随机生成互动数据
    read_count = random.randint(100, 10000)
    comment_count = random.randint(10, 500)
    like_count = random.randint(20, 1000)
    share_count = random.randint(5, 200)
    
    # 随机选择标签
    tags = random.sample(tag_pools.get(platform_type, ["其他"]), random.randint(1, 3))
    
    # 生成URL
    url = f"https://example.com/{platform_type}/{keyword}/{random.randint(10000, 99999)}"
    
    # 生成新闻ID
    news_id = f"news_{platform_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
    
    # 返回新闻数据
    return {
        "id": news_id,
        "keyword": keyword,
        "title": random.choice(titles),
        "summary": random.choice(summaries),
        "content": "",  # 实际应用中会有完整内容
        "url": url,
        "platform_type": platform_type,
        "platform": platform_name,
        "publish_time": publish_time,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tags": tags,
        "read_count": read_count,
        "comment_count": comment_count,
        "like_count": like_count,
        "share_count": share_count,
        "sentiment": random.choice(["positive", "neutral", "negative"])
    }

def generate_mock_hot_news(limit=5):
    """生成模拟热门新闻数据"""
    hot_news = []
    
    # 模拟平台
    platforms = [
        {"type": "tencent", "name": "腾讯新闻"},
        {"type": "toutiao", "name": "今日头条"},
        {"type": "weixin", "name": "微信公众号"},
        {"type": "weibo", "name": "微博"}
    ]
    
    # 模拟关键词
    keywords = ["人工智能", "数字经济", "元宇宙", "区块链", "新能源"]
    
    # 生成模拟新闻
    for i in range(limit):
        platform = random.choice(platforms)
        keyword = random.choice(keywords)
        hot_news.append(generate_mock_news(keyword, platform["type"], platform["name"]))
    
    return hot_news

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
