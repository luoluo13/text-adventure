#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, session
import os
import sys
import json

# 将src目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config_manager import ConfigManager
from src.character import Player, Enemy
from src.battle import Battle
from src.quest import Quest

app = Flask(__name__)
app.secret_key = 'text_adventure_secret_key'

# 移除全局配置管理器初始化，避免在应用启动时尝试从错误路径加载配置文件

class GameManager:
    def __init__(self, config_path="config"):
        self.player = None
        self.current_chapter = 1
        self.difficulty = "normal"
        self.game_state = "menu"
        self.battle = None
        self.quests = {}  # 存储激活的任务
        self.completed_quests = set()  # 存储已完成的任务ID
        self.config_path = config_path  # 配置文件路径
        self.sync_mode = "manual"  # 同步模式：auto 或 manual
        
    def save_game(self, save_name="save"):
        """
        保存游戏状态到文件
        
        Args:
            save_name (str): 保存文件名
            
        Returns:
            bool: 保存是否成功
        """
        try:
            import json
            import os
            
            # 创建保存目录，基于游戏名称，与config同级
            game_id = session.get('game_id', 'default')
            save_dir = os.path.join("story-list", game_id, "saves", save_name)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 准备保存数据
            save_data = {
                "player": self._serialize_player(),
                "current_chapter": self.current_chapter,
                "difficulty": self.difficulty,
                "game_state": self.game_state,
                "quests": self._serialize_quests(),
                "completed_quests": list(self.completed_quests),
                "sync_mode": self.sync_mode
            }
            
            # 保存到文件
            save_path = os.path.join(save_dir, "save.json")
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存游戏失败: {e}")
            return False

    def load_game(self, save_name="save"):
        """
        从文件加载游戏状态
        
        Args:
            save_name (str): 保存文件名
            
        Returns:
            bool: 加载是否成功
        """
        try:
            import json
            import os
            
            # 检查保存文件是否存在
            game_id = session.get('game_id', 'default')
            save_path = os.path.join("story-list", game_id, "saves", save_name, "save.json")
            if not os.path.exists(save_path):
                return False
            
            # 从文件加载数据
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # 恢复游戏状态
            self._deserialize_player(save_data["player"])
            self.current_chapter = save_data["current_chapter"]
            self.difficulty = save_data["difficulty"]
            self.game_state = save_data["game_state"]
            self._deserialize_quests(save_data["quests"])
            self.completed_quests = set(save_data["completed_quests"])
            self.sync_mode = save_data.get("sync_mode", "manual")
            
            return True
        except Exception as e:
            print(f"加载游戏失败: {e}")
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
        config_manager = get_config_manager()  # 使用会话特定的配置管理器
        char_class = config_manager.get_class(player_data["class_name"])
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

# 为每个会话创建独立的游戏管理器
game_managers = {}

# 创建一个全局的配置管理器字典，为每个故事ID维护一个配置管理器
config_managers = {}

def get_game_manager():
    """获取当前会话的游戏管理器"""
    session_id = session.get('id', 'default')
    if session_id not in game_managers:
        config_path = session.get('config_path', 'config')
        game_managers[session_id] = GameManager(config_path)
    return game_managers[session_id]

def get_config_manager():
    """获取当前会话的配置管理器"""
    game_id = session.get('game_id', 'default')
    if game_id not in config_managers:
        config_path = session.get('config_path', os.path.join('story-list', game_id, 'config'))
        config_managers[game_id] = ConfigManager(config_path)
        config_managers[game_id].load_all_configs()
    return config_managers[game_id]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_story_list', methods=['GET'])
