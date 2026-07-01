"""
Skill Manager - Prompt Submit Hook (Auto-Activation)

This hook analyzes user prompts and recommends relevant skills.
Only runs if auto-activation is enabled in config.
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

# Import registry (inline to avoid import issues)
REGISTRY_FILE = Path.home() / ".claude" / "skill-manager" / "data" / "registry.json"
CONFIG_FILE = Path.home() / ".claude" / "skill-manager" / "data" / "config.json"
HISTORY_FILE = Path.home() / ".claude" / "skill-manager" / "data" / "activation_history.json"

def load_config():
    """Load configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"auto_activation_enabled": False}

def load_registry():
    """Load skill registry."""
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def activate_skills(prompt, registry):
    """Activate skills based on prompt."""
    results = []
    prompt_lower = prompt.lower()

    for skill_id, skill in registry.items():
        if skill['status'] != 'enabled':
            continue

        score = 0.0
        matched_levels = []

        # Keyword matching
        for trigger in skill.get('trigger_words', []):
            if trigger.lower() in prompt_lower:
                score += 0.5
                matched_levels.append('keyword')

        # Name matching
        if skill['name'].lower() in prompt_lower:
            score += 0.4
            if 'keyword' not in matched_levels:
                matched_levels.append('name')

        # Description keywords
        desc_keywords = re.findall(r'\b[a-z]{4,}\b', skill['description'].lower())
        desc_keywords = [k for k in desc_keywords[:20] if k not in {'this', 'that', 'when', 'use', 'with'}]
        matches = sum(1 for k in desc_keywords if k in prompt_lower)

        if matches >= 2:
            score += matches * 0.1
            matched_levels.append('semantic')

        if score > 0:
            results.append({
                'skill_id': skill_id,
                'name': skill['name'],
                'category': skill['category'],
                'confidence': round(score, 2),
                'matched_levels': matched_levels,
                'recommendation': 'primary' if score > 0.7 else 'secondary'
            })

    return sorted(results, key=lambda r: r['confidence'], reverse=True)

def record_activation(prompt, results):
    """Record activation to history."""
    history = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)

    record = {
        'timestamp': datetime.now().isoformat(),
        'prompt': prompt[:100],  # Truncate long prompts
        'prompt_keywords': re.findall(r'\b[a-z一-鿿]{2,}\b', prompt.lower())[:10],
        'activations': results[:5],
        'success': False  # Updated later
    }

    history.append(record)

    # Keep last 100 records
    history = history[-100:]

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def main():
    """Main hook function."""
    # Check if auto-activation is enabled
    config = load_config()

    if not config.get('auto_activation_enabled', False):
        # Silent skip - no output if disabled
        return

    # Get prompt from stdin (passed by Claude Code hook)
    prompt = ""
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    else:
        # Try to read from stdin
        try:
            prompt = sys.stdin.read().strip()
        except:
            return

    if not prompt:
        return

    # Load registry and activate
    registry = load_registry()
    results = activate_skills(prompt, registry)

    # Record activation
    if results:
        record_activation(prompt, results)

        # Show recommendations
        print("\n[Skill Manager] Detected skills:")
        for result in results[:3]:
            levels = ', '.join(result['matched_levels'])
            print(f"  - {result['name']} ({result['confidence']}, {levels})")

        print("\n  Tip: Use skills by mentioning their triggers in your prompt.")
        print("  Disable: Edit ~/.claude/skill-manager/data/config.json")

if __name__ == '__main__':
    main()