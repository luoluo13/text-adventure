class Quest:
    """
    任务类，用于管理单个任务的状态和进度
    """
    def __init__(self, quest_data):
        """
        初始化任务
        
        Args:
            quest_data (dict): 从story.json加载的任务数据
        """
        self.id = quest_data.get("id")
        self.name = quest_data.get("name")
        self.description = quest_data.get("description")
        self.objective = quest_data.get("objective", {})
        self.reward = quest_data.get("reward", {})
        self.completed = False
        self.progress = 0
        self.required_count = self.objective.get("count", 1)
        
    def update_progress(self, enemy_name=None, count=1):
        """
        更新任务进度
        
        Args:
            enemy_name (str): 被击败的敌人名称
            count (int): 击败数量
            
        Returns:
            bool: 如果任务完成返回True，否则返回False
        """
        # 检查是否是击败敌人类型的任务
        if self.objective.get("type") == "defeat_enemies":
            target_enemy = self.objective.get("enemy")
            # 如果是目标敌人，则更新进度
            if enemy_name == target_enemy:
                self.progress += count
                # 检查任务是否完成
                if self.progress >= self.required_count:
                    self.completed = True
                    return True
        return False
        
    def get_progress_text(self):
        """
        获取任务进度文本
        
        Returns:
            str: 任务进度描述
        """
        if self.objective.get("type") == "defeat_enemies":
            return f"{self.progress}/{self.required_count}"
        return "未知进度"
        
    def is_completed(self):
        """
        检查任务是否已完成
        
        Returns:
            bool: 如果任务已完成返回True，否则返回False
        """
        return self.completed
        
    def get_reward(self):
        """
        获取任务奖励
        
        Returns:
            dict: 任务奖励数据
        """
        return self.reward