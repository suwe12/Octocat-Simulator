#!/usr/bin/env python3
"""
定时衰减脚本
模拟时间流逝，让 Octocat 的状态自然衰减
"""
#流程如下：读取当前状态，衰减，更新state文件

import sys
from pathlib import Path

# 添加 scripts 目录到路径，以便导入 utils
sys.path.insert(0, str(Path(__file__).parent))

from utils import load_state, save_state


def apply_decay(state):
    """
    应用衰减逻辑
    
    衰减规则：
    - hunger 增加 20 点（更饿）
    - mood 减少 10 点（心情下降）
    - 如果 hunger > 80 或 mood < 20，health 减少 5 点
    
    Args:
        state: 当前状态字典
        
    Returns:
        Dict: 更新后的状态字典
    """
    # 应用基础衰减
    state['hunger'] = min(100, state['hunger'] + 20)  # 饥饿值增加，最高 100
    state['mood'] = max(0, state['mood'] - 10)  # 心情下降，最低 0
    
    # 如果状态很差，健康值下降
    if state['hunger'] > 80 or state['mood'] < 20:
        state['health'] = max(0, state['health'] - 5)  # 健康值下降，最低 0
    
    # 根据状态更新表情符号
    if state['health'] < 30 or state['hunger'] > 80 or state['mood'] < 20:
        state['status_emoji'] = "😰"  # 状态不好
    elif state['health'] < 60 or state['hunger'] > 60 or state['mood'] < 40:
        state['status_emoji'] = "😐"  # 状态一般
    else:
        state['status_emoji'] = "🐙"  # 状态良好
    
    return state


def main():
    """主函数"""
    try:
        # 读取当前状态
        state = load_state()
        
        print(f"衰减前状态:")
        print(f"  健康值: {state['health']}")
        print(f"  饥饿值: {state['hunger']}")
        print(f"  心情值: {state['mood']}")
        
        # 应用衰减
        state = apply_decay(state)
        
        # 保存状态
        save_state(state)
        
        print(f"\n衰减后状态:")
        print(f"  健康值: {state['health']}")
        print(f"  饥饿值: {state['hunger']}")
        print(f"  心情值: {state['mood']}")
        print(f"  表情: {state['status_emoji']}")
        print(f"\n✅ 状态已更新并保存")
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()