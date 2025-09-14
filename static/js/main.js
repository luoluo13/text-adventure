// 全局变量
let gameState = {
    player: null,
    currentScreen: 'game-selection', // 默认显示游戏选择界面
    battle: null,
    quests: {},  // 存储激活的任务
    completedQuests: [],  // 存储已完成的任务
    currentGame: null,  // 当前选择的游戏
    saves: [],  // 存档列表
    syncMode: 'manual',  // 同步模式：manual 或 auto
    autoSaveInterval: null  // 自动保存定时器
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化游戏选择界面
    initGameSelection();
    
    // 初始化游戏主界面事件
    initGameMainEvents();
    
    // 初始化新游戏界面事件
    initNewGameEvents();
    
    // 初始化存档选择界面事件
    initSaveSelectionEvents();
    
    // 初始化主菜单事件
    initMainMenu();
    
    // 加载职业选项
    loadClassOptions();
});

// 在页面即将卸载时保存游戏
window.addEventListener('beforeunload', function(e) {
    // 如果是自动同步模式且有玩家数据，执行保存
    if (gameState.syncMode === 'auto' && gameState.player) {
        saveGame();
    }
});

// 初始化游戏选择界面
function initGameSelection() {
    loadGameList();
}

// 加载游戏列表
function loadGameList() {
    fetch('/api/get_story_list')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const gameList = document.getElementById('game-list');
                gameList.innerHTML = '';
                
                data.story_list.forEach(game => {
                    const gameDiv = document.createElement('div');
                    gameDiv.className = 'game-option';
                    gameDiv.setAttribute('data-game-id', game.id);
                    
                    gameDiv.innerHTML = `
                        <h5>> ${game.name}</h5>
                        <p>${game.description}</p>
                    `;
                    
                    gameDiv.addEventListener('click', function() {
                        selectGame(game.id);
                    });
                    
                    gameList.appendChild(gameDiv);
                });
            } else {
                console.error('加载游戏列表失败:', data.message);
            }
        })
        .catch(error => {
            console.error('加载游戏列表失败:', error);
        });
}

// 选择游戏
function selectGame(gameId) {
    fetch('/api/select_story', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({game_id: gameId})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            gameState.currentGame = data.game;
            document.getElementById('game-title').textContent = data.game.name;
            showScreen('game-main');
        } else {
            alert('选择游戏失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('选择游戏失败:', error);
        alert('选择游戏失败');
    });
}

// 初始化游戏主界面事件
function initGameMainEvents() {
    // 为游戏主界面的菜单项添加事件监听器
    document.querySelectorAll('#game-main-screen .menu li').forEach(item => {
        item.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            handleGameMainAction(action);
        });
    });
}

// 处理游戏主界面操作
function handleGameMainAction(action) {
    switch(action) {
        case 'start-new-game':
            showScreen('new-game');
            break;
        case 'load-game':
            loadSaveList();
            showScreen('save-selection');
            break;
        case 'game-settings':
            alert('敬请期待');
            break;
        case 'back-to-games':
            showScreen('game-selection');
            break;
    }
}

// 初始化新游戏界面事件
function initNewGameEvents() {
    // 确认新游戏按钮
    const confirmNewGameBtn = document.getElementById('confirm-new-game');
    if (confirmNewGameBtn) {
        confirmNewGameBtn.addEventListener('click', function() {
            const saveName = document.getElementById('save-name').value || 'save1';
            const syncMode = document.getElementById('sync-mode').value || 'manual';
            const characterName = document.getElementById('character-name').value || '勇者';
            
            startNewGame(saveName, syncMode, characterName);
        });
    }
    
    // 返回按钮
    const backToGameMainBtn = document.getElementById('back-to-game-main');
    if (backToGameMainBtn) {
        backToGameMainBtn.addEventListener('click', function() {
            showScreen('game-main');
        });
    }
}

// 开始新游戏
function startNewGame(saveName, syncMode, characterName) {
    fetch('/api/start_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: characterName,
            save_name: saveName,
            sync_mode: syncMode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // 存储同步模式和存档名称
            gameState.syncMode = syncMode;
            gameState.saveName = saveName;
            
            // 如果是自动同步模式，启动自动保存定时器
            if (syncMode === 'auto') {
                startAutoSave();
            }
            
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

// 初始化存档选择界面事件
function initSaveSelectionEvents() {
    // 返回按钮
    const backBtn = document.getElementById('back-to-game-main-from-saves');
    if (backBtn) {
        backBtn.addEventListener('click', function() {
            showScreen('game-main');
        });
    }
}

// 加载存档列表
function loadSaveList() {
    fetch('/api/get_save_list', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            gameState.saves = data.saves;
            updateSaveListUI();
        } else {
            console.error('加载存档列表失败:', data.message);
        }
    })
    .catch(error => {
        console.error('加载存档列表失败:', error);
    });
}

