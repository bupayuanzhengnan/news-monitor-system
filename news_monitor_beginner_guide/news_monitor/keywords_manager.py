import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

class KeywordsManager:
    """
    关键词管理类，提供关键词的增删改查功能
    """
    
    def __init__(self, storage):
        """
        初始化关键词管理器
        
        Args:
            storage: 文件存储对象
        """
        self.storage = storage
        self.keywords_file = "keywords"
        self.logger = logging.getLogger(__name__)
    
    def add_keyword(self, keyword: str, category: str = "默认分类") -> bool:
        """
        添加关键词
        
        Args:
            keyword: 关键词
            category: 分类
            
        Returns:
            是否成功添加
        """
        try:
            # 获取现有关键词
            keywords = self.get_all_keywords()
            
            # 检查是否已存在
            if any(k.get("keyword") == keyword for k in keywords):
                self.logger.warning(f"关键词 '{keyword}' 已存在")
                return False
            
            # 创建新关键词
            new_keyword = {
                "keyword": keyword,
                "category": category,
                "status": "active",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 添加到列表
            keywords.append(new_keyword)
            
            # 保存到文件
            result = self.storage.save_json(keywords, self.keywords_file)
            
            if result:
                self.logger.info(f"成功添加关键词 '{keyword}'")
            else:
                self.logger.error(f"保存关键词 '{keyword}' 失败")
                
            return result
        except Exception as e:
            self.logger.error(f"添加关键词 '{keyword}' 时发生错误: {str(e)}")
            return False
    
    def delete_keyword(self, keyword: str) -> bool:
        """
        删除关键词
        
        Args:
            keyword: 关键词
            
        Returns:
            是否成功删除
        """
        try:
            # 获取现有关键词
            keywords = self.get_all_keywords()
            
            # 检查是否存在
            if not any(k.get("keyword") == keyword for k in keywords):
                self.logger.warning(f"关键词 '{keyword}' 不存在")
                return False
            
            # 过滤掉要删除的关键词
            keywords = [k for k in keywords if k.get("keyword") != keyword]
            
            # 保存到文件
            result = self.storage.save_json(keywords, self.keywords_file)
            
            if result:
                self.logger.info(f"成功删除关键词 '{keyword}'")
            else:
                self.logger.error(f"删除关键词 '{keyword}' 失败")
                
            return result
        except Exception as e:
            self.logger.error(f"删除关键词 '{keyword}' 时发生错误: {str(e)}")
            return False
    
    def update_keyword_status(self, keyword: str, status: str) -> bool:
        """
        更新关键词状态
        
        Args:
            keyword: 关键词
            status: 状态
            
        Returns:
            是否成功更新
        """
        try:
            # 获取现有关键词
            keywords = self.get_all_keywords()
            
            # 更新状态
            updated = False
            for k in keywords:
                if k.get("keyword") == keyword:
                    k["status"] = status
                    k["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    updated = True
                    break
            
            if not updated:
                self.logger.warning(f"关键词 '{keyword}' 不存在")
                return False
            
            # 保存到文件
            result = self.storage.save_json(keywords, self.keywords_file)
            
            if result:
                self.logger.info(f"成功更新关键词 '{keyword}' 的状态为 '{status}'")
            else:
                self.logger.error(f"更新关键词 '{keyword}' 的状态失败")
                
            return result
        except Exception as e:
            self.logger.error(f"更新关键词 '{keyword}' 的状态时发生错误: {str(e)}")
            return False
    
    def get_all_keywords(self) -> List[Dict[str, Any]]:
        """
        获取所有关键词
        
        Returns:
            关键词列表
        """
        try:
            return self.storage.load_json(self.keywords_file, [])
        except Exception as e:
            self.logger.error(f"获取所有关键词时发生错误: {str(e)}")
            return []
    
    def get_keyword_by_name(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        根据名称获取关键词
        
        Args:
            keyword: 关键词
            
        Returns:
            关键词信息或None
        """
        try:
            keywords = self.get_all_keywords()
            for k in keywords:
                if k.get("keyword") == keyword:
                    return k
            return None
        except Exception as e:
            self.logger.error(f"根据名称获取关键词时发生错误: {str(e)}")
            return None
    
    def get_keywords_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        根据分类获取关键词
        
        Args:
            category: 分类
            
        Returns:
            关键词列表
        """
        try:
            keywords = self.get_all_keywords()
            return [k for k in keywords if k.get("category") == category]
        except Exception as e:
            self.logger.error(f"根据分类获取关键词时发生错误: {str(e)}")
            return []
    
    def get_active_keywords(self) -> List[Dict[str, Any]]:
        """
        获取活跃关键词
        
        Returns:
            活跃关键词列表
        """
        try:
            keywords = self.get_all_keywords()
            return [k for k in keywords if k.get("status") == "active"]
        except Exception as e:
            self.logger.error(f"获取活跃关键词时发生错误: {str(e)}")
            return []
