#!/usr/bin/env python3
"""
Skill Manager - Standalone CLI (Windows Compatible)
"""

import sys
import os
import json
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ============================================================================
# Registry Module
# ============================================================================

class SkillRegistry:
    """Central registry for all Claude Code skills."""

    SKILLS_DIR = Path.home() / ".claude" / "skills"
    REGISTRY_FILE = Path.home() / ".claude" / "skill-manager" / "data" / "registry.json"

    def __init__(self):
        self.registry: Dict[str, Dict] = {}
        self._load_registry()

    def _load_registry(self):
        if self.REGISTRY_FILE.exists():
            try:
                with open(self.REGISTRY_FILE, 'r', encoding='utf-8') as f:
                    self.registry = json.load(f)
            except Exception:
                self.scan_skills()
        else:
            self.scan_skills()

    def _extract_frontmatter(self, skill_md_path: Path) -> Optional[Dict]:
        try:
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.startswith('---'):
                return None

            end_match = content.find('\n---', 3)
            if end_match == -1:
                return None

            frontmatter_text = content[3:end_match].strip()
            metadata = {}

            name_match = re.search(r'^name:\s*["\']?(.+?)["\']?\s*$', frontmatter_text, re.MULTILINE)
            if name_match:
                metadata['name'] = name_match.group(1).strip()

            desc_match = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', frontmatter_text, re.MULTILINE | re.DOTALL)
            if desc_match:
                desc = desc_match.group(1).strip()
                if desc.startswith('|'):
                    desc = desc[1:].strip()
                metadata['description'] = desc

            return metadata if 'name' in metadata and 'description' in metadata else None
        except Exception:
            return None

    def _extract_trigger_words(self, description: str) -> List[str]:
        triggers = []
        patterns = [
            r"TRIGGER when:.+contains\s+'([^']+)'",
            r"触发词[：:]\s*['\"]([^'\"]+)['\"]",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            triggers.extend(matches)

        quoted_words = re.findall(r'["\']([^"\']{3,20})["\']', description)
        common_words = {'the', 'this', 'that', 'when', 'use', 'user', 'skill', 'claude'}
        triggers.extend([w for w in quoted_words if w.lower() not in common_words])

        return list(set(triggers))[:10]

    def _categorize_skill(self, name: str, description: str) -> str:
        categories = {
            '思维方法': ['socrates', 'nuwa', 'karlmarx', '思维', '蒸馏'],
            '文本处理': ['humanizer', '润色', '文本'],
            '学术研究': ['research', 'confluencia', '学术', '论文'],
            '商业运营': ['business', 'marketing', 'product', 'project'],
            '合规质量': ['compliance', 'ra-qm', 'iso', 'gdpr'],
            '工程技术': ['engineering', 'figmirror', '工程'],
            'GitHub集成': ['github', 'git'],
            'Agent编排': ['swarm', 'agent', '编排'],
            '向量搜索': ['agentdb', 'vector', 'search', 'rag'],
            '强化学习': ['learning', 'rl'],
            '自动化工具': ['hooks', 'automation', 'stream'],
            '开发工具': ['skill-builder', 'sparc', 'pair'],
            '质量验证': ['verification', 'quality', 'verify'],
        }

        text = f"{name} {description}".lower()
        for category, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return category
        return '其他'

    def scan_skills(self) -> Dict[str, Dict]:
        self.registry = {}

        if not self.SKILLS_DIR.exists():
            print(f"Skills directory not found: {self.SKILLS_DIR}")
            return self.registry

        for skill_dir in self.SKILLS_DIR.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            metadata = self._extract_frontmatter(skill_md)
            if not metadata:
                continue

            skill_id = skill_dir.name
            description = metadata.get('description', '')

            skill_entry = {
                'skill_id': skill_id,
                'name': metadata.get('name', skill_id),
                'description': description,
                'trigger_words': self._extract_trigger_words(description),
                'category': self._categorize_skill(metadata.get('name', ''), description),
                'status': 'enabled',
                'path': str(skill_dir),
                'installed_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'metrics': {
                    'invocations': 0,
                    'success_rate': 0.0,
                    'avg_execution_time_ms': 0.0
                }
            }

            self.registry[skill_id] = skill_entry

        self._save_registry()
        return self.registry

    def _save_registry(self):
        self.REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
        print(f"Registry saved: {len(self.registry)} skills")

    def list_skills(self, category: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        skills = list(self.registry.values())
        if category:
            skills = [s for s in skills if s['category'] == category]
        if status:
            skills = [s for s in skills if s['status'] == status]
        return sorted(skills, key=lambda s: s['name'])

    def search_skills(self, query: str) -> List[Dict]:
        results = []
        query_lower = query.lower()

        for skill_id, skill in self.registry.items():
            score = 0.0
            for trigger in skill['trigger_words']:
                if trigger.lower() in query_lower:
                    score += 0.5
            if query_lower in skill['name'].lower():
                score += 0.4
            if query_lower in skill['description'].lower():
                score += 0.2

            if score > 0:
                results.append({'skill': skill, 'score': score})

        return sorted(results, key=lambda r: r['score'], reverse=True)

    def get_skill(self, skill_id: str) -> Optional[Dict]:
        return self.registry.get(skill_id)

    def enable_skill(self, skill_id: str) -> bool:
        if skill_id not in self.registry:
            return False
        self.registry[skill_id]['status'] = 'enabled'
        self._save_registry()
        return True

    def disable_skill(self, skill_id: str) -> bool:
        if skill_id not in self.registry:
            return False
        self.registry[skill_id]['status'] = 'disabled'
        self._save_registry()
        return True

    def get_stats(self) -> Dict:
        total = len(self.registry)
        enabled = sum(1 for s in self.registry.values() if s['status'] == 'enabled')
        categories = {}
        for skill in self.registry.values():
            cat = skill['category']
            categories[cat] = categories.get(cat, 0) + 1

        return {
            'total_skills': total,
            'enabled_skills': enabled,
            'disabled_skills': total - enabled,
            'categories': categories,
            'last_scan': datetime.now().isoformat()
        }


# ============================================================================
# Activation Engine Module
# ============================================================================

class ActivationEngine:
    """Multi-level skill activation engine."""

    def __init__(self, registry: SkillRegistry):
        self.registry = registry
        self.history_file = Path.home() / ".claude" / "skill-manager" / "data" / "activation_history.json"
        self.activation_history: List[Dict] = []
        self._load_history()

    def _load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.activation_history = json.load(f)
            except Exception:
                pass

    def _save_history(self):
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.activation_history[-100:], f, indent=2, ensure_ascii=False)

    def activate(self, prompt: str, context: Optional[Dict] = None) -> List[Dict]:
        results = []
        prompt_lower = prompt.lower()

        for skill_id, skill in self.registry.registry.items():
            if skill['status'] != 'enabled':
                continue

            score = 0.0
            matched_levels = []

            # Keyword matching
            for trigger in skill['trigger_words']:
                if trigger.lower() in prompt_lower:
                    score += 0.5
                    matched_levels.append('keyword')

            # Name matching
            if skill['name'].lower() in prompt_lower:
                score += 0.4
                if 'keyword' not in matched_levels:
                    matched_levels.append('name')

            # Description matching
            if any(word in skill['description'].lower() for word in prompt_lower.split()[:5]):
                score += 0.2
                if matched_levels:
                    matched_levels.append('semantic')

            if score > 0:
                results.append({
                    'skill': skill,
                    'confidence': round(score, 3),
                    'matched_levels': matched_levels,
                    'recommendation': 'primary' if score > 0.7 else 'secondary'
                })

        results = sorted(results, key=lambda r: r['confidence'], reverse=True)
        return results


