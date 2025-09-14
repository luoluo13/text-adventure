import random
from .character import Player, Enemy

class Battle:
    """
    战斗系统类，处理玩家与敌人之间的战斗逻辑
    """
    def __init__(self, player, enemy, config_manager, difficulty="normal"):
        """
        初始化战斗系统
        
        Args:
            player (Player): 玩家角色
            enemy (Enemy): 敌人角色
            config_manager (ConfigManager): 配置管理器
            difficulty (str): 游戏难度
        """
        self.player = player
        self.enemy = enemy
        self.config_manager = config_manager
        self.difficulty = difficulty
        self.battle_log = []
        self.is_active = True
        self.player_buffs = {}  # 玩家增益效果
        self.enemy_buffs = {}    # 敌人增益效果
        
        # 根据难度调整敌人属性
        self.apply_difficulty_modifiers()
        
    def apply_difficulty_modifiers(self):
        """
        根据难度调整敌人属性
        """
        difficulty_config = self.config_manager.get_difficulty(self.difficulty)
        if difficulty_config:
            multiplier = difficulty_config.get("enemy_strength_multiplier", 1.0)
            self.enemy.hp = int(self.enemy.hp * multiplier)
            self.enemy.max_hp = self.enemy.hp
            self.enemy.atk = int(self.enemy.atk * multiplier)
            self.enemy.defense = int(self.enemy.defense * multiplier)
            
    def start_battle(self):
        """
        开始战斗
        
        Returns:
            dict: 战斗结果
        """
        self.add_to_log(f"{self.enemy.name}向你冲了过来!")
        self.add_to_log("战斗开始!")
        
        while self.is_active and self.player.is_alive() and self.enemy.is_alive():
            # 玩家回合
            if self.is_active and self.player.is_alive() and self.enemy.is_alive():
                self.add_to_log("你的回合")
                break  # 等待玩家操作
                
        return {
            "is_active": self.is_active,
            "player_alive": self.player.is_alive(),
            "enemy_alive": self.enemy.is_alive(),
            "log": self.battle_log
        }
        
    def player_action(self, action, skill_name=None):
        """
        处理玩家行动
        
        Args:
            action (str): 行动类型 (attack, skill, item, defend, escape)
            skill_name (str): 技能名称（如果使用技能）
        """
        if action == "attack":
            self.player_attack()
        elif action == "skill" and skill_name:
            self.player_use_skill(skill_name)
        elif action == "item":
            self.player_use_item()
        elif action == "defend":
            self.player_defend()
        elif action == "escape":
            self.player_escape()
            
        # 检查敌人是否还存活
        if self.enemy.is_alive() and self.is_active:
            # 敌人回合
            self.enemy_action()
        else:
            # 战斗结束
            self.end_battle()
            
    def player_attack(self):
        """
        玩家普通攻击
        """
        # 计算暴击
        is_critical = random.randint(1, 100) <= 10  # 10%暴击率
        
        # 计算伤害
        damage = max(1, self.player.atk - self.enemy.defense // 2)
        damage = random.randint(int(damage * 0.8), int(damage * 1.2))  # 添加随机性
        
        # 暴击伤害翻倍
        if is_critical:
            damage *= 2
            self.add_to_log("暴击!")
            
        # 造成伤害
        actual_damage = self.enemy.take_damage(damage)
        self.add_to_log(f"你对{self.enemy.name}造成了{actual_damage}点伤害!")
        
    def player_use_skill(self, skill_name):
        """
        玩家使用技能
        
        Args:
            skill_name (str): 技能名称
        """
        skill = self.config_manager.get_skill(skill_name)
        if not skill:
            self.add_to_log(f"未知技能: {skill_name}")
            return
            
        # 检查魔法值是否足够
        mp_cost = skill.get("mp_cost", 0)
        if not self.player.use_mp(mp_cost):
            self.add_to_log("魔法值不足!")
            return
            
        skill_type = skill.get("type", "physical")
        power = skill.get("power", 0)
        
        self.add_to_log(f"你使用了{skill.get('name', skill_name)}!")
        
        if skill_type == "physical":
            # 物理技能
            is_critical = random.randint(1, 100) <= 15  # 15%暴击率
            damage = max(1, (self.player.atk + power) - self.enemy.defense // 2)
            damage = random.randint(int(damage * 0.8), int(damage * 1.2))
            
            # 暴击伤害翻倍
            if is_critical:
                damage *= 2
                self.add_to_log("暴击!")
                
            actual_damage = self.enemy.take_damage(damage)
            self.add_to_log(f"对{self.enemy.name}造成了{actual_damage}点伤害!")
            
        elif skill_type == "magical":
            # 魔法技能
            is_critical = random.randint(1, 100) <= 15  # 15%暴击率
            damage = max(1, (self.player.matk + power) - self.enemy.mdef // 2)
            damage = random.randint(int(damage * 0.8), int(damage * 1.2))
            
            # 暴击伤害翻倍
            if is_critical:
                damage *= 2
                self.add_to_log("暴击!")
                
            actual_damage = self.enemy.take_damage(damage)
            self.add_to_log(f"对{self.enemy.name}造成了{actual_damage}点魔法伤害!")
            
        elif skill_type == "support":
            # 辅助技能
            if skill_name == "heal":
                heal_amount = skill.get("power", 0)
                actual_heal = self.player.heal(heal_amount)
                self.add_to_log(f"你恢复了{actual_heal}点生命值!")
                
        elif skill_type == "buff":
            # 增益技能
            self.add_to_log(f"你获得了{skill.get('name', skill_name)}的效果!")
            # 这里可以添加增益效果的实现
            
    def player_use_item(self):
        """
        玩家使用道具
        """
        # 检查玩家是否有道具
        if not self.player.items:
            self.add_to_log("你没有任何道具!")
            return
            
        # 这里应该有一个界面让用户选择道具
        # 简单实现：使用第一个道具
        item_name = self.player.items[0]
        item = self.config_manager.get_item(item_name)
        
        if self.player.use_item(item_name, self.config_manager):
            # 从背包中移除已使用的道具
            if item.get("type") == "consumable":
                self.player.items.remove(item_name)
            self.add_to_log(f"你使用了{item.get('name', item_name)}!")
        else:
            self.add_to_log(f"无法使用{item.get('name', item_name)}!")
            
    def player_defend(self):
        """
        玩家防御
        """
        self.add_to_log("你采取了防御姿态!")
        # 这里可以添加防御效果的实现
        
    def player_escape(self):
        """
        玩家逃跑
        """
        # 逃跑成功率受难度影响
        difficulty_config = self.config_manager.get_difficulty(self.difficulty)
        escape_chance = 70  # 基础逃跑率
        
        if difficulty_config:
            # 简单难度增加逃跑率，困难难度降低逃跑率
            if self.difficulty == "easy":
                escape_chance = 80
            elif self.difficulty == "hard":
                escape_chance = 50
                
        if random.randint(1, 100) <= escape_chance:
            self.add_to_log("你成功逃跑了!")
            self.is_active = False
        else:
            self.add_to_log("逃跑失败!")
            
    def enemy_action(self):
        """
        敌人行动
        """
        # 简单的AI，随机选择技能或普通攻击
        available_skills = self.enemy.skills
        if available_skills and random.randint(1, 100) <= 30:  # 30%概率使用技能
            # 随机选择一个技能
            skill_name = random.choice(available_skills)
            self.enemy_use_skill(skill_name)
        else:
            # 普通攻击
            self.enemy_attack()
            
    def enemy_attack(self):
        """
        敌人普通攻击
        """
        # 计算暴击
        is_critical = random.randint(1, 100) <= 5  # 敌人5%暴击率
        
        # 计算伤害
        damage = max(1, self.enemy.atk - self.player.defense // 2)
        damage = random.randint(int(damage * 0.8), int(damage * 1.2))  # 添加随机性
        
        # 暴击伤害翻倍
        if is_critical:
            damage *= 2
            self.add_to_log(f"{self.enemy.name}的攻击暴击了!")
            
        # 造成伤害
        actual_damage = self.player.take_damage(damage)
        self.add_to_log(f"{self.enemy.name}对你造成了{actual_damage}点伤害!")
        
    def enemy_use_skill(self, skill_name):
        """
        敌人使用技能
        
        Args:
            skill_name (str): 技能名称
        """
        skill = self.config_manager.get_skill(skill_name)
        if not skill:
            # 如果技能不存在，则执行普通攻击
            self.enemy_attack()
            return
            
        skill_type = skill.get("type", "physical")
        power = skill.get("power", 0)
        
        self.add_to_log(f"{self.enemy.name}使用了{skill.get('name', skill_name)}!")
        
        if skill_type == "physical":
            # 物理技能
            is_critical = random.randint(1, 100) <= 10  # 10%暴击率
            damage = max(1, (self.enemy.atk + power) - self.player.defense // 2)
            damage = random.randint(int(damage * 0.8), int(damage * 1.2))
            
            # 暴击伤害翻倍
            if is_critical:
                damage *= 2
                self.add_to_log(f"{self.enemy.name}的技能暴击了!")
                
            actual_damage = self.player.take_damage(damage)
            self.add_to_log(f"对你造成了{actual_damage}点伤害!")
            
        elif skill_type == "magical":
            # 魔法技能
            is_critical = random.randint(1, 100) <= 10  # 10%暴击率
            damage = max(1, (self.enemy.matk + power) - self.player.mdef // 2)
            damage = random.randint(int(damage * 0.8), int(damage * 1.2))
            
            # 暴击伤害翻倍
            if is_critical:
                damage *= 2
                self.add_to_log(f"{self.enemy.name}的技能暴击了!")
                
            actual_damage = self.player.take_damage(damage)
            self.add_to_log(f"对你造成了{actual_damage}点魔法伤害!")
            
        elif skill_type == "support":
            # 辅助技能
            if skill_name == "heal":
                heal_amount = skill.get("power", 0)
                actual_heal = self.enemy.heal(heal_amount)
                self.add_to_log(f"{self.enemy.name}恢复了{actual_heal}点生命值!")
                
    def add_to_log(self, message):
        """
        添加战斗日志
        
        Args:
            message (str): 日志消息
        """
        self.battle_log.append(message)
        print(f"> {message}")  # 同时打印到控制台
        
    def end_battle(self):
        """
        结束战斗
        """
        self.is_active = False
        if not self.player.is_alive():
            self.add_to_log("你被击败了!")
        elif not self.enemy.is_alive():
            self.add_to_log(f"你击败了{self.enemy.name}!")
            # 给予奖励
            self.player.add_exp(self.enemy.exp_reward)
            self.player.add_gold(self.enemy.gold_reward)
            self.add_to_log(f"获得了{self.enemy.exp_reward}点经验值和{self.enemy.gold_reward}枚金币!")
            
            # 添加掉落物品
            for item_name in self.enemy.drop_items:
                self.player.items.append(item_name)
                item = self.config_manager.get_item(item_name)
                self.add_to_log(f"获得了{item.get('name', item_name)}!")