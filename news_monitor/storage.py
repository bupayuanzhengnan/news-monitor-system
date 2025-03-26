import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

class FileStorage:
    """
    文件存储类，用于替代MongoDB数据库
    提供基本的数据存储和读取功能
    """
    
    def __init__(self, data_dir: str):
        """
        初始化文件存储
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
    
    def _get_file_path(self, collection: str) -> str:
        """
        获取集合对应的文件路径
        
        Args:
            collection: 集合名称
            
        Returns:
            文件路径
        """
        return os.path.join(self.data_dir, f"{collection}.json")
    
    def save_json(self, collection: str, data: Any) -> bool:
        """
        保存JSON数据到文件
        
        Args:
            collection: 集合名称
            data: 要保存的数据
            
        Returns:
            是否保存成功
        """
        try:
            file_path = self._get_file_path(collection)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"数据已保存到 {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存数据到 {collection} 时发生错误: {str(e)}")
            return False
    
    def load_json(self, collection: str, default: Any = None) -> Any:
        """
        从文件加载JSON数据
        
        Args:
            collection: 集合名称
            default: 默认值，如果文件不存在则返回此值
            
        Returns:
            加载的数据或默认值
        """
        try:
            file_path = self._get_file_path(collection)
            if not os.path.exists(file_path):
                self.logger.info(f"文件 {file_path} 不存在，返回默认值")
                return default
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"从 {file_path} 加载了数据")
            return data
        except Exception as e:
            self.logger.error(f"从 {collection} 加载数据时发生错误: {str(e)}")
            return default
    
    def append_json(self, collection: str, item: Any) -> bool:
        """
        向JSON文件追加数据
        
        Args:
            collection: 集合名称
            item: 要追加的数据项
            
        Returns:
            是否追加成功
        """
        try:
            file_path = self._get_file_path(collection)
            data = self.load_json(collection, [])
            
            if not isinstance(data, list):
                self.logger.error(f"{collection} 中的数据不是列表类型，无法追加")
                return False
            
            data.append(item)
            return self.save_json(collection, data)
        except Exception as e:
            self.logger.error(f"向 {collection} 追加数据时发生错误: {str(e)}")
            return False
    
    def update_json(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """
        更新JSON文件中的数据
        
        Args:
            collection: 集合名称
            query: 查询条件
            update: 更新内容
            
        Returns:
            是否更新成功
        """
        try:
            file_path = self._get_file_path(collection)
            data = self.load_json(collection, [])
            
            if not isinstance(data, list):
                self.logger.error(f"{collection} 中的数据不是列表类型，无法更新")
                return False
            
            updated = False
            for item in data:
                if all(item.get(k) == v for k, v in query.items()):
                    item.update(update)
                    updated = True
            
            if updated:
                return self.save_json(collection, data)
            else:
                self.logger.warning(f"在 {collection} 中未找到匹配的数据进行更新")
                return False
        except Exception as e:
            self.logger.error(f"更新 {collection} 中的数据时发生错误: {str(e)}")
            return False
    
    def delete_json(self, collection: str, query: Dict[str, Any]) -> bool:
        """
        删除JSON文件中的数据
        
        Args:
            collection: 集合名称
            query: 查询条件
            
        Returns:
            是否删除成功
        """
        try:
            file_path = self._get_file_path(collection)
            data = self.load_json(collection, [])
            
            if not isinstance(data, list):
                self.logger.error(f"{collection} 中的数据不是列表类型，无法删除")
                return False
            
            original_length = len(data)
            data = [item for item in data if not all(item.get(k) == v for k, v in query.items())]
            
            if len(data) < original_length:
                return self.save_json(collection, data)
            else:
                self.logger.warning(f"在 {collection} 中未找到匹配的数据进行删除")
                return False
        except Exception as e:
            self.logger.error(f"从 {collection} 中删除数据时发生错误: {str(e)}")
            return False
    
    def find_json(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        查找JSON文件中的数据
        
        Args:
            collection: 集合名称
            query: 查询条件
            
        Returns:
            匹配的数据列表
        """
        try:
            data = self.load_json(collection, [])
            
            if not isinstance(data, list):
                self.logger.error(f"{collection} 中的数据不是列表类型，无法查找")
                return []
            
            result = [item for item in data if all(item.get(k) == v for k, v in query.items())]
            return result
        except Exception as e:
            self.logger.error(f"在 {collection} 中查找数据时发生错误: {str(e)}")
            return []
