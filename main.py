#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文字战斗者 (Text Fighter)
一个基于文本的回合制角色扮演游戏
"""

import os
import sys

# 将src目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.game import Game

def main():
    """
    游戏主函数
    """
    # 创建游戏实例并启动
    game = Game("config")
    game.start()

if __name__ == "__main__":
    main()