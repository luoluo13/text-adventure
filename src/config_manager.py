import json
import os

class ConfigManager:
    """
    配置管理器，用于加载和管理游戏的所有JSON配置文件
    """
    def __init__(self, config_dir="config"):
        """
        初始化配置管理器
        
        Args:
            config_dir (str): 配置文件目录路径
        """
        self.config_dir = config_dir
        self.classes = {}
        self.story = {}
        self.difficulty = {}
        self.enemies = {}
        self.skills = {}
        self.items = {}
        
    def load_all_configs(self):
        """
        加载所有配置文件
        """
        self.load_classes()
        self.load_story()
        self.load_difficulty()
        self.load_enemies()
        self.load_skills()
        self.load_items()
        
    def load_config_file(self, filename):
        """
        加载单个配置文件
        
        Args:
            filename (str): 配置文件名
            
        Returns:
            dict: 配置数据
        """
        file_path = os.path.join(self.config_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件 {file_path} 未找到")
            return {}
        except json.JSONDecodeError:
            print(f"配置文件 {file_path} 格式错误")
            return {}
    
    def load_classes(self):
        """
        加载职业配置
        """
        self.classes = self.load_config_file("classes.json")
        
    def load_story(self):
        """
        加载剧情配置
        """
        self.story = self.load_config_file("story.json")
        
    def load_difficulty(self):
        """
        加载难度配置
        """
        self.difficulty = self.load_config_file("difficulty.json")
        
    def load_enemies(self):
        """
        加载敌人配置
        """
        self.enemies = self.load_config_file("enemies.json")
        
    def load_skills(self):
        """
        加载技能配置
        """
        self.skills = self.load_config_file("skills.json")
        
    def load_items(self):
        """
        加载物品配置
        """
        self.items = self.load_config_file("items.json")
        
    def get_class(self, class_name):
        """
        获取职业配置
        
        Args:
            class_name (str): 职业名称
            
        Returns:
            dict: 职业配置数据
        """
        return self.classes.get(class_name, {})
        
    def get_enemy(self, enemy_name):
        """
        获取敌人配置
        
        Args:
            enemy_name (str): 敌人名称
            
        Returns:
            dict: 敌人配置数据
        """
        return self.enemies.get(enemy_name, {})
        
    def get_skill(self, skill_name):
        """
        获取技能配置
        
        Args:
            skill_name (str): 技能名称
            
        Returns:
            dict: 技能配置数据
        """
        return self.skills.get(skill_name, {})
        
    def get_item(self, item_name):
        """
        获取物品配置
        
        Args:
            item_name (str): 物品名称
            
        Returns:
            dict: 物品配置数据
        """
        return self.items.get(item_name, {})
        
    def get_difficulty(self, difficulty_name):
        """
        获取难度配置
        
        Args:
            difficulty_name (str): 难度名称
            
        Returns:
            dict: 难度配置数据
        """
        return self.difficulty.get(difficulty_name, {})
        
    def get_chapter(self, chapter_id):
        """
        获取章节配置
        
        Args:
            chapter_id (int): 章节ID
            
        Returns:
            dict: 章节配置数据
        """
        for chapter in self.story.get("chapters", []):
            if chapter.get("id") == chapter_id:
                return chapter
        return {}