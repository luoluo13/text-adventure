class Character:
    """
    角色基类，包含玩家和敌人的共同属性和方法
    """
    def __init__(self, name, char_class=None, config=None):
        """
        初始化角色
        
        Args:
            name (str): 角色名称
            char_class (dict): 角色职业配置
            config (dict): 角色配置数据
        """
        self.name = name
        self.level = 1
        self.exp = 0
        
        # 如果提供了职业配置，则使用职业配置初始化角色
        if char_class:
            self.init_from_class(char_class)
        # 如果提供了配置数据，则使用配置数据初始化角色
        elif config:
            self.init_from_config(config)
        # 否则使用默认值
        else:
            self.hp = 100
            self.max_hp = 100
            self.mp = 50
            self.max_mp = 50
            self.atk = 10
            self.matk = 10
            self.defense = 5
            self.mdef = 5
            self.agi = 5
            self.skills = []
            self.items = []
            
    def init_from_class(self, char_class):
        """
        根据职业配置初始化角色
        
        Args:
            char_class (dict): 职业配置
        """
        base_stats = char_class.get("base_stats", {})
        self.hp = base_stats.get("hp", 100)
        self.max_hp = self.hp
        self.mp = base_stats.get("mp", 50)
        self.max_mp = self.mp
        self.atk = base_stats.get("atk", 10)
        self.matk = base_stats.get("matk", 10)
        self.defense = base_stats.get("def", 5)
        self.mdef = base_stats.get("mdef", 5)
        self.agi = base_stats.get("agi", 5)
        self.skills = char_class.get("skills", [])
        self.items = char_class.get("starting_items", [])
        
    def init_from_config(self, config):
        """
        根据配置数据初始化角色
        
        Args:
            config (dict): 角色配置数据
        """
        self.hp = config.get("hp", 100)
        self.max_hp = self.hp
        self.mp = config.get("mp", 50)
        self.max_mp = self.mp
        self.atk = config.get("atk", 10)
        self.matk = config.get("matk", 10)
        self.defense = config.get("def", 5)
        self.mdef = config.get("mdef", 5)
        self.agi = config.get("agi", 5)
        self.exp_reward = config.get("exp_reward", 0)
        self.gold_reward = config.get("gold_reward", 0)
        self.skills = config.get("skills", [])
        self.drop_items = config.get("drop_items", [])
        
    def is_alive(self):
        """
        检查角色是否存活
        
        Returns:
            bool: 如果角色存活返回True，否则返回False
        """
        return self.hp > 0
        
    def take_damage(self, damage):
        """
        角色受到伤害
        
        Args:
            damage (int): 伤害值
            
        Returns:
            int: 实际受到的伤害值
        """
        actual_damage = max(1, damage)  # 至少受到1点伤害
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
        
    def heal(self, amount):
        """
        恢复角色生命值
        
        Args:
            amount (int): 恢复量
            
        Returns:
            int: 实际恢复的生命值
        """
        actual_heal = min(amount, self.max_hp - self.hp)
        self.hp = min(self.max_hp, self.hp + actual_heal)
        return actual_heal
        
    def restore_mp(self, amount):
        """
        恢复角色魔法值
        
        Args:
            amount (int): 恢复量
            
        Returns:
            int: 实际恢复的魔法值
        """
        actual_restore = min(amount, self.max_mp - self.mp)
        self.mp = min(self.max_mp, self.mp + actual_restore)
        return actual_restore
        
    def use_mp(self, amount):
        """
        消耗魔法值
        
        Args:
            amount (int): 消耗量
            
        Returns:
            bool: 如果魔法值足够返回True，否则返回False
        """
        if self.mp >= amount:
            self.mp -= amount
            return True
        return False
        
    def add_exp(self, exp):
        """
        增加经验值
        
        Args:
            exp (int): 获得的经验值
        """
        self.exp += exp
        
    def get_stats(self):
        """
        获取角色状态信息
        
        Returns:
            dict: 角色状态信息
        """
        return {
            "name": self.name,
            "level": self.level,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mp": self.mp,
            "max_mp": self.max_mp,
            "atk": self.atk,
            "matk": self.matk,
            "defense": self.defense,
            "mdef": self.mdef,
            "agi": self.agi
        }


class Player(Character):
    """
    玩家角色类
    """
    def __init__(self, name, char_class):
        """
        初始化玩家角色
        
        Args:
            name (str): 玩家名称
            char_class (dict): 玩家职业配置
        """
        super().__init__(name, char_class=char_class)
        self.gold = 0
        self.class_name = char_class.get("name", "")
        
    def level_up(self):
        """
        角色升级
        """
        self.level += 1
        # 这里可以添加升级时的属性增长逻辑
        
    def add_gold(self, amount):
        """
        增加金币
        
        Args:
            amount (int): 金币数量
        """
        self.gold += amount
        
    def remove_gold(self, amount):
        """
        减少金币
        
        Args:
            amount (int): 金币数量
            
        Returns:
            bool: 如果金币足够返回True，否则返回False
        """
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False


class Enemy(Character):
    """
    敌人角色类
    """
    def __init__(self, config):
        """
        初始化敌人角色
        
        Args:
            config (dict): 敌人配置数据
        """
        super().__init__(config.get("name", "未知敌人"), config=config)