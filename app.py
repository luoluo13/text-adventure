from flask import Flask, render_template, request, jsonify, session
import os
import sys
import json

# 将src目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config_manager import ConfigManager
from src.character import Player, Enemy
from src.battle import Battle

app = Flask(__name__)
app.secret_key = 'text_fighter_secret_key'

# 初始化配置管理器
config_manager = ConfigManager("config")
config_manager.load_all_configs()

class GameManager:
    def __init__(self):
        self.player = None
        self.current_chapter = 1
        self.difficulty = "normal"
        self.game_state = "menu"
        self.battle = None

game_manager = GameManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_game', methods=['POST'])
def start_game():
    data = request.get_json()
    name = data.get('name', '勇者')
    
    # 重置游戏状态
    global game_manager
    game_manager = GameManager()
    
    # 设置玩家名称
    session['player_name'] = name
    return jsonify({'status': 'success', 'message': '游戏开始'})

@app.route('/api/select_class', methods=['POST'])
def select_class():
    data = request.get_json()
    class_name = data.get('class_name')
    player_name = session.get('player_name', '勇者')
    
    # 获取职业配置
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
        {'id': 2, 'text': '选择难度'},
        {'id': 3, 'text': '角色状态'},
        {'id': 4, 'text': '退出游戏'}
    ]
    return jsonify({'menu_items': menu_items})

@app.route('/api/get_story_intro', methods=['GET'])
def get_story_intro():
    intro = config_manager.story.get('intro', {})
    return jsonify({
        'title': intro.get('title', '冒险开始'),
        'text': intro.get('text', '')
    })

@app.route('/api/start_battle', methods=['POST'])
def start_battle():
    # 创建一个哥布林敌人作为示例
    goblin_config = config_manager.get_enemy("goblin")
    if not goblin_config:
        return jsonify({'status': 'error', 'message': '敌人配置错误'})
    
    enemy = Enemy(goblin_config)
    game_manager.battle = Battle(game_manager.player, enemy, config_manager)
    
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
    if not game_manager.battle:
        return jsonify({'status': 'error', 'message': '没有进行中的战斗'})
    
    data = request.get_json()
    action = data.get('action')
    skill_name = data.get('skill_name')
    
    # 执行玩家行动
    game_manager.battle.player_action(action, skill_name)
    
    # 检查战斗是否结束
    battle_ended = not game_manager.battle.is_active or \
                   not game_manager.battle.player.is_alive() or \
                   not game_manager.battle.enemy.is_alive()
    
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
        'player_won': game_manager.battle.enemy.hp <= 0 if game_manager.battle else False
    }
    
    return jsonify({
        'status': 'success',
        'battle_state': battle_state
    })

if __name__ == '__main__':
    app.run(debug=True)