# ============================================================================
# CLI Implementation
# ============================================================================

def create_parser():
    parser = argparse.ArgumentParser(
        description='Skill Manager CLI - Manage Claude Code skills',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List
    list_parser = subparsers.add_parser('list', help='List all skills')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--status', choices=['enabled', 'disabled'])
    list_parser.add_argument('--format', choices=['table', 'json'], default='table')

    # Search
    search_parser = subparsers.add_parser('search', help='Search skills')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--format', choices=['table', 'json'], default='table')

    # Info
    info_parser = subparsers.add_parser('info', help='Show skill details')
    info_parser.add_argument('skill_id', help='Skill ID')
    info_parser.add_argument('--metrics', action='store_true')

    # Enable/Disable
    enable_parser = subparsers.add_parser('enable', help='Enable a skill')
    enable_parser.add_argument('skill_id', help='Skill ID')

    disable_parser = subparsers.add_parser('disable', help='Disable a skill')
    disable_parser.add_argument('skill_id', help='Skill ID')

    # Scan
    scan_parser = subparsers.add_parser('scan', help='Rebuild skill registry')

    # Recommend
    recommend_parser = subparsers.add_parser('recommend', help='Recommend skills')
    recommend_parser.add_argument('prompt', nargs='?', default='')

    # Metrics
    metrics_parser = subparsers.add_parser('metrics', help='Show performance metrics')
    metrics_parser.add_argument('skill_id', nargs='?')

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    registry = SkillRegistry()
    engine = ActivationEngine(registry)

    if args.command == 'scan':
        print("\n[Scanning skills directory...]")
        skills = registry.scan_skills()
        print(f"\n[OK] Registry rebuilt: {len(skills)} skills")
        stats = registry.get_stats()
        print(f"\nStatistics:")
        print(f"  Enabled: {stats['enabled_skills']}")
        print(f"  Disabled: {stats['disabled_skills']}")
        print(f"\nCategories:")
        for cat, count in sorted(stats['categories'].items()):
            print(f"  {cat}: {count}")

    elif args.command == 'list':
        skills = registry.list_skills(category=args.category, status=args.status)
        if args.format == 'json':
            print(json.dumps(skills, indent=2, ensure_ascii=False))
        else:
            print(f"\n{'Skill ID':<30} {'Name':<20} {'Category':<15} {'Status':<10}")
            print('=' * 80)
            for skill in skills:
                print(f"{skill['skill_id']:<30} {skill['name']:<20} {skill['category']:<15} {skill['status']}")
            print(f"\nTotal: {len(skills)} skills")

    elif args.command == 'search':
        results = registry.search_skills(args.query)
        if not results:
            print(f"\n[WARN] No skills found for: '{args.query}'")
            return
        if args.format == 'json':
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(f"\nSearch Results for '{args.query}' ({len(results)} matches)\n")
            for result in results[:10]:
                skill = result['skill']
                print(f"  {skill['name']:<20} (score: {result['score']:.2f}, category: {skill['category']})")

    elif args.command == 'info':
        skill = registry.get_skill(args.skill_id)
        if not skill:
            print(f"\n[ERROR] Skill not found: '{args.skill_id}'")
            return
        print(f"\nSkill: {skill['name']}\n")
        print(f"ID: {skill['skill_id']}")
        print(f"Category: {skill['category']}")
        print(f"Status: {skill['status']}")
        print(f"\nDescription:\n  {skill['description'][:200]}...")
        print(f"\nTrigger Words:")
        for trigger in skill['trigger_words']:
            print(f"  - {trigger}")
        if args.metrics:
            metrics = skill['metrics']
            print(f"\nMetrics:")
            print(f"  Invocations: {metrics['invocations']}")
            print(f"  Success Rate: {metrics['success_rate']:.1%}")

    elif args.command == 'enable':
        if registry.enable_skill(args.skill_id):
            print(f"\n[OK] Skill enabled: {args.skill_id}")
        else:
            print(f"\n[ERROR] Failed to enable: {args.skill_id}")

    elif args.command == 'disable':
        if registry.disable_skill(args.skill_id):
            print(f"\n[OK] Skill disabled: {args.skill_id}")
        else:
            print(f"\n[ERROR] Failed to disable: {args.skill_id}")

    elif args.command == 'recommend':
        results = engine.activate(args.prompt)
        if not results:
            print("\n[WARN] No skill recommendations")
            return
        print(f"\nSkill Recommendations\n")
        for result in results[:5]:
            skill = result['skill']
            levels = ', '.join(result['matched_levels'])
            print(f"  {skill['name']:<20} (confidence: {result['confidence']:.2f}, levels: {levels})")

    elif args.command == 'metrics':
        if args.skill_id:
            skill = registry.get_skill(args.skill_id)
            if not skill:
                print(f"\n[ERROR] Skill not found: {args.skill_id}")
                return
            metrics = skill['metrics']
            print(f"\nMetrics for {skill['name']}\n")
            print(f"  Invocations: {metrics['invocations']}")
            print(f"  Success Rate: {metrics['success_rate']:.1%}")
        else:
            stats = registry.get_stats()
            all_skills = list(registry.registry.values())
            total_inv = sum(s['metrics']['invocations'] for s in all_skills)
            print(f"\nOverall Metrics\n")
            print(f"  Total Invocations: {total_inv}")
            print(f"  Total Skills: {stats['total_skills']}")
            print(f"  Active Skills: {stats['enabled_skills']}")


if __name__ == '__main__':
    main()