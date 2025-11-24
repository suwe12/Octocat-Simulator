#!/usr/bin/env python3
"""
README 自动更新脚本
- 读取 data/state.json
- 生成与现有 README 格式一致的中英双语内容
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
STATE_FILE = ROOT_DIR / "data" / "state.json"
README_FILE = ROOT_DIR / "README.md"

# 统一的 Issue 链接模板（记得根据需要调整默认的作者名）
DEFAULT_AUTHOR = "your-name"
ISSUE_BASE = "https://github.com/suwe12/Octocat-Simulator/issues/new?title={title}&body=You%20don't%20need%20to%20do%20anything,%20just%20click%20'create'"

COMMAND_LINKS = [
    ("喂食|降低饥饿", "FEED"),
    ("玩耍|玩耍，提升心情", "PLAY"),
    ("抚摸|轻微提升心情", "PET"),
    ("照顾|综合提升", "CARE"),
    ("治疗|大幅恢复健康", "HEAL"),
]

def load_state():
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def build_link(label: str, command: str) -> str:
    title = f"{command}%7COctavia%7C{DEFAULT_AUTHOR}"
    url = ISSUE_BASE.format(title=title)
    return f"- [{label}]({url})"

def build_readme(state: dict) -> str:
    links_section = "\n".join(
        build_link(label, cmd) for label, cmd in COMMAND_LINKS
    )

    hunger_icons = "🍽️" * max(1, (100 - state["hunger"]) // 20)
    mood_icons = "😊" * max(1, state["mood"] // 20)

    return f"""# Octocat-Simulator

一个由社区驱动的、基于 GitHub Issues 的虚拟 Octocat 宠物养成项目。

## 状态概览 / Status Overview
<img src="{state['status_pic']}" width="40%" alt="Octavia 当前状态">
- **健康 Health**: {state['health']} / 100 ❤️❤️❤️❤️
- **饥饿 Hunger**: {state['hunger']} / 100 {hunger_icons}
- **心情 Mood**: {state['mood']} / 100 {mood_icons}


## 可用指令 / Available Commands

{links_section}

**自动更新 / Auto-updated at {state['last_updated']}**
"""

def main():
    state = load_state()
    readme_content = build_readme(state)
    README_FILE.write_text(readme_content, encoding="utf-8")
    print("README 已更新 / README updated.")

if __name__ == "__main__":
    main()