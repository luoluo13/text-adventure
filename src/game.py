import os
import sys
from .config_manager import ConfigManager
from .character import Player, Enemy
from .battle import Battle

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
        print("2. 选择难度")
        print("3. 角色状态")
        print("4. 退出游戏")
        print("=" * 50)
        
        choice = self.get_user_choice(1, 4)
        
        if choice == 1:
            self.start_new_game()
        elif choice == 2:
            self.select_difficulty()
        elif choice == 3:
            self.show_character_status()
        elif choice == 4:
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
            print("\n可执行操作:")
            print("1. 移动到黑暗森林")
            print("2. 与村长交谈")
            print("3. 查看角色状态")
            print("4. 查看物品背包")
            print("5. 保存游戏")
            print("6. 返回主菜单")
            
            choice = self.get_user_choice(1, 6)
            
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
                self.save_game()
            elif choice == 6:
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
        print("\n可选回应:")
        print("1. 我会保护村庄的!")
        print("2. 哥布林在哪里?")
        print("3. 我需要更多情报")
        print("4. 结束对话")
        
        choice = self.get_user_choice(1, 4)
        if choice == 1:
            print("\n村长: 很好，年轻人。哥布林就在村庄周围的森林里，去消灭它们吧!")
        elif choice == 2:
            print("\n村长: 它们在村庄北边的森林里，小心点!")
        elif choice == 3:
            print("\n村长: 消灭5只哥布林就能保护村庄了。")
            
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
            for i, item_name in enumerate(self.player.items, 1):
                item = self.config_manager.get_item(item_name)
                print(f"{i}. {item.get('name', item_name)} - {item.get('description', '')}")
        print("=" * 30)
        print("\n按回车键继续...")
        input()
        
    def save_game(self):
        """
        保存游戏
        """
        self.clear_screen()
        print("游戏保存功能尚未实现!")
        print("\n按回车键继续...")
        input()
        
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
                # 显示最终结果
                self.clear_screen()
                print("战斗结束!")
                for log_entry in battle.battle_log:
                    print(f"> {log_entry}")
                    
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