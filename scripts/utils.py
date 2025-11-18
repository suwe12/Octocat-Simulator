#!/usr/bin/env python3
"""
状态文件读写工具
提供原子性的读取和写入操作，避免 GitHub Actions 并发冲突
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any


# 状态文件路径，路径为：项目根目录/data/state.json
STATE_FILE = Path(__file__).parent.parent / "data" / "state.json"


def load_state() -> Dict[str, Any]:
    """
    读取状态文件，将读取的json数据转换为字典
    
    Returns:
        Dict[str, Any]: 状态字典
        
    Raises:
        FileNotFoundError: 如果状态文件不存在
        json.JSONDecodeError: 如果 JSON 格式错误
    """
    if not STATE_FILE.exists():
        raise FileNotFoundError(f"状态文件不存在: {STATE_FILE}")
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存文件
def save_state(state: Dict[str, Any]) -> None:
    """
    保存状态文件（原子性写入）
    
    Args:
        state: 要保存的状态字典
        
    Raises:
        OSError: 如果写入失败
    """
    # 确保目录存在
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # 更新最后更新时间戳
    state['last_updated'] = datetime.now(timezone.utc).isoformat()
    
    # 原子性写入：先写入临时文件，再重命名
    temp_file = STATE_FILE.with_suffix('.json.tmp')
    
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        # 重命名操作在大多数文件系统上是原子的
        temp_file.replace(STATE_FILE)
    except Exception as e:
        # 清理临时文件
        if temp_file.exists():
            temp_file.unlink()
        raise


def init_state() -> Dict[str, Any]:
    """
    初始化默认状态（如果状态文件不存在）
    
    Returns:
        Dict[str, Any]: 初始状态字典
    """
    default_state = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "name": "Octavia",
        "health": 100,
        "hunger": 50,
        "mood": 80,
        "level": 1,
        "owner_count": 0,
        "status_emoji": "🐙"
    }
    
    if not STATE_FILE.exists():
        save_state(default_state)
        print(f"已创建初始状态文件: {STATE_FILE}")
    
    return default_state


def get_state() -> Dict[str, Any]:
    """
    获取当前状态（如果不存在则初始化）
    
    Returns:
        Dict[str, Any]: 状态字典
    """
    try:
        return load_state()
    except FileNotFoundError:
        return init_state()


if __name__ == "__main__":
    # 测试代码
    print("测试状态文件工具...")
    
    # 初始化状态
    state = get_state()
    print(f"当前状态: {json.dumps(state, indent=2, ensure_ascii=False)}")
    
    # 测试更新
    state['mood'] = 90
    save_state(state)
    print("状态已更新")
    
    # 验证读取
    loaded_state = load_state()
    print(f"验证读取: mood = {loaded_state['mood']}")