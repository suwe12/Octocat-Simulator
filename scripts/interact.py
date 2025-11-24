#!/usr/bin/env python3
"""
用户交互脚本
处理用户通过 Issue 提交的指令，更新 Octocat 状态
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime, timezone

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils import load_state, save_state
from decay import apply_decay


def parse_instruction(issue_title: str) -> str:
    """
    从 Issue 标题中提取指令
    
    标题格式：指令|Octavia
    例如：FEED|Octavia
    """
    # 按 | 分割标题
    parts = issue_title.strip().split('|')
    
    if len(parts) != 2:
        return None
    
    instruction = parts[0].strip().upper()
    pet_name = parts[1].strip()

    
    # 验证格式：中间部分应该是 Octavia
    if pet_name.upper() != 'OCTAVIA':
        return None
    
    # 验证指令是否有效
    valid_instructions = ['FEED', 'PLAY', 'PET', 'CARE', 'HEAL']
    if instruction not in valid_instructions:
        return None
    
    return instruction

def apply_instruction(state: dict, instruction: str) -> dict:
    """
    应用用户指令
    
    Args:
        state: 当前状态字典
        instruction: 用户指令（FEED, PLAY 等）
        
    Returns:
        dict: 更新后的状态字典
    """
    instruction = instruction.upper()
    
    if instruction == 'FEED':
        # 喂食：饥饿值减少 30，心情增加 10
        state['hunger'] = max(0, state['hunger'] - 30)
        state['mood'] = min(100, state['mood'] + 10)
        state['health'] = min(100, state['health'] + 5)  # 喂食也会稍微恢复健康
        
    elif instruction == 'PLAY':
        # 玩耍：心情增加 30，饥饿值增加 5
        state['mood'] = min(100, state['mood'] + 30)
        state['hunger'] = min(100, state['hunger'] + 5)
        
    elif instruction == 'PET':
        # 抚摸：心情增加 20
        state['mood'] = min(100, state['mood'] + 20)
        
    elif instruction == 'CARE':
        # 照顾：综合提升
        state['hunger'] = max(0, state['hunger'] - 20)
        state['mood'] = min(100, state['mood'] + 15)
        state['health'] = min(100, state['health'] + 3)
        
    elif instruction == 'HEAL':
        # 治疗：恢复健康
        state['health'] = min(100, state['health'] + 20)
        state['mood'] = min(100, state['mood'] + 10)

    # 更新状态图片
    if state['health'] < 30 or state['hunger'] > 80 or state['mood'] < 20:
        state['status_pic'] = "images/bad.png"
    elif state['health'] < 60 or state['hunger'] > 60 or state['mood'] < 40:
        state['status_pic'] = "images/general.png"
    else:
        state['status_pic'] = "images/good.png"
    
    return state


def generate_response(state: dict, instruction: str, username: str) -> str:
    """
    生成反馈消息
    
    Args:
        state: 更新后的状态字典
        instruction: 执行的指令
        username: 执行指令的用户名
        
    Returns:
        str: Markdown 格式的反馈消息
    """
    name = state['name']
    status_pic = state['status_pic']
    
    # 根据指令生成不同的消息
    messages = {
        'FEED': f"感谢 @{username} 喂食 {name}！{status_pic}",
        'PLAY': f"感谢 @{username} 和 {name} 一起玩耍！{status_pic}",
        'PET': f"感谢 @{username} 抚摸 {name}！{status_pic}",
        'CARE': f"感谢 @{username} 照顾 {name}！{status_pic}",
        'HEAL': f"感谢 @{username} 治疗 {name}！{status_pic}",
    }
    
    base_message = messages.get(instruction, f"感谢 @{username} 的指令！")
    
    response = f"""## {base_message}

### 📊 当前状态

- **健康值**: {state['health']}/100 {'❤️' * (state['health'] // 20)}
- **饥饿值**: {state['hunger']}/100 {'🍽️' * (10 - state['hunger'] // 10) if state['hunger'] < 100 else '😰'}
- **心情值**: {state['mood']}/100 {'😊' * (state['mood'] // 20)}
- **状态图片**: <img src="{state['status_pic']}" width="40%" alt="Octavia 当前状态">

---
*状态已自动更新 | 最后更新: {state['last_updated']}*
"""
    return response


def main():
    """主函数"""
    try:
        # 从环境变量获取 Issue 信息（GitHub Actions 会提供）
        issue_title = os.getenv('ISSUE_TITLE', '')
        issue_body = os.getenv('ISSUE_BODY', '')
        issue_author = os.getenv('ISSUE_AUTHOR', 'unknown')
        issue_number = os.getenv('ISSUE_NUMBER', '')
        
        if not issue_title:
            print("⚠️  警告: 未找到 Issue 标题，使用测试模式")
            issue_title = "FEED|Octavia"
            issue_author = "test-user"
        
        print(f"📝 Issue 标题: {issue_title}")
        print(f"👤 Issue 作者: {issue_author}")

        # 解析指令和作者名（从标题中提取）
        instruction = parse_instruction(issue_title)
        
      
        print(f"使用 GitHub 用户名: {issue_author}")
        
        if not instruction:
            print(f"❌ 未找到有效指令。支持的指令: FEED, PLAY, PET, CARE, HEAL")
            # 生成错误消息
            error_msg = f"""## ❌ 指令格式错误

Issue 标题格式不正确。

### 正确的格式：
标题必须遵循以下格式：

### 支持的指令：
- **FEED** - 喂食 Octavia（减少饥饿值）
- **PLAY** - 和 Octavia 玩耍（提升心情）
- **PET** - 抚摸 Octavia（提升心情）
- **CARE** - 照顾 Octavia（综合提升）
- **HEAL** - 治疗 Octavia（恢复健康）

### 使用示例：
- `FEED|Octavia|`
- `PLAY|Octavia|`
- `PET|Octavia|`
"""
           # 将错误消息输出到文件，供 GitHub Actions 使用
            response_file = os.getenv('GITHUB_STEP_SUMMARY', '/tmp/response.md')
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(error_msg)
            sys.exit(1)
        
        print(f"✅ 识别到指令: {instruction}")
        
        # 读取当前状态
        state = load_state()
        print(f"\n📊 执行前状态:")
        print(f"  健康值: {state['health']}")
        print(f"  饥饿值: {state['hunger']}")
        print(f"  心情值: {state['mood']}")
        
        # 先应用衰减（确保状态是最新的）
        print(f"\n⏰ 应用时间衰减...")
        state = apply_decay(state)
        
        # 应用用户指令
        print(f"\n🎮 执行指令: {instruction}")
        state = apply_instruction(state, instruction)
        
        # 保存状态
        save_state(state)
        
        print(f"\n📊 执行后状态:")
        print(f"  健康值: {state['health']}")
        print(f"  饥饿值: {state['hunger']}")
        print(f"  心情值: {state['mood']}")
        print(f"  状态图片: {state['status_pic']}")
        
        # 生成反馈消息（使用实际作者名）
        response = generate_response(state, instruction, issue_author)
        
        # 将反馈消息写入文件，供 GitHub Actions 使用
        response_file = os.getenv('GITHUB_STEP_SUMMARY', '/tmp/response.md')
        with open(response_file, 'w', encoding='utf-8') as f:
            f.write(response)
        
        # 同时输出到标准输出（用于调试）
        print(f"\n💬 反馈消息:")
        print(response)
        
        print(f"\n✅ 指令执行完成")
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()