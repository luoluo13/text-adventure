import os
import sys
import json
from .config_manager import ConfigManager
from .character import Player, Enemy
from .battle import Battle
from .quest import Quest

class Game:
    """
    游戏主类，控制游戏流程
    """
    def __init__(self, config_dir="config"):
        """
        初始化游戏
        
        Args:
            config_dir (str): 配置文件目录路径
        """
        self.config_manager = ConfigManager(config_dir)
        self.config_manager.load_all_configs()
        self.player = None
        self.current_chapter = 1
        self.difficulty = "normal"
        self.game_state = "menu"  # menu, playing, battle, game_over
        self.quests = {}  # 存储激活的任务
        self.completed_quests = set()  # 存储已完成的任务ID
        
    def start(self):
        """
        启动游戏
        """
        self.show_menu()
        
    def show_menu(self):
        """
        显示主菜单
        """
        self.clear_screen()
        print("=" * 50)
        print("       自由式文字冒险RPG (text-adventure)")
        print("=" * 50)
        print("1. 开始游戏")
        print("2. 加载游戏")
        print("3. 选择难度")
        print("4. 角色状态")
        print("5. 退出游戏")
        print("=" * 50)
        
        choice = self.get_user_choice(1, 5)
        
        if choice == 1:
            self.start_new_game()
        elif choice == 2:
            if self.load_game():
                # 加载成功后进入游戏
                self.show_world_menu(self.config_manager.get_chapter(self.current_chapter))
        elif choice == 3:
            self.select_difficulty()
        elif choice == 4:
            self.show_character_status()
        elif choice == 5:
            self.quit_game()
            
    def start_new_game(self):
        """
        开始新游戏
        """
        self.clear_screen()
        print("请输入角色名称:")
        name = input("> ")
        
        if not name:
            name = "勇者"
            
        self.select_class(name)
        
    def select_class(self, name):
        """
        选择职业
        
        Args:
            name (str): 角色名称
        """
        self.clear_screen()
        print(f"请选择{name}的职业:")
        
        classes = list(self.config_manager.classes.keys())
        for i, class_key in enumerate(classes, 1):
            class_data = self.config_manager.get_class(class_key)
            print(f"{i}. {class_data.get('name', class_key)} - {class_data.get('description', '')}")
            
        choice = self.get_user_choice(1, len(classes))
        selected_class = classes[choice - 1]
        class_data = self.config_manager.get_class(selected_class)
        
        # 创建玩家角色
        self.player = Player(name, class_data)
        
        # 显示角色初始属性
        self.show_character_creation_result(class_data)
        
        # 初始化任务系统
        self.init_quests()
        
        # 开始游戏
        self.game_state = "playing"
        self.start_story()
        
    def show_character_creation_result(self, class_data):
        """
        显示角色创建结果
        
        Args:
            class_data (dict): 职业数据
        """
        self.clear_screen()
        print("角色创建成功!")
        print(f"名称: {self.player.name}")
        print(f"职业: {class_data.get('name', '')}")
        print(f"生命值: {self.player.hp}")
        print(f"魔法值: {self.player.mp}")
        print(f"攻击力: {self.player.atk}")
        print(f"魔法攻击力: {self.player.matk}")
        print(f"防御力: {self.player.defense}")
        print(f"魔法防御力: {self.player.mdef}")
        print(f"敏捷度: {self.player.agi}")
        print("\n按回车键继续...")
        input()
        
    def select_difficulty(self):
        """
        选择难度
        """
        self.clear_screen()
        print("请选择游戏难度:")
        
        difficulties = list(self.config_manager.difficulty.keys())
        for i, diff_key in enumerate(difficulties, 1):
            diff_data = self.config_manager.get_difficulty(diff_key)
            print(f"{i}. {diff_data.get('name', diff_key)} - {diff_data.get('description', '')}")
            
        choice = self.get_user_choice(1, len(difficulties))
        self.difficulty = difficulties[choice - 1]
        
        print(f"已选择难度: {self.config_manager.get_difficulty(self.difficulty).get('name')}")
        print("\n按回车键返回主菜单...")
        input()
        self.show_menu()
        
    def show_character_status(self):
        """
        显示角色状态
        """
        if not self.player:
            self.clear_screen()
            print("尚未创建角色!")
            print("\n按回车键返回主菜单...")
            input()
            self.show_menu()
            return
            
        self.clear_screen()
        print("角色状态")
        print("=" * 30)
        print(f"名称: {self.player.name}")
        print(f"职业: {self.player.class_name}")
        print(f"等级: {self.player.level}")
        print(f"经验值: {self.player.exp}")
        print(f"生命值: {self.player.hp}/{self.player.max_hp}")
        print(f"魔法值: {self.player.mp}/{self.player.max_mp}")
        print(f"攻击力: {self.player.atk}")
        print(f"魔法攻击力: {self.player.matk}")
        print(f"防御力: {self.player.defense}")
        print(f"魔法防御力: {self.player.mdef}")
        print(f"敏捷度: {self.player.agi}")
        print(f"金币: {self.player.gold}")
        print("=" * 30)
        print("\n按回车键返回主菜单...")
        input()
        self.show_menu()
        
    def init_quests(self):
        """
        初始化任务系统
        """
        self.quests = {}
        self.completed_quests = set()
        
    def accept_quest(self, quest_id):
        """
        接受任务
        
        Args:
            quest_id (str): 任务ID
        """
        # 获取当前章节
        chapter = self.config_manager.get_chapter(self.current_chapter)
        if not chapter:
            return False
            
        # 查找任务数据
        for quest_data in chapter.get("quests", []):
            if quest_data.get("id") == quest_id:
                # 创建任务实例
                quest = Quest(quest_data)
                self.quests[quest_id] = quest
                return True
                
        return False
        
    def update_quest_progress(self, enemy_name):
        """
        更新任务进度
        
        Args:
            enemy_name (str): 被击败的敌人名称
        """
        completed_quests = []
        for quest_id, quest in self.quests.items():
            if not quest.is_completed():
                if quest.update_progress(enemy_name):
                    completed_quests.append(quest_id)
                    
        # 处理已完成的任务
        for quest_id in completed_quests:
            self.complete_quest(quest_id)
            
    def complete_quest(self, quest_id):
        """
        完成任务
        
        Args:
            quest_id (str): 任务ID
        """
        if quest_id not in self.quests:
            return
            
        quest = self.quests[quest_id]
        reward = quest.get_reward()
        
        # 发放奖励
        exp_reward = reward.get("exp", 0)
        gold_reward = reward.get("gold", 0)
        items_reward = reward.get("items", [])
        title_reward = reward.get("title", "")
        
        if exp_reward > 0:
            self.player.add_exp(exp_reward)
            print(f"获得了 {exp_reward} 点经验值!")
            
        if gold_reward > 0:
            self.player.add_gold(gold_reward)
            print(f"获得了 {gold_reward} 枚金币!")
            
        for item_name in items_reward:
            self.player.items.append(item_name)
            item_data = self.config_manager.get_item(item_name)
            item_display_name = item_data.get("name", item_name) if item_data else item_name
            print(f"获得了 {item_display_name}!")
            
        if title_reward:
            print(f"获得了称号: {title_reward}!")
            
        # 标记任务为已完成
        self.completed_quests.add(quest_id)
        print(f"任务 '{quest.name}' 已完成!")
        
    def show_quests(self):
        """
        显示任务列表
        """
        self.clear_screen()
        print("任务列表")
        print("=" * 30)
        
        if not self.quests:
            print("当前没有进行中的任务")
        else:
            print("进行中的任务:")
            for quest_id, quest in self.quests.items():
                if not quest.is_completed():
                    print(f"- {quest.name}")
                    print(f"  {quest.description}")
                    print(f"  进度: {quest.get_progress_text()}")
                    print()
                    
        if self.completed_quests:
            print("已完成的任务:")
            for quest_id in self.completed_quests:
                if quest_id in self.quests:
                    quest = self.quests[quest_id]
                    print(f"- {quest.name}")
            print()
            
        print("=" * 30)
        print("\n按回车键继续...")
        input()
        
    def start_story(self):
        """
        开始游戏剧情
        """
        # 显示开场剧情
        intro = self.config_manager.story.get("intro", {})
        self.clear_screen()
        print(intro.get("title", "开始冒险"))
        print("-" * 30)
        print(intro.get("text", ""))
        print("\n按回车键继续...")
        input()
        
        # 进入第一章
        self.show_chapter(self.current_chapter)
        
    def show_chapter(self, chapter_id):
        """
        显示章节内容
        
        Args:
            chapter_id (int): 章节ID
        """
        chapter = self.config_manager.get_chapter(chapter_id)
        if not chapter:
            print("章节数据错误!")
            return
            
        self.clear_screen()
        print(f"第{chapter_id}章: {chapter.get('title', '')}")
        print("-" * 30)
        print(chapter.get('description', ''))
        print("\n按回车键继续...")
        input()
        
        # 显示可执行操作
        self.show_world_menu(chapter)
        
    def show_world_menu(self, chapter):
        """
        显示游戏世界菜单
        
        Args:
            chapter (dict): 章节数据
        """
        while True:
            self.clear_screen()
            print("当前位置: 村庄")
            print("场景描述: 你站在一个宁静的村庄中央，周围是简朴的木屋和友好的村民。远处可以看到被黑暗笼罩的森林。")
            print(f"\n当前章节: 第{self.current_chapter}章")
            if self.player.stat_points > 0:
                print(f"提示: 你有{self.player.stat_points}个未分配的属性点!")
            print("\n可执行操作:")
            print("1. 移动到黑暗森林")
            print("2. 与村长交谈")
            print("3. 查看角色状态")
            print("4. 查看物品背包")
            print("5. 查看已装备物品")
            print("6. 查看任务列表")
            print("7. 分配属性点")
            print("8. 访问商店")
            print("9. 保存游戏")
            print("10. 返回主菜单")
            
            choice = self.get_user_choice(1, 10)
            
            if choice == 1:
                # 进入战斗示例
                self.start_battle_example()
            elif choice == 2:
                self.talk_to_village_elder(chapter)
            elif choice == 3:
                self.show_character_status_in_game()
            elif choice == 4:
                self.show_inventory()
            elif choice == 5:
                self.show_equipment()
            elif choice == 6:
                self.show_quests()
            elif choice == 7:
                self.allocate_stat_points()
            elif choice == 8:
                self.visit_shop("village_shop")
            elif choice == 9:
                self.save_game()
            elif choice == 10:
                self.show_menu()
                break
                
    def talk_to_village_elder(self, chapter):
        """
        与村长交谈
        
        Args:
            chapter (dict): 章节数据
        """
        npcs = chapter.get("npcs", [])
        village_elder = None
        for npc in npcs:
            if npc.get("id") == "village_elder":
                village_elder = npc
                break
                
        if not village_elder:
            print("未找到村长数据!")
            return
            
        self.clear_screen()
        print("村长:")
        print(village_elder.get("dialogue", ""))
        
        # 显示可接任务
        quests_available = village_elder.get("quests_available", [])
        if quests_available:
            print("\n可接任务:")
            available_quests = []
            for quest_id in quests_available:
                # 检查任务是否已经完成
                if quest_id not in self.completed_quests:
                    # 检查任务是否已经接受
                    if quest_id not in self.quests:
                        available_quests.append(quest_id)
                        
            if available_quests:
                for i, quest_id in enumerate(available_quests, 1):
                    # 获取任务数据
                    quest_data = None
                    for q in chapter.get("quests", []):
                        if q.get("id") == quest_id:
                            quest_data = q
                            break
                            
                    if quest_data:
                        print(f"{i}. {quest_data.get('name', quest_id)}")
                        print(f"   {quest_data.get('description', '')}")
                        
                print(f"{len(available_quests) + 1}. 返回")
                
                quest_choice = self.get_user_choice(1, len(available_quests) + 1)
                if quest_choice <= len(available_quests):
                    selected_quest_id = available_quests[quest_choice - 1]
                    if self.accept_quest(selected_quest_id):
                        quest_name = None
                        for q in chapter.get("quests", []):
                            if q.get("id") == selected_quest_id:
                                quest_name = q.get("name", selected_quest_id)
                                break
                        print(f"\n已接受任务: {quest_name}")
            else:
                print("当前没有可接任务")
        else:
            print("\n当前没有可接任务")
            
        print("\n按回车键继续...")
        input()
        
    def show_character_status_in_game(self):
        """
        在游戏过程中显示角色状态
        """
        self.clear_screen()
        print("角色状态")
        print("=" * 30)
        print(f"名称: {self.player.name}")
        print(f"职业: {self.player.class_name}")
        print(f"等级: {self.player.level}")
        print(f"生命值: {self.player.hp}/{self.player.max_hp}")
        print(f"魔法值: {self.player.mp}/{self.player.max_mp}")
        print(f"金币: {self.player.gold}")
        print("=" * 30)
        print("\n按回车键继续...")
        input()
        
    def show_inventory(self):
        """
        显示物品背包
        """
        self.clear_screen()
        print("物品背包")
        print("=" * 30)
        if not self.player.items:
            print("背包是空的")
        else:
            print("可使用物品:")
            consumables = []
            equipments = []
            
            # 分类物品
            for item_name in self.player.items:
                item = self.config_manager.get_item(item_name)
                if item:
                    if item.get("type") in ["consumable"]:
                        consumables.append(item_name)
                    elif item.get("type") in ["weapon", "armor"]:
                        equipments.append(item_name)
            
            # 显示消耗品
            if consumables:
                print("\n消耗品:")
                for i, item_name in enumerate(consumables, 1):
                    item = self.config_manager.get_item(item_name)
                    print(f"  {i}. {item.get('name', item_name)} - {item.get('description', '')}")
                    
            # 显示装备
            if equipments:
                print("\n装备:")
                for i, item_name in enumerate(equipments, len(consumables) + 1):
                    item = self.config_manager.get_item(item_name)
                    print(f"  {i}. {item.get('name', item_name)} - {item.get('description', '')}")
                    
            print(f"\n{len(consumables) + len(equipments) + 1}. 返回")
            
            # 用户选择
            if consumables or equipments:
                choice = self.get_user_choice(1, len(consumables) + len(equipments) + 1)
                if choice <= len(consumables):
                    # 使用消耗品
                    item_name = consumables[choice - 1]
                    if self.player.use_item(item_name, self.config_manager):
                        self.player.items.remove(item_name)
                        item = self.config_manager.get_item(item_name)
                        print(f"\n你使用了{item.get('name', item_name)}!")
                    else:
                        print("\n无法使用该物品!")
                elif choice <= len(consumables) + len(equipments):
                    # 装备物品
                    item_name = equipments[choice - len(consumables) - 1]
                    item = self.config_manager.get_item(item_name)
                    item_type = item.get("type")
                    
                    # 检查是否已装备同类物品
                    if item_type in self.player.equipped_items:
                        print(f"\n你已经装备了{self.player.equipped_items[item_type]}!")
                        print("是否替换? (y/n)")
                        confirm = input("> ").strip().lower()
                        if confirm != 'y':
                            print("操作已取消")
                            print("\n按回车键继续...")
                            input()
                            return
                    
                    if self.player.equip_item(item_name, self.config_manager):
                        print(f"\n你装备了{item.get('name', item_name)}!")
                    else:
                        print("\n无法装备该物品!")
                else:
                    # 返回
                    return
        
        print("\n按回车键继续...")
        input()
        
    def show_equipment(self):
        """
        显示已装备物品
        """
        self.clear_screen()
        print("已装备物品")
        print("=" * 30)
        
        if not self.player.equipped_items:
            print("未装备任何物品")
        else:
            for item_type, item_name in self.player.equipped_items.items():
                item = self.config_manager.get_item(item_name)
                type_name = "武器" if item_type == "weapon" else "防具"
                print(f"{type_name}: {item.get('name', item_name)}")
                # 显示属性加成
                stat_bonus = item.get("stat_bonus", {})
                if stat_bonus:
                    print("  属性加成:")
                    for stat, bonus in stat_bonus.items():
                        stat_names = {
                            "atk": "攻击力",
                            "matk": "魔法攻击力",
                            "def": "防御力",
                            "mdef": "魔法防御力",
                            "agi": "敏捷度"
                        }
                        print(f"    {stat_names.get(stat, stat)}: +{bonus}")
        
        print("\n按回车键继续...")
        input()
        
    def save_game(self):
        """
        保存游戏
        """
        self.clear_screen()
        print("请输入保存文件名（直接回车使用默认名称）:")
        save_name = input("> ").strip()
        if not save_name:
            save_name = "save"
        
        try:
            # 创建保存目录
            save_dir = "saves"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 准备保存数据
            save_data = {
                "player": self._serialize_player(),
                "current_chapter": self.current_chapter,
                "difficulty": self.difficulty,
                "game_state": self.game_state,
                "quests": self._serialize_quests(),
                "completed_quests": list(self.completed_quests)
            }
            
            # 保存到文件
            save_path = os.path.join(save_dir, f"{save_name}.json")
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"游戏已保存到: {save_path}")
        except Exception as e:
            print(f"保存游戏失败: {e}")
        
        print("\n按回车键继续...")
        input()
    
    def load_game(self):
        """
        加载游戏
        """
        self.clear_screen()
        
        # 检查保存目录
        save_dir = "saves"
        if not os.path.exists(save_dir):
            print("没有找到保存的游戏!")
            print("\n按回车键继续...")
            input()
            return False
        
        # 列出保存的文件
        save_files = [f for f in os.listdir(save_dir) if f.endswith('.json')]
        if not save_files:
            print("没有找到保存的游戏!")
            print("\n按回车键继续...")
            input()
            return False
        
        print("请选择要加载的游戏:")
        for i, save_file in enumerate(save_files, 1):
            print(f"{i}. {save_file.replace('.json', '')}")
        print(f"{len(save_files) + 1}. 返回")
        
        choice = self.get_user_choice(1, len(save_files) + 1)
        if choice > len(save_files):
            return False
        
        save_name = save_files[choice - 1].replace('.json', '')
        
        try:
            # 从文件加载数据
            save_path = os.path.join(save_dir, f"{save_name}.json")
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # 恢复游戏状态
            self._deserialize_player(save_data["player"])
            self.current_chapter = save_data["current_chapter"]
            self.difficulty = save_data["difficulty"]
            self.game_state = save_data["game_state"]
            self._deserialize_quests(save_data["quests"])
            self.completed_quests = set(save_data["completed_quests"])
            
            print(f"游戏 '{save_name}' 加载成功!")
            return True
        except Exception as e:
            print(f"加载游戏失败: {e}")
            print("\n按回车键继续...")
            input()
            return False
    
    def _serialize_player(self):
        """序列化玩家数据"""
        if not self.player:
            return None
            
        return {
            "name": self.player.name,
            "class_name": self.player.class_name,
            "level": self.player.level,
            "exp": self.player.exp,
            "exp_to_next_level": getattr(self.player, 'exp_to_next_level', 100),
            "hp": self.player.hp,
            "max_hp": self.player.max_hp,
            "mp": self.player.mp,
            "max_mp": self.player.max_mp,
            "atk": self.player.atk,
            "matk": self.player.matk,
            "defense": self.player.defense,
            "mdef": self.player.mdef,
            "agi": self.player.agi,
            "gold": self.player.gold,
            "skills": self.player.skills,
            "items": self.player.items,
            "stat_points": getattr(self.player, 'stat_points', 0),
            "equipped_items": getattr(self.player, 'equipped_items', {})
        }
    
    def _deserialize_player(self, player_data):
        """反序列化玩家数据"""
        if not player_data:
            self.player = None
            return
            
        # 获取职业配置
        char_class = self.config_manager.get_class(player_data["class_name"])
        if not char_class:
            # 如果职业不存在，创建一个基础角色
            self.player = Player(player_data["name"], {
                "name": player_data["class_name"],
                "base_stats": {
                    "hp": player_data["max_hp"],
                    "mp": player_data["max_mp"],
                    "atk": player_data["atk"],
                    "matk": player_data["matk"],
                    "def": player_data["defense"],
                    "mdef": player_data["mdef"],
                    "agi": player_data["agi"]
                },
                "skills": player_data["skills"]
            })
        else:
            self.player = Player(player_data["name"], char_class)
            
        # 恢复玩家状态
        self.player.level = player_data["level"]
        self.player.exp = player_data["exp"]
        self.player.exp_to_next_level = player_data.get("exp_to_next_level", 100)
        self.player.hp = player_data["hp"]
        self.player.max_hp = player_data["max_hp"]
        self.player.mp = player_data["mp"]
        self.player.max_mp = player_data["max_mp"]
        self.player.atk = player_data["atk"]
        self.player.matk = player_data["matk"]
        self.player.defense = player_data["defense"]
        self.player.mdef = player_data["mdef"]
        self.player.agi = player_data["agi"]
        self.player.gold = player_data["gold"]
        self.player.skills = player_data["skills"]
        self.player.items = player_data["items"]
        self.player.stat_points = player_data.get("stat_points", 0)
        self.player.equipped_items = player_data.get("equipped_items", {})
    
    def _serialize_quests(self):
        """序列化任务数据"""
        serialized_quests = {}
        for quest_id, quest in self.quests.items():
            serialized_quests[quest_id] = {
                "id": quest.id,
                "name": quest.name,
                "description": quest.description,
                "target_enemy": getattr(quest, 'target_enemy', ''),
                "required_count": getattr(quest, 'required_count', 0),
                "current_count": getattr(quest, 'current_count', 0),
                "reward": getattr(quest, 'reward', {}),
                "completed": getattr(quest, 'completed', False)
            }
        return serialized_quests
    
    def _deserialize_quests(self, quests_data):
        """反序列化任务数据"""
        self.quests = {}
        for quest_id, quest_data in quests_data.items():
            quest = Quest({
                "id": quest_data["id"],
                "name": quest_data["name"],
                "description": quest_data["description"],
                "target": quest_data["target_enemy"],
                "required_count": quest_data["required_count"],
                "reward": quest_data["reward"]
            })
            quest.current_count = quest_data["current_count"]
            quest.completed = quest_data["completed"]
            self.quests[quest_id] = quest
    
    def start_battle_example(self):
        """
        启动战斗示例
        """
        # 创建一个哥布林敌人
        goblin_config = self.config_manager.get_enemy("goblin")
        if not goblin_config:
            print("敌人配置错误!")
            return
            
        enemy = Enemy(goblin_config)
        battle = Battle(self.player, enemy, self.config_manager)
        
        # 开始战斗
        result = battle.start_battle()
        
        # 显示战斗界面
        self.show_battle_ui(battle)
        
    def show_battle_ui(self, battle):
        """
        显示战斗界面
        
        Args:
            battle (Battle): 战斗实例
        """
        while battle.is_active:
            self.clear_screen()
            # 显示角色和敌人状态
            print(f"角色: {battle.player.name} (Lv.{battle.player.level})")
            print(f"职业: {battle.player.class_name}")
            print(f"HP: {battle.player.hp}/{battle.player.max_hp}")
            print(f"MP: {battle.player.mp}/{battle.player.max_mp}")
            print("-" * 30)
            print(f"敌人: {battle.enemy.name}")
            print(f"等级: {battle.enemy.level}")
            print(f"HP: {battle.enemy.hp}/{battle.enemy.max_hp}")
            print("=" * 30)
            
            # 显示战斗日志
            print("战斗日志:")
            for log_entry in battle.battle_log[-5:]:  # 只显示最近5条日志
                print(f"> {log_entry}")
            print("=" * 30)
            
            # 检查角色是否死亡
            if not battle.player.is_alive():
                print("\n你已被击败!")
                print("1. 返回主菜单")
                choice = self.get_user_choice(1, 1)
                if choice == 1:
                    self.show_menu()
                    return
            
            # 显示操作选项
            print("请选择行动:")
            print("1. 攻击")
            print("2. 技能")
            print("3. 道具")
            print("4. 防御")
            print("5. 逃跑")
            
            choice = self.get_user_choice(1, 5)
            
            if choice == 1:
                battle.player_action("attack")
            elif choice == 2:
                self.show_skill_menu(battle)
            elif choice == 3:
                battle.player_action("item")
            elif choice == 4:
                battle.player_action("defend")
            elif choice == 5:
                battle.player_action("escape")
                
            # 检查战斗是否结束
            if not battle.is_active or not battle.player.is_alive() or not battle.enemy.is_alive():
                # 检查是否击败了敌人
                if not battle.enemy.is_alive():
                    # 更新任务进度
                    self.update_quest_progress(battle.enemy.name)
                    
                # 显示最终结果
                self.clear_screen()
                print("战斗结束!")
                for log_entry in battle.battle_log:
                    print(f"> {log_entry}")
                    
                # 检查角色是否死亡
                if not battle.player.is_alive():
                    print("\n你已被击败!游戏结束。")
                    battle.player.is_dead = True
                else:
                    print("\n按回车键继续...")
                    input()
                break
                
    def show_skill_menu(self, battle):
        """
        显示技能菜单
        
        Args:
            battle (Battle): 战斗实例
        """
        self.clear_screen()
        print("请选择技能:")
        skills = battle.player.skills
        for i, skill_name in enumerate(skills, 1):
            skill = self.config_manager.get_skill(skill_name)
            mp_cost = skill.get("mp_cost", 0)
            print(f"{i}. {skill.get('name', skill_name)} (MP: {mp_cost})")
        print(f"{len(skills) + 1}. 返回")
        
        choice = self.get_user_choice(1, len(skills) + 1)
        if choice <= len(skills):
            skill_name = skills[choice - 1]
            battle.player_action("skill", skill_name)
        else:
            # 返回战斗界面
            pass
            
    def visit_shop(self, shop_name):
        """
        访问商店
        
        Args:
            shop_name (str): 商店名称
        """
        shop = self.config_manager.get_shop(shop_name)
        if not shop:
            print("未知商店!")
            print("\n按回车键继续...")
            input()
            return
            
        while True:
            self.clear_screen()
            print(f"欢迎来到{shop.get('name', shop_name)}")
            print(shop.get('description', ''))
            print(f"\n你的金币: {self.player.gold}")
            print("\n商品列表:")
            
            items = shop.get('items', [])
            for i, item_name in enumerate(items, 1):
                item = self.config_manager.get_item(item_name)
                if item:
                    print(f"{i}. {item.get('name', item_name)} - {item.get('price', 0)}金币 - {item.get('description', '')}")
                    
            print(f"{len(items) + 1}. 返回")
            
            choice = self.get_user_choice(1, len(items) + 1)
            if choice > len(items):
                break
                
            item_name = items[choice - 1]
            item = self.config_manager.get_item(item_name)
            price = item.get('price', 0)
            
            print(f"\n你想要购买 {item.get('name', item_name)} 吗? ({price}金币)")
            print("1. 购买")
            print("2. 取消")
            
            purchase_choice = self.get_user_choice(1, 2)
            if purchase_choice == 1:
                if self.player.gold >= price:
                    self.player.remove_gold(price)
                    self.player.items.append(item_name)
                    print(f"你购买了 {item.get('name', item_name)}!")
                else:
                    print("金币不足!")
                    
                print("\n按回车键继续...")
                input()
                
    def allocate_stat_points(self):
        """
        分配属性点
        """
        if self.player.stat_points <= 0:
            print("没有可分配的属性点!")
            print("\n按回车键继续...")
            input()
            return
            
        while self.player.stat_points > 0:
            self.clear_screen()
            print(f"属性点分配 (剩余: {self.player.stat_points}点)")
            print("1. 生命值 (HP) +5/点")
            print("2. 魔法值 (MP) +3/点")
            print("3. 攻击力 (ATK) +1/点")
            print("4. 魔法攻击力 (MATK) +1/点")
            print("5. 防御力 (DEF) +1/点")
            print("6. 魔法防御力 (MDEF) +1/点")
            print("7. 敏捷度 (AGI) +1/点")
            print("8. 完成分配")
            
            choice = self.get_user_choice(1, 8)
            if choice == 8:
                break
                
            stat_map = {
                1: "hp",
                2: "mp",
                3: "atk",
                4: "matk",
                5: "def",
                6: "mdef",
                7: "agi"
            }
            
            if choice in stat_map:
                stat = stat_map[choice]
                max_points = self.player.stat_points
                print(f"\n输入要分配给{stat.upper()}的点数 (1-{max_points}):")
                
                try:
                    points = int(input("> "))
                    if 1 <= points <= max_points:
                        if self.player.allocate_stat_points(stat, points):
                            print(f"成功分配{points}点给{stat.upper()}!")
                        else:
                            print("分配失败!")
                    else:
                        print("无效的点数!")
                except ValueError:
                    print("请输入有效的数字!")
                    
                print("\n按回车键继续...")
                input()
                
        print("属性点分配完成!")
        print("\n按回车键继续...")
        input()
        
    def advance_chapter(self):
        """
        推进章节
        """
        # 检查当前章节的所有任务是否已完成
        chapter = self.config_manager.get_chapter(self.current_chapter)
        if not chapter:
            return
            
        all_quests_completed = True
        chapter_quests = chapter.get("quests", [])
        for quest_data in chapter_quests:
            quest_id = quest_data.get("id")
            if quest_id not in self.completed_quests:
                all_quests_completed = False
                break
                
        if all_quests_completed:
            self.current_chapter += 1
            print(f"恭喜你完成了第{self.current_chapter - 1}章!")
            print("正在进入下一章节...")
            print("\n按回车键继续...")
            input()
            
            # 显示新章节内容
            self.show_chapter(self.current_chapter)
        else:
            print("你还有未完成的任务!")
            print("\n按回车键继续...")
            input()
            
    def get_user_choice(self, min_val, max_val):
        """
        获取用户选择
        
        Args:
            min_val (int): 最小值
            max_val (int): 最大值
            
        Returns:
            int: 用户选择的值
        """
        while True:
            try:
                choice = int(input("> "))
                if min_val <= choice <= max_val:
                    return choice
                else:
                    print(f"请输入 {min_val} 到 {max_val} 之间的数字!")
            except ValueError:
                print("请输入有效的数字!")
                
    def clear_screen(self):
        """
        清屏
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def quit_game(self):
        """
        退出游戏
        """
        self.clear_screen()
        print("感谢游玩自由式文字冒险RPG!")
        sys.exit(0)