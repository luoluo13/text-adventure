# 自由式文字冒险RPG (text-adventure)

一款基于纯文本交互的回合制角色扮演游戏(RPG)，所有游戏内容通过JSON配置文件进行配置和读取。

## 产品特色

- 完全基于文本交互，无任何图像、音频媒体文件
- 所有游戏信息通过JSON配置文件读取，支持自定义难度和模式
- 丰富的剧情系统和多职业选择
- 经典回合制战斗系统
- 基于Web的用户界面，提供更好的交互体验

## 安装和运行

1. 确保已安装Python 3.6或更高版本
2. 安装所需依赖：
   ```bash
   pip install flask
   ```
3. 克隆或下载本项目
4. 在项目根目录下运行以下命令启动游戏：
   ```bash
   python app.py
   ```
5. 在浏览器中访问 `http://localhost:5000` 开始游戏

## 游戏操作

- 使用鼠标点击界面元素进行游戏操作
- 按照屏幕提示进行游戏操作

## 自定义游戏内容

游戏的所有内容都通过JSON配置文件定义，您可以修改以下文件来自定义游戏：

- `config/classes.json` - 职业配置
- `config/story.json` - 剧情配置
- `config/difficulty.json` - 难度配置
- `config/enemies.json` - 敌人配置
- `config/skills.json` - 技能配置
- `config/items.json` - 物品配置

## 许可证

The MIT License (MIT)

Copyright (c) 2025 Text Adventure Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.