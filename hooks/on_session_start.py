"""
Skill Manager - Session Start Hook (Non-Interactive)

This hook runs at session start and checks config to determine
if auto-activation should be enabled.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Config file
CONFIG_FILE = Path.home() / ".claude" / "skill-manager" / "data" / "config.json"

def load_config():
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "auto_activation_enabled": False,
        "default_choice": "ask",
        "session_count": 0
    }

def save_config(config):
    """Save configuration to file."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def main():
    """Main hook function."""
    config = load_config()

    # Increment session count
    config["session_count"] += 1
    config["last_session"] = datetime.now().isoformat()

    # Check default choice
    default = config.get("default_choice", "ask")

    if default == "always":
        config["auto_activation_enabled"] = True
        save_config(config)
        print("\n[Skill Manager] Auto-activation ENABLED (always)")
        print("  37 skills ready for activation")
        print("  Disable: Edit config.json or use CLI")

    elif default == "never":
        config["auto_activation_enabled"] = False
        save_config(config)
        # Silent - no output if disabled

    elif default == "ask":
        # Show status message
        print("\n[Skill Manager] Ready")
        print("  37 skills registered")
        print("  Auto-activation: DISABLED (default)")
        print("  ")
        print("  To enable, edit config.json:")
        print("    ~/.claude/skill-manager/data/config.json")
        print("    Set: \"default_choice\": \"always\"")
        print("  ")
        print("  Or use CLI:")
        print("    python skill_manager.py recommend \"<prompt>\"")

        config["auto_activation_enabled"] = False
        save_config(config)

if __name__ == '__main__':
    main()