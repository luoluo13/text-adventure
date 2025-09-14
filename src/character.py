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
        self.equipped_items = {}  # 装备的物品
        self.is_dead = False  # 死亡状态
        self.stat_points = 0  # 属性点
        self.exp_to_next_level = self.calculate_exp_to_next_level()
        
    def level_up(self):
        """
        角色升级
        """
        self.level += 1
        self.stat_points += 5  # 每次升级获得5个属性点
        
        # 根据职业成长率增加属性
        char_class = None
        # 这里应该通过配置管理器获取职业信息，暂时使用默认值
        # 实际实现中应该从GameManager或Game实例中获取配置管理器
        
        self.exp_to_next_level = self.calculate_exp_to_next_level()
        
    def calculate_exp_to_next_level(self):
        """
        计算升级到下一级所需的经验值
        
        Returns:
            int: 所需经验值
        """
        return 100 * self.level  # 简单计算公式
        
    def add_exp(self, exp):
        """
        增加经验值
        
        Args:
            exp (int): 获得的经验值
        """
        self.exp += exp
        # 检查是否升级
        while self.exp >= self.exp_to_next_level:
            self.level_up()
        
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
        
    def use_item(self, item_name, config_manager):
        """
        使用物品
        
        Args:
            item_name (str): 物品名称
            config_manager (ConfigManager): 配置管理器
            
        Returns:
            bool: 使用成功返回True，否则返回False
        """
        item = config_manager.get_item(item_name)
        if not item:
            return False
            
        item_type = item.get("type")
        if item_type == "consumable":
            effect = item.get("effect")
            value = item.get("value", 0)
            
            if effect == "restore_hp":
                healed = self.heal(value)
                return True
            elif effect == "restore_mp":
                restored = self.restore_mp(value)
                return True
            elif effect == "permanent_bonus":
                # 永久属性加成
                stat_bonus = item.get("stat_bonus", {})
                for stat, bonus in stat_bonus.items():
                    if hasattr(self, stat):
                        setattr(self, stat, getattr(self, stat) + bonus)
                return True
                
        return False
        
    def equip_item(self, item_name, config_manager):
        """
        装备物品
        
        Args:
            item_name (str): 物品名称
            config_manager (ConfigManager): 配置管理器
            
        Returns:
            bool: 装备成功返回True，否则返回False
        """
        item = config_manager.get_item(item_name)
        if not item:
            return False
            
        item_type = item.get("type")
        if item_type not in ["weapon", "armor"]:
            return False
            
        # 卸下当前同类装备
        if item_type in self.equipped_items:
            self.unequip_item(item_type, config_manager)
            
        # 装备新物品
        self.equipped_items[item_type] = item_name
        
        # 应用属性加成
        stat_bonus = item.get("stat_bonus", {})
        for stat, bonus in stat_bonus.items():
            if hasattr(self, stat):
                setattr(self, stat, getattr(self, stat) + bonus)
                
        return True
        
    def unequip_item(self, item_type, config_manager):
        """
        卸下物品
        
        Args:
            item_type (str): 物品类型
            config_manager (ConfigManager): 配置管理器
            
        Returns:
            bool: 卸下成功返回True，否则返回False
        """
        if item_type not in self.equipped_items:
            return False
            
        item_name = self.equipped_items[item_type]
        item = config_manager.get_item(item_name)
        if not item:
            return False
            
        # 移除属性加成
        stat_bonus = item.get("stat_bonus", {})
        for stat, bonus in stat_bonus.items():
            if hasattr(self, stat):
                setattr(self, stat, getattr(self, stat) - bonus)
                
        # 移除装备记录
        del self.equipped_items[item_type]
        return True
        
    def is_alive(self):
        """
        检查角色是否存活
        
        Returns:
            bool: 如果角色存活返回True，否则返回False
        """
        alive = self.hp > 0
        if not alive and not self.is_dead:
            self.is_dead = True
        return alive
        
    def allocate_stat_points(self, stat, points):
        """
        分配属性点
        
        Args:
            stat (str): 属性名称
            points (int): 分配的点数
            
        Returns:
            bool: 分配成功返回True，否则返回False
        """
        if points > self.stat_points:
            return False
            
        if stat in ["hp", "mp", "atk", "matk", "def", "mdef", "agi"]:
            # 增加属性值
            if stat == "hp":
                self.max_hp += points * 5
                self.hp += points * 5
            elif stat == "mp":
                self.max_mp += points * 3
                self.mp += points * 3
            else:
                setattr(self, stat, getattr(self, stat) + points)
                
            self.stat_points -= points
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