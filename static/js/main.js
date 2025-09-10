// 全局变量
let gameState = {
    player: null,
    currentScreen: 'menu',
    battle: null,
    quests: {},  // 存储激活的任务
    completedQuests: []  // 存储已完成的任务
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化主菜单事件
    initMainMenu();
    
    // 加载职业选项
    loadClassOptions();
});

// 初始化主菜单事件
function initMainMenu() {
    const menuItems = document.querySelectorAll('#main-menu li');
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            handleMenuAction(action);
        });
    });
    
    // 确认角色名称按钮
    const confirmNameBtn = document.getElementById('confirm-name');
    if (confirmNameBtn) {
        confirmNameBtn.addEventListener('click', function() {
            const name = document.getElementById('character-name').value || '勇者';
            startGame(name);
        });
    }
    
    // 返回主菜单按钮
    const backToMenuBtn = document.getElementById('back-to-menu');
    if (backToMenuBtn) {
        backToMenuBtn.addEventListener('click', function() {
            showScreen('menu');
        });
    }
    
    // 查看任务列表按钮
    const viewQuestsBtn = document.getElementById('view-quests');
    if (viewQuestsBtn) {
        viewQuestsBtn.addEventListener('click', function() {
            showQuests();
        });
    }
}

// 处理主菜单操作
function handleMenuAction(action) {
    switch(action) {
        case 'start-game':
            showScreen('character-creation');
            break;
        case 'select-difficulty':
            alert('选择难度功能尚未实现');
            break;
        case 'character-status':
            if (gameState.player) {
                showCharacterStatus();
            } else {
                alert('请先创建角色');
            }
            break;
        case 'quit-game':
            if (confirm('确定要退出游戏吗？')) {
                alert('感谢游玩自由式文字冒险RPG!');
                // 这里可以添加实际的退出逻辑
            }
            break;
    }
}

// 显示指定界面
function showScreen(screenName) {
    // 隐藏所有界面
    document.getElementById('menu-screen').style.display = 'none';
    document.getElementById('character-creation-screen').style.display = 'none';
    document.getElementById('world-screen').style.display = 'none';
    document.getElementById('battle-screen').style.display = 'none';
    document.getElementById('skill-screen').style.display = 'none';
    document.getElementById('character-status-screen').style.display = 'none';
    document.getElementById('quests-screen').style.display = 'none';
    
    // 显示指定界面
    switch(screenName) {
        case 'menu':
            document.getElementById('menu-screen').style.display = 'block';
            break;
        case 'character-creation':
            document.getElementById('character-creation-screen').style.display = 'block';
            break;
        case 'world':
            document.getElementById('world-screen').style.display = 'block';
            break;
        case 'battle':
            document.getElementById('battle-screen').style.display = 'block';
            break;
        case 'skill':
            document.getElementById('skill-screen').style.display = 'block';
            break;
        case 'character-status':
            document.getElementById('character-status-screen').style.display = 'block';
            break;
        case 'quests':
            document.getElementById('quests-screen').style.display = 'block';
            break;
    }
    
    gameState.currentScreen = screenName;
}

// 加载职业选项
function loadClassOptions() {
    fetch('/api/get_classes')
        .then(response => response.json())
        .then(data => {
            const classOptions = document.getElementById('class-options');
            classOptions.innerHTML = '';
            
            data.classes.forEach(charClass => {
                const classDiv = document.createElement('div');
                classDiv.className = 'class-option';
                classDiv.setAttribute('data-class', charClass.key);
                
                classDiv.innerHTML = `
                    <h5>> ${charClass.name} (${charClass.key})</h5>
                    <p>${charClass.description}</p>
                    <div class="character-stats">
                        <div>HP: ${charClass.stats.hp}</div>
                        <div>MP: ${charClass.stats.mp}</div>
                        <div>ATK: ${charClass.stats.atk}</div>
                        <div>DEF: ${charClass.stats.def}</div>
                    </div>
                `;
                
                classDiv.addEventListener('click', function() {
                    selectClass(charClass.key);
                });
                
                classOptions.appendChild(classDiv);
            });
        })
        .catch(error => {
            console.error('加载职业选项失败:', error);
        });
}

// 开始游戏
function startGame(name) {
    fetch('/api/start_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({name: name})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // 显示职业选择界面
            showScreen('character-creation');
        } else {
            alert('游戏开始失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('游戏开始失败:', error);
        alert('游戏开始失败');
    });
}

// 选择职业
function selectClass(className) {
    fetch('/api/select_class', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({class_name: className})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            gameState.player = data.player;
            // 显示开场剧情
            showStoryIntro();
        } else {
            alert('职业选择失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('职业选择失败:', error);
        alert('职业选择失败');
    });
}

// 显示开场剧情
function showStoryIntro() {
    fetch('/api/get_story_intro')
        .then(response => response.json())
        .then(data => {
            alert(`${data.title}\n\n${data.text}`);
            // 进入游戏世界
            showScreen('world');
        })
        .catch(error => {
            console.error('加载剧情失败:', error);
            // 直接进入游戏世界
            showScreen('world');
        });
}

// 显示角色状态
function showCharacterStatus() {
    if (!gameState.player) return;
    
    // 更新界面元素
    document.getElementById('status-character-name').textContent = `${gameState.player.name} (Lv. ${gameState.player.level})`;
    document.getElementById('status-character-class').textContent = gameState.player.class_name;
    document.getElementById('status-hp').textContent = gameState.player.hp;
    document.getElementById('status-max-hp').textContent = gameState.player.max_hp;
    document.getElementById('status-mp').textContent = gameState.player.mp;
    document.getElementById('status-max-mp').textContent = gameState.player.max_mp;
    document.getElementById('character-atk').textContent = gameState.player.atk;
    document.getElementById('character-matk').textContent = gameState.player.matk;
    document.getElementById('character-defense').textContent = gameState.player.defense;
    document.getElementById('character-mdef').textContent = gameState.player.mdef;
    document.getElementById('character-agi').textContent = gameState.player.agi;
    
    showScreen('character-status');
}

// 显示任务列表
function showQuests() {
    fetch('/api/get_quests')
        .then(response => response.json())
        .then(data => {
            // 更新任务数据
            gameState.activeQuests = data.active_quests;
            gameState.completedQuests = data.completed_quests;
            
            // 更新界面
            const activeQuestsList = document.getElementById('active-quests-list');
            const completedQuestsList = document.getElementById('completed-quests-list');
            
            // 清空现有内容
            activeQuestsList.innerHTML = '';
            completedQuestsList.innerHTML = '';
            
            // 显示进行中的任务
            if (data.active_quests.length > 0) {
                data.active_quests.forEach(quest => {
                    const questItem = document.createElement('div');
                    questItem.className = 'quest-item';
                    questItem.innerHTML = `
                        <strong>${quest.name}</strong>
                        <p>${quest.description}</p>
                        <p>进度: ${quest.progress}/${quest.required_count}</p>
                    `;
                    activeQuestsList.appendChild(questItem);
                });
            } else {
                activeQuestsList.innerHTML = '<p>当前没有进行中的任务</p>';
            }
            
            // 显示已完成的任务
            if (data.completed_quests.length > 0) {
                data.completed_quests.forEach(quest => {
                    const questItem = document.createElement('div');
                    questItem.className = 'quest-item';
                    questItem.innerHTML = `
                        <strong>${quest.name}</strong>
                        <p>${quest.description}</p>
                        <p style="color: #0f0;">[已完成]</p>
                    `;
                    completedQuestsList.appendChild(questItem);
                });
            } else {
                completedQuestsList.innerHTML = '<p>当前没有已完成的任务</p>';
            }
            
            showScreen('quests');
        })
        .catch(error => {
            console.error('加载任务列表失败:', error);
            alert('加载任务列表失败');
        });
}

// 世界界面操作
document.addEventListener('click', function(e) {
    if (gameState.currentScreen !== 'world') return;
    
    const action = e.target.getAttribute('data-action');
    if (!action) return;
    
    switch(action) {
        case 'enter-forest':
            startBattle();
            break;
        case 'talk-to-elder':
            alert('村长: 年轻人，村庄需要你的帮助！哥布林正在袭击我们的家园，请你保护村民！');
            break;
        case 'view-status':
            showCharacterStatus();
            break;
        case 'view-inventory':
            alert('物品背包功能尚未实现');
            break;
        case 'view-quests':
            showQuests();
            break;
        case 'save-game':
            alert('保存游戏功能尚未实现');
            break;
    }
});

// 开始战斗
function startBattle() {
    fetch('/api/start_battle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            gameState.battle = data.battle_state;
            updateBattleUI();
            showScreen('battle');
        } else {
            alert('开始战斗失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('开始战斗失败:', error);
        alert('开始战斗失败: ' + error.message);
    });
}

// 更新战斗界面
function updateBattleUI() {
    if (!gameState.battle) return;
    
    // 更新玩家信息
    document.getElementById('player-name').textContent = gameState.battle.player.name;
    document.getElementById('player-class').textContent = gameState.battle.player.class_name;
    document.getElementById('player-hp').textContent = gameState.battle.player.hp;
    document.getElementById('player-max-hp').textContent = gameState.battle.player.max_hp;
    document.getElementById('player-mp').textContent = gameState.battle.player.mp;
    document.getElementById('player-max-mp').textContent = gameState.battle.player.max_mp;
    
    // 更新玩家血条
    const playerHpPercent = (gameState.battle.player.hp / gameState.battle.player.max_hp) * 100;
    document.getElementById('player-hp-bar').style.width = playerHpPercent + '%';
    
    // 更新玩家蓝条
    const playerMpPercent = (gameState.battle.player.mp / gameState.battle.player.max_mp) * 100;
    document.getElementById('player-mp-bar').style.width = playerMpPercent + '%';
    
    // 更新敌人信息
    document.getElementById('enemy-name').textContent = gameState.battle.enemy.name;
    document.getElementById('enemy-level').textContent = gameState.battle.enemy.level;
    document.getElementById('enemy-hp').textContent = gameState.battle.enemy.hp;
    document.getElementById('enemy-max-hp').textContent = gameState.battle.enemy.max_hp;
    
    // 更新敌人血条
    const enemyHpPercent = (gameState.battle.enemy.hp / gameState.battle.enemy.max_hp) * 100;
    document.getElementById('enemy-hp-bar').style.width = enemyHpPercent + '%';
    
    // 更新战斗日志
    const battleLog = document.getElementById('battle-log');
    battleLog.innerHTML = '';
    gameState.battle.log.forEach(logEntry => {
        const logLine = document.createElement('div');
        logLine.textContent = '> ' + logEntry;
        battleLog.appendChild(logLine);
    });
    
    // 滚动到底部
    battleLog.scrollTop = battleLog.scrollHeight;
}

// 战斗操作
document.addEventListener('click', function(e) {
    if (gameState.currentScreen !== 'battle') return;
    
    const action = e.target.getAttribute('data-action');
    if (!action) return;
    
    switch(action) {
        case 'attack':
            performBattleAction('attack');
            break;
        case 'skill':
            alert('技能选择功能尚未完全实现');
            break;
        case 'item':
            performBattleAction('item');
            break;
        case 'defend':
            performBattleAction('defend');
            break;
        case 'escape':
            performBattleAction('escape');
            break;
    }
});

// 执行战斗行动
function performBattleAction(action) {
    fetch('/api/battle_action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: action
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            gameState.battle = data.battle_state;
            updateBattleUI();
            
            // 检查战斗是否结束
            if (data.battle_state.battle_ended) {
                if (data.battle_state.player_won) {
                    alert('你赢得了战斗!');
                } else {
                    alert('你被击败了!');
                }
                showScreen('world');
            }
        } else {
            alert('执行行动失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('执行行动失败:', error);
        alert('执行行动失败: ' + error.message);
    });
}