def get_story_list():
    """获取游戏列表"""
    try:
        with open('story-list.json', 'r', encoding='utf-8') as f:
            story_list = json.load(f)
        return jsonify({'status': 'success', 'story_list': story_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取游戏列表失败: {e}'})

@app.route('/api/select_story', methods=['POST'])
def select_story():
    """选择游戏"""
    data = request.get_json()
    game_id = data.get('game_id')
    
    try:
        with open('story-list.json', 'r', encoding='utf-8') as f:
            story_list = json.load(f)
            
        selected_game = None
        for game in story_list:
            if game.get('id') == game_id:
                selected_game = game
                break
                
        if not selected_game:
            return jsonify({'status': 'error', 'message': '游戏不存在'})
            
        # 设置会话信息
        session['game_id'] = game_id
        session['game_name'] = selected_game.get('name', game_id)
        
        # 构造实际的配置路径: story-list/[id]/[path]
        config_path = os.path.join('story-list', game_id, selected_game.get('path', 'config'))
        session['config_path'] = config_path
        
        # 注意：我们不再在这里创建全局config_manager，而是在需要时通过get_config_manager()获取
        # config_manager = ConfigManager(config_path)
        # config_manager.load_all_configs()
        
        return jsonify({
            'status': 'success', 
            'message': f'已选择游戏: {selected_game.get("name")}',
            'game': selected_game
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'选择游戏失败: {e}'})

@app.route('/api/get_save_list', methods=['POST'])
def get_save_list():
    """获取存档列表"""
    game_id = session.get('game_id', 'default')
    save_dir = os.path.join("story-list", game_id, "saves")
    
    try:
        if not os.path.exists(save_dir):
            return jsonify({'status': 'success', 'saves': []})
            
        # 获取所有子目录（存档）
        saves = []
        for item in os.listdir(save_dir):
            item_path = os.path.join(save_dir, item)
            if os.path.isdir(item_path):
                # 获取存档中save.json文件的修改时间
                save_file_path = os.path.join(item_path, 'save.json')
                if os.path.exists(save_file_path):
                    mtime = os.path.getmtime(save_file_path)
                else:
                    # 如果save.json不存在，则使用文件夹的修改时间
                    mtime = os.path.getmtime(item_path)
                saves.append({
                    'name': item,
                    'modified_time': mtime
                })
                
        # 按修改时间排序
        saves.sort(key=lambda x: x['modified_time'], reverse=True)
        return jsonify({'status': 'success', 'saves': saves})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取存档列表失败: {e}'})

@app.route('/api/start_game', methods=['POST'])
def start_game():
    data = request.get_json()
    name = data.get('name', '勇者')
    save_name = data.get('save_name', 'save')
    sync_mode = data.get('sync_mode', 'manual')
    
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    
    # 设置同步模式
    game_manager.sync_mode = sync_mode
    
    # 重置游戏状态
    game_manager.player = None
    game_manager.current_chapter = 1
    game_manager.game_state = "playing"
    
    # 设置玩家名称
    session['player_name'] = name
    session['save_name'] = save_name
    return jsonify({'status': 'success', 'message': '游戏开始', 'sync_mode': sync_mode})

@app.route('/api/select_class', methods=['POST'])
def select_class():
    data = request.get_json()
    class_name = data.get('class_name')
    player_name = session.get('player_name', '勇者')
    
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    
    # 获取职业配置
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    char_class = config_manager.get_class(class_name)
    if not char_class:
        return jsonify({'status': 'error', 'message': '无效的职业选择'})
    
    # 创建玩家角色
    game_manager.player = Player(player_name, char_class)
    game_manager.game_state = "playing"
    
    # 返回角色信息
    player_info = {
        'name': game_manager.player.name,
        'class_name': game_manager.player.class_name,
        'hp': game_manager.player.hp,
        'max_hp': game_manager.player.max_hp,
        'mp': game_manager.player.mp,
        'max_mp': game_manager.player.max_mp,
        'atk': game_manager.player.atk,
        'matk': game_manager.player.matk,
        'defense': game_manager.player.defense,
        'mdef': game_manager.player.mdef,
        'agi': game_manager.player.agi
    }
    
    return jsonify({
        'status': 'success', 
        'player': player_info,
        'message': f'{player_name}选择了{char_class["name"]}职业'
    })

@app.route('/api/get_classes', methods=['GET'])
def get_classes():
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    classes = []
    for class_key, class_data in config_manager.classes.items():
        classes.append({
            'key': class_key,
            'name': class_data['name'],
            'description': class_data['description'],
            'stats': class_data['base_stats']
        })
    return jsonify({'classes': classes})

@app.route('/api/get_menu', methods=['GET'])
def get_menu():
    menu_items = [
        {'id': 1, 'text': '开始游戏'},
        {'id': 2, 'text': '加载游戏'},
        {'id': 3, 'text': '选择难度'},
        {'id': 4, 'text': '角色状态'},
        {'id': 5, 'text': '退出游戏'}
    ]
    return jsonify({'menu_items': menu_items})

@app.route('/api/get_story_intro', methods=['GET'])
def get_story_intro():
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    intro = config_manager.story.get('intro', {})
    return jsonify({
        'title': intro.get('title', '冒险开始'),
        'text': intro.get('text', '')
    })

@app.route('/api/start_battle', methods=['POST'])
def start_battle():
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    
    # 检查玩家是否存在
    if not game_manager.player:
        return jsonify({'status': 'error', 'message': '请先创建角色'})
    
    # 创建一个哥布林敌人作为示例
    goblin_config = config_manager.get_enemy("goblin")
    if not goblin_config:
        return jsonify({'status': 'error', 'message': '敌人配置错误'})
    
    enemy = Enemy(goblin_config)
    # 传递难度参数
    game_manager.battle = Battle(game_manager.player, enemy, config_manager, game_manager.difficulty)
    
    # 初始化战斗
    result = game_manager.battle.start_battle()
    
    # 返回战斗状态
    battle_state = {
        'player': {
            'name': game_manager.player.name,
            'class_name': game_manager.player.class_name,
            'level': game_manager.player.level,
            'hp': game_manager.player.hp,
            'max_hp': game_manager.player.max_hp,
            'mp': game_manager.player.mp,
            'max_mp': game_manager.player.max_mp
        },
        'enemy': {
            'name': game_manager.battle.enemy.name,
            'level': game_manager.battle.enemy.level,
            'hp': game_manager.battle.enemy.hp,
            'max_hp': game_manager.battle.enemy.max_hp
        },
        'log': game_manager.battle.battle_log,
        'is_active': game_manager.battle.is_active
    }
    
    return jsonify({
        'status': 'success',
        'battle_state': battle_state
    })

@app.route('/api/battle_action', methods=['POST'])
def battle_action():
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    
    if not game_manager.battle:
        return jsonify({'status': 'error', 'message': '没有进行中的战斗'})
    
    if not game_manager.player:
        return jsonify({'status': 'error', 'message': '请先创建角色'})
    
    data = request.get_json()
    action = data.get('action')
    skill_name = data.get('skill_name')
    
    # 执行玩家行动
    game_manager.battle.player_action(action, skill_name)
    
    # 检查战斗是否结束
    battle_ended = not game_manager.battle.is_active or \
                   not game_manager.battle.player.is_alive() or \
                   not game_manager.battle.enemy.is_alive()
    
    # 如果敌人被击败，更新任务进度
    enemy_name = None
    if not game_manager.battle.enemy.is_alive():
        enemy_name = game_manager.battle.enemy.name
        update_quest_progress(enemy_name)
    
    # 返回战斗状态
    battle_state = {
        'player': {
            'name': game_manager.player.name,
            'class_name': game_manager.player.class_name,
            'level': game_manager.player.level,
            'hp': game_manager.player.hp,
            'max_hp': game_manager.player.max_hp,
            'mp': game_manager.player.mp,
            'max_mp': game_manager.player.max_mp
        },
        'enemy': {
            'name': game_manager.battle.enemy.name,
            'level': game_manager.battle.enemy.level,
            'hp': game_manager.battle.enemy.hp,
            'max_hp': game_manager.battle.enemy.max_hp
        },
        'log': game_manager.battle.battle_log,
        'is_active': game_manager.battle.is_active,
        'battle_ended': battle_ended,
        'player_won': game_manager.battle.enemy.hp <= 0 if game_manager.battle else False,
        'player_dead': not game_manager.player.is_alive()
    }
    
    return jsonify({
        'status': 'success',
        'battle_state': battle_state
    })

def update_quest_progress(enemy_name):
    """
    更新任务进度
    
    Args:
        enemy_name (str): 被击败的敌人名称
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    
    completed_quests = []
    for quest_id, quest in game_manager.quests.items():
        if not quest.is_completed():
            if quest.update_progress(enemy_name):
                completed_quests.append(quest_id)
                
    # 处理已完成的任务
    for quest_id in completed_quests:
        complete_quest(quest_id)

def complete_quest(quest_id):
    """
    完成任务
    
    Args:
        quest_id (str): 任务ID
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    
    if quest_id not in game_manager.quests:
        return
        
    quest = game_manager.quests[quest_id]
    reward = quest.get_reward()
    
    # 发放奖励
    exp_reward = reward.get("exp", 0)
    gold_reward = reward.get("gold", 0)
    items_reward = reward.get("items", [])
    
    if exp_reward > 0:
        game_manager.player.add_exp(exp_reward)
        
    if gold_reward > 0:
        game_manager.player.add_gold(gold_reward)
        
    for item_name in items_reward:
        game_manager.player.items.append(item_name)
        
    # 标记任务为已完成
    game_manager.completed_quests.add(quest_id)

@app.route('/api/accept_quest', methods=['POST'])
def accept_quest():
    """
    接受任务
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    
    data = request.get_json()
    quest_id = data.get('quest_id')
    
    # 获取当前章节
    chapter = config_manager.get_chapter(game_manager.current_chapter)
    if not chapter:
        return jsonify({'status': 'error', 'message': '章节数据错误'})
        
    # 查找任务数据
    for quest_data in chapter.get("quests", []):
        if quest_data.get("id") == quest_id:
            # 创建任务实例
            quest = Quest(quest_data)
            game_manager.quests[quest_id] = quest
            return jsonify({'status': 'success', 'message': f'已接受任务: {quest.name}'})
            
    return jsonify({'status': 'error', 'message': '任务未找到'})

@app.route('/api/get_quests', methods=['GET'])
def get_quests():
    """
    获取任务列表
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    
    active_quests = []
    completed_quests = []
    
    # 添加进行中的任务
    for quest_id, quest in game_manager.quests.items():
        if not quest.is_completed():
            active_quests.append({
                'id': quest.id,
                'name': quest.name,
                'description': quest.description,
                'progress': quest.get_progress_text(),
                'required_count': quest.required_count
            })
    
    # 添加已完成的任务
    for quest_id in game_manager.completed_quests:
        if quest_id in game_manager.quests:
            quest = game_manager.quests[quest_id]
            completed_quests.append({
                'id': quest.id,
                'name': quest.name,
                'description': quest.description
            })
    
    return jsonify({
        'active_quests': active_quests,
        'completed_quests': completed_quests
    })

@app.route('/api/save_game', methods=['POST'])
def save_game():
    """
    保存游戏
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    
    if not game_manager.player:
        return jsonify({'status': 'error', 'message': '请先创建角色'})
    
    data = request.get_json()
    save_name = data.get('save_name', session.get('save_name', 'save'))
    
    if game_manager.save_game(save_name):
        return jsonify({'status': 'success', 'message': '游戏保存成功'})
    else:
        return jsonify({'status': 'error', 'message': '游戏保存失败'})

@app.route('/api/load_game', methods=['POST'])
def load_game():
    """
    加载游戏
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    
    data = request.get_json()
    save_name = data.get('save_name', 'save')
    
    if game_manager.load_game(save_name):
        # 返回加载后的游戏状态
        player_info = None
        if game_manager.player:
            player_info = {
                'name': game_manager.player.name,
                'class_name': game_manager.player.class_name,
                'level': game_manager.player.level,
                'hp': game_manager.player.hp,
                'max_hp': game_manager.player.max_hp,
                'mp': game_manager.player.mp,
                'max_mp': game_manager.player.max_mp,
                'gold': game_manager.player.gold
            }
        
        return jsonify({
            'status': 'success', 
            'message': '游戏加载成功',
            'player': player_info,
            'current_chapter': game_manager.current_chapter,
            'difficulty': game_manager.difficulty,
            'game_state': game_manager.game_state,
            'sync_mode': game_manager.sync_mode
        })
    else:
        return jsonify({'status': 'error', 'message': '游戏加载失败'})

@app.route('/api/load_game_list', methods=['GET'])
def load_game_list():
    """
    获取可加载的游戏列表
    """
    try:
        import os
        import glob
        from datetime import datetime
        
        save_dir = "saves"
        if not os.path.exists(save_dir):
            return jsonify({'status': 'success', 'saves': []})
        
        # 查找所有保存文件
        save_files = glob.glob(os.path.join(save_dir, "*.json"))
        saves = []
        for save_file in save_files:
            save_name = os.path.basename(save_file).replace(".json", "")
            # 获取文件修改时间
            mtime = os.path.getmtime(save_file)
            modified_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            saves.append({
                'name': save_name,
                'modified_time': modified_time
            })
        
        # 按修改时间排序
        saves.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return jsonify({'status': 'success', 'saves': saves})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取保存列表失败: {e}'})

@app.route('/api/use_item', methods=['POST'])
def use_item():
    """
    使用物品
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    
    if not game_manager.player:
        return jsonify({'status': 'error', 'message': '请先创建角色'})
    
    data = request.get_json()
    item_name = data.get('item_name')
    
    if not item_name:
        return jsonify({'status': 'error', 'message': '未指定物品'})
    
    if item_name not in game_manager.player.items:
        return jsonify({'status': 'error', 'message': '你没有这个物品'})
    
    # 使用物品
    if game_manager.player.use_item(item_name, config_manager):
        # 从背包中移除消耗品
        item = config_manager.get_item(item_name)
        if item.get("type") == "consumable":
            if item_name in game_manager.player.items:
                game_manager.player.items.remove(item_name)
        return jsonify({'status': 'success', 'message': f'你使用了{item.get("name", item_name)}!'})
    else:
        return jsonify({'status': 'error', 'message': '无法使用该物品'})

@app.route('/api/equip_item', methods=['POST'])
def equip_item():
    """
    装备物品
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    
    if not game_manager.player:
        return jsonify({'status': 'error', 'message': '请先创建角色'})
    
    data = request.get_json()
    item_name = data.get('item_name')
    
    if not item_name:
        return jsonify({'status': 'error', 'message': '未指定物品'})
    
    if item_name not in game_manager.player.items:
        return jsonify({'status': 'error', 'message': '你没有这个物品'})
    
    # 装备物品
    item = config_manager.get_item(item_name)
    item_type = item.get("type")
    
    if item_type not in ["weapon", "armor"]:
        return jsonify({'status': 'error', 'message': '该物品无法装备'})
    
    # 检查是否已装备同类物品
    old_item = None
    if item_type in game_manager.player.equipped_items:
        old_item = game_manager.player.equipped_items[item_type]
    
    if game_manager.player.equip_item(item_name, config_manager):
        # 从背包中移除已装备的物品
        if item_name in game_manager.player.items:
            game_manager.player.items.remove(item_name)
            
        result = {
            'status': 'success', 
            'message': f'你装备了{item.get("name", item_name)}!',
            'equipped_items': game_manager.player.equipped_items
        }
        
        # 如果替换了旧装备，将其放回背包
        if old_item:
            game_manager.player.items.append(old_item)
            old_item_data = config_manager.get_item(old_item)
            result['message'] += f' {old_item_data.get("name", old_item)}已放回背包。'
            
        return jsonify(result)
    else:
        return jsonify({'status': 'error', 'message': '无法装备该物品'})

@app.route('/api/get_inventory', methods=['GET'])
def get_inventory():
    """
    获取玩家背包信息
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    
    if not game_manager.player:
        return jsonify({'status': 'error', 'message': '请先创建角色'})
    
    inventory = []
    for item_name in game_manager.player.items:
        item = config_manager.get_item(item_name)
        if item:
            inventory.append({
                'name': item_name,
                'display_name': item.get('name', item_name),
                'type': item.get('type', ''),
                'description': item.get('description', ''),
                'stat_bonus': item.get('stat_bonus', {})
            })
    
    equipped_items = {}
    for item_type, item_name in game_manager.player.equipped_items.items():
        item = config_manager.get_item(item_name)
        if item:
            equipped_items[item_type] = {
                'name': item_name,
                'display_name': item.get('name', item_name),
                'type': item.get('type', ''),
                'description': item.get('description', ''),
                'stat_bonus': item.get('stat_bonus', {})
            }
    
    return jsonify({
        'status': 'success',
        'inventory': inventory,
        'equipped_items': equipped_items
    })

@app.route('/api/check_player_status', methods=['GET'])
def check_player_status():
    """
    检查玩家状态
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    
    if not game_manager.player:
        return jsonify({'status': 'error', 'message': '请先创建角色'})
    
    return jsonify({
        'status': 'success',
        'player': {
            'name': game_manager.player.name,
            'class_name': game_manager.player.class_name,
            'level': game_manager.player.level,
            'hp': game_manager.player.hp,
            'max_hp': game_manager.player.max_hp,
            'mp': game_manager.player.mp,
            'max_mp': game_manager.player.max_mp,
            'gold': game_manager.player.gold,
            'is_dead': game_manager.player.is_dead
        },
        'is_dead': game_manager.player.is_dead
    })

@app.route('/api/get_shop', methods=['POST'])
def get_shop():
    """
    获取商店信息
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    
    if not game_manager.player:
        return jsonify({'status': 'error', 'message': '请先创建角色'})
    
    data = request.get_json()
    shop_name = data.get('shop_name', 'village_shop')
    
    shop = config_manager.get_shop(shop_name)
    if not shop:
        return jsonify({'status': 'error', 'message': '商店不存在'})
    
    # 获取商品信息
    items = []
    for item_name in shop.get('items', []):
        item = config_manager.get_item(item_name)
        if item:
            items.append({
                'name': item_name,
                'display_name': item.get('name', item_name),
                'price': item.get('price', 0),
                'description': item.get('description', ''),
                'type': item.get('type', '')
            })
    
    return jsonify({
        'status': 'success',
        'shop': {
            'name': shop.get('name', shop_name),
            'description': shop.get('description', ''),
            'items': items
        },
        'player_gold': game_manager.player.gold
    })

@app.route('/api/buy_item', methods=['POST'])
def buy_item():
    """
    购买物品
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    
    if not game_manager.player:
        return jsonify({'status': 'error', 'message': '请先创建角色'})
    
    data = request.get_json()
    shop_name = data.get('shop_name', 'village_shop')
    item_name = data.get('item_name')
    
    if not item_name:
        return jsonify({'status': 'error', 'message': '未指定物品'})
    
    # 检查商店是否有该物品
    shop = config_manager.get_shop(shop_name)
    if not shop or item_name not in shop.get('items', []):
        return jsonify({'status': 'error', 'message': '商店没有该物品'})
    
    # 获取物品信息
    item = config_manager.get_item(item_name)
    if not item:
        return jsonify({'status': 'error', 'message': '物品不存在'})
    
    price = item.get('price', 0)
    
    # 检查金币是否足够
    if game_manager.player.gold < price:
        return jsonify({'status': 'error', 'message': '金币不足'})
    
    # 扣除金币并添加物品
    game_manager.player.remove_gold(price)
    game_manager.player.items.append(item_name)
    
    return jsonify({
        'status': 'success',
        'message': f'你购买了{item.get("name", item_name)}!',
        'player_gold': game_manager.player.gold
    })

@app.route('/api/allocate_stat_points', methods=['POST'])
def allocate_stat_points():
    """
    分配属性点
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    
    if not game_manager.player:
        return jsonify({'status': 'error', 'message': '请先创建角色'})
    
    data = request.get_json()
    stat = data.get('stat')
    points = data.get('points', 0)
    
    if not stat or points <= 0:
        return jsonify({'status': 'error', 'message': '无效的属性或点数'})
    
    if points > game_manager.player.stat_points:
        return jsonify({'status': 'error', 'message': '属性点不足'})
    
    if game_manager.player.allocate_stat_points(stat, points):
        return jsonify({
            'status': 'success',
            'message': f'成功分配{points}点给{stat.upper()}!',
            'stat_points_remaining': game_manager.player.stat_points,
            'player_stats': game_manager.player.get_stats()
        })
    else:
        return jsonify({'status': 'error', 'message': '分配失败'})

@app.route('/api/get_player_stats', methods=['GET'])
def get_player_stats():
    """
    获取玩家完整状态信息
    """
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    
    if not game_manager.player:
        return jsonify({'status': 'error', 'message': '请先创建角色'})
    
    stats = game_manager.player.get_stats()
    stats['gold'] = game_manager.player.gold
    stats['stat_points'] = game_manager.player.stat_points
    stats['exp_to_next_level'] = game_manager.player.exp_to_next_level
    stats['equipped_items'] = game_manager.player.equipped_items
    
    return jsonify({
        'status': 'success',
        'player_stats': stats
    })

@app.route('/api/get_current_scene', methods=['GET'])
def get_current_scene():
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    
    # 获取配置管理器
    config_manager = game_manager.config_manager
    
    # 获取当前章节
    current_chapter_id = game_manager.current_chapter
    chapter = config_manager.get_chapter(current_chapter_id)
    
    if not chapter:
        return jsonify({
            'location': '未知地点',
            'description': '你在一个未知的地方。',
            'actions': [
                {'id': 'view-status', 'text': '查看角色状态'},
                {'id': 'view-quests', 'text': '查看任务列表'},
                {'id': 'save-game', 'text': '保存游戏'}
            ]
        })
    
    # 构造场景信息
    scene_info = {
        'location': chapter.get('title', f'第{current_chapter_id}章'),
        'description': chapter.get('description', '你在一个神秘的地方。'),
        'actions': [
            {'id': 'view-status', 'text': '查看角色状态'},
            {'id': 'view-quests', 'text': '查看任务列表'},
            {'id': 'save-game', 'text': '保存游戏'}
        ]
    }
    
    # 添加特定章节的操作
    if current_chapter_id == 1:
        scene_info['actions'].insert(0, {'id': 'enter-forest', 'text': '移动到黑暗森林'})
        scene_info['actions'].insert(1, {'id': 'talk-to-elder', 'text': '与村长交谈'})
    
    return jsonify(scene_info)

@app.route('/api/talk_to_npc', methods=['POST'])
def talk_to_npc():
    data = request.get_json()
    npc_id = data.get('npc_id')
    
    # 获取当前会话的游戏管理器
    game_manager = get_game_manager()
    
    # 获取配置管理器
    config_manager = get_config_manager()  # 使用会话特定的配置管理器
    
    # 获取当前章节
    current_chapter_id = game_manager.current_chapter
    chapter = config_manager.get_chapter(current_chapter_id)
    
    if not chapter:
        return jsonify({'status': 'error', 'message': '无法获取章节信息'})
    
    # 查找NPC
    npcs = chapter.get('npcs', [])
    target_npc = None
    for npc in npcs:
        if npc.get('id') == npc_id:
            target_npc = npc
            break
    
    if not target_npc:
        return jsonify({'status': 'error', 'message': '无法找到该NPC'})
    
    # 返回NPC信息
    return jsonify({
        'status': 'success',
        'npc_name': target_npc.get('name', '未知NPC'),
        'dialogue': target_npc.get('dialogue', '...'),
        'quests': target_npc.get('quests_available', [])
    })

if __name__ == '__main__':
    app.run(debug=True)