// 更新存档列表界面
function updateSaveListUI() {
    const saveList = document.getElementById('save-list');
    const noSavesMessage = document.getElementById('no-saves-message');
    
    if (gameState.saves.length > 0) {
        saveList.style.display = 'block';
        noSavesMessage.style.display = 'none';
        
        saveList.innerHTML = '';
        gameState.saves.forEach(save => {
            const saveDiv = document.createElement('div');
            saveDiv.className = 'save-option';
            saveDiv.setAttribute('data-save-name', save.name);
            
            // 将时间戳转换为可读格式
            const date = new Date(save.modified_time * 1000);
            const dateString = date.toLocaleString('zh-CN');
            
            saveDiv.innerHTML = `
                <h5>> ${save.name}</h5>
                <p>最后修改: ${dateString}</p>
            `;
            
            saveDiv.addEventListener('click', function() {
                loadSave(save.name);
            });
            
            saveList.appendChild(saveDiv);
        });
    } else {
        saveList.style.display = 'none';
        noSavesMessage.style.display = 'block';
    }
}

// 加载存档
function loadSave(saveName) {
    fetch('/api/load_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({save_name: saveName})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            if (data.player) {
                gameState.player = data.player;
            }
            
            // 存储同步模式和存档名称
            gameState.syncMode = data.sync_mode || 'manual';
            gameState.saveName = saveName;
            
            // 如果是自动同步模式，启动自动保存定时器
            if (gameState.syncMode === 'auto') {
                startAutoSave();
            }
            
            // 进入游戏世界
            showScreen('world');
        } else {
            alert('加载存档失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('加载存档失败:', error);
        alert('加载存档失败');
    });
}

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
            const name = document.getElementById('character-name-create').value || '勇者';
            startGame(name);
        });
    }
    
    // 返回游戏主界面按钮（从角色状态界面）
    const backToGameMainFromStatusBtn = document.getElementById('back-to-game-main-from-status');
    if (backToGameMainFromStatusBtn) {
        backToGameMainFromStatusBtn.addEventListener('click', function() {
            showScreen('game-main');
        });
    }
    
    
    // 返回游戏世界按钮（从任务界面）
    const backToWorldFromQuestsBtn = document.getElementById('back-to-world');
    if (backToWorldFromQuestsBtn) {
        backToWorldFromQuestsBtn.addEventListener('click', function() {
            showScreen('world');
        });
    }
    
    // 返回上一页按钮（从任务界面）
    const backToPreviousFromQuestsBtn = document.getElementById('back-to-previous-from-quests');
    if (backToPreviousFromQuestsBtn) {
        backToPreviousFromQuestsBtn.addEventListener('click', function() {
            showScreen('world');
        });
    }
    
    // 查看任务列表按钮
    const viewQuestsBtn = document.getElementById('view-quests');
    if (viewQuestsBtn) {
        viewQuestsBtn.addEventListener('click', function() {
            showQuests();
        });
    }
    
    // 初始化世界场景操作
    initWorldActions();
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
    document.getElementById('game-selection-screen').style.display = 'none';
    document.getElementById('game-main-screen').style.display = 'none';
    document.getElementById('new-game-screen').style.display = 'none';
    document.getElementById('save-selection-screen').style.display = 'none';
    document.getElementById('menu-screen').style.display = 'none';
    document.getElementById('character-creation-screen').style.display = 'none';
    document.getElementById('world-screen').style.display = 'none';
    document.getElementById('battle-screen').style.display = 'none';
    document.getElementById('skill-screen').style.display = 'none';
    document.getElementById('character-status-screen').style.display = 'none';
    document.getElementById('quests-screen').style.display = 'none';
    
    // 显示指定界面
    switch(screenName) {
        case 'game-selection':
            document.getElementById('game-selection-screen').style.display = 'block';
            break;
        case 'game-main':
            document.getElementById('game-main-screen').style.display = 'block';
            break;
        case 'new-game':
            document.getElementById('new-game-screen').style.display = 'block';
            break;
        case 'save-selection':
            document.getElementById('save-selection-screen').style.display = 'block';
            break;
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

// 添加接受任务的函数
function acceptQuest(questId) {
    fetch('/api/accept_quest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            quest_id: questId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(data.message);
            // 接受任务后自动保存（如果是自动同步模式）
            if (gameState.syncMode === 'auto') {
                saveGame();
            }
        } else {
            alert('接受任务失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('接受任务失败:', error);
        alert('接受任务失败');
    });
}

// 显示游戏世界界面
function showWorld() {
    // 从后端获取当前场景信息
    fetch('/api/get_current_scene')
        .then(response => response.json())
        .then(data => {
            // 更新场景信息
            if (data.location) {
                document.getElementById('current-location').textContent = data.location;
            }
            if (data.description) {
                document.getElementById('scene-description').textContent = data.description;
            }
            
            // 更新可执行操作
            const actionsList = document.getElementById('world-actions');
            if (data.actions && data.actions.length > 0) {
                actionsList.innerHTML = '';
                data.actions.forEach(action => {
                    const li = document.createElement('li');
                    li.setAttribute('data-action', action.id);
                    li.textContent = `> ${action.text}`;
                    actionsList.appendChild(li);
                });
                
                // 重新绑定事件监听器
                initWorldActions();
            }
            
            showScreen('world');
        })
        .catch(error => {
            console.error('获取场景信息失败:', error);
            // 如果获取失败，仍然显示默认界面
            showScreen('world');
        });
}

// 初始化世界场景操作事件
function initWorldActions() {
    const worldActions = document.querySelectorAll('#world-actions li');
    worldActions.forEach(action => {
        action.addEventListener('click', function() {
            const actionType = this.getAttribute('data-action');
            handleWorldAction(actionType);
        });
    });
}

// 处理世界场景操作
function handleWorldAction(action) {
    switch(action) {
        case 'enter-forest':
            // 进入森林，可能触发战斗
            startBattle('goblin'); // 示例敌人
            break;
        case 'talk-to-elder':
            // 与村长交谈
            talkToNpc('village_elder');
            break;
        case 'view-status':
            // 查看角色状态
            showCharacterStatus();
            break;
        case 'view-inventory':
            // 查看物品背包
            alert('查看物品背包功能尚未实现');
            break;
        case 'view-quests':
            // 查看任务列表
            showQuests();
            break;
        case 'save-game':
            // 保存游戏
            saveGame();
            break;
        default:
            alert('未知操作');
    }
}

// 与NPC交谈
function talkToNpc(npcId) {
    fetch('/api/talk_to_npc', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ npc_id: npcId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(`${data.npc_name}:\n${data.dialogue}`);
            // 如果有任务，可以在这里处理
            if (data.quests && data.quests.length > 0) {
                // 显示可接任务
                console.log('可接任务:', data.quests);
            }
        } else {
            alert('与NPC交谈失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('与NPC交谈失败:', error);
        alert('与NPC交谈失败: ' + error.message);
    });
}

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
                    // 战斗胜利后自动保存（如果是自动同步模式）
                    if (gameState.syncMode === 'auto') {
                        saveGame();
                    }
                } else if (data.battle_state.player_dead) {
                    // 玩家被击败
                    alert('你被击败了!');
                } else {
                    // 其他情况（如逃跑成功）
                    alert('逃跑成功！');
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

// 启动自动保存
function startAutoSave() {
    // 清除现有的自动保存定时器（如果有的话）
    stopAutoSave();
    
    // 设置自动保存定时器（每5分钟保存一次）
    gameState.autoSaveInterval = setInterval(function() {
        // 只有在有玩家数据时才执行自动保存
        if (gameState.player) {
            saveGame();
        }
    }, 300000); // 300000毫秒 = 5分钟
}

// 停止自动保存
function stopAutoSave() {
    if (gameState.autoSaveInterval) {
        clearInterval(gameState.autoSaveInterval);
        gameState.autoSaveInterval = null;
    }
}

// 手动保存游戏
function saveGame() {
    // 获取当前存档名称
    const saveName = document.getElementById('save-name')?.value || gameState.saveName || 'save1';
    
    fetch('/api/save_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            save_name: saveName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('游戏保存成功！');
            console.log('游戏保存成功');
        } else {
            alert('游戏保存失败: ' + data.message);
            console.error('游戏保存失败:', data.message);
        }
    })
    .catch(error => {
        alert('游戏保存失败: ' + error.message);
        console.error('游戏保存失败:', error);
    });
}
