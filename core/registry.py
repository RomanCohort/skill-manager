"""
Skill Manager - Enhanced Registry with Project Scanning

Automatically scans both global and project-level skills.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class SkillRegistry:
    """Enhanced registry for all Claude Code skills (global + project)."""

    # Global skills directory
    GLOBAL_SKILLS_DIR = Path.home() / ".claude" / "skills"
    # Registry file
    REGISTRY_FILE = Path.home() / ".claude" / "skill-manager" / "data" / "registry.json"

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize registry with optional project root.

        Args:
            project_root: Project root directory (defaults to cwd)
        """
        self.project_root = project_root or Path.cwd()
        self.registry: Dict[str, Dict] = {}
        self._load_registry()

    def _get_project_skills_dir(self) -> Path:
        """Get project-level skills directory."""
        return self.project_root / ".claude" / "skills"

    def _load_registry(self):
        """Load registry from file if it exists."""
        if self.REGISTRY_FILE.exists():
            with open(self.REGISTRY_FILE, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)

    def _extract_frontmatter(self, skill_md_path: Path) -> Optional[Dict]:
        """Extract YAML frontmatter from SKILL.md file."""
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

            # Extract name
            name_match = re.search(r'^name:\s*["\']?(.+?)["\']?\s*$', frontmatter_text, re.MULTILINE)
            if name_match:
                metadata['name'] = name_match.group(1).strip()

            # Extract description
            desc_match = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', frontmatter_text, re.MULTILINE | re.DOTALL)
            if desc_match:
                desc = desc_match.group(1).strip()
                if desc.startswith('|'):
                    desc = desc[1:].strip()
                metadata['description'] = desc

            return metadata if 'name' in metadata and 'description' in metadata else None

        except Exception as e:
            print(f"Error parsing {skill_md_path}: {e}")
            return None

    def _extract_trigger_words(self, description: str) -> List[str]:
        """Extract trigger words from skill description."""
        triggers = []

        # Pattern: TRIGGER when: ... contains 'word', 'word2'
        trigger_patterns = [
            r"TRIGGER when:.+contains\s+'([^']+)'",
            r"触发词[：:]\s*['\"]([^'\"]+)['\"]",
            r"trigger_words:\s*\[([^\]]+)\]",
        ]

        for pattern in trigger_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            triggers.extend(matches)

        # Extract quoted keywords
        quoted_words = re.findall(r'["\']([^"\']{3,20})["\']', description)
        common_words = {'the', 'this', 'that', 'when', 'use', 'user', 'skill', 'claude'}
        triggers.extend([w for w in quoted_words if w.lower() not in common_words])

        return list(set(triggers))[:10]

    def _categorize_skill(self, name: str, description: str) -> str:
        """Categorize skill based on name and description."""
        categories = {
            '思维方法': ['socrates', 'nuwa', 'karlmarx', '思维', '蒸馏', '苏格拉底'],
            '文本处理': ['humanizer', '润色', '文本', '写作'],
            '学术研究': ['research', 'confluencia', '学术', '论文', '研究'],
            '商业运营': ['business', 'commercial', 'finance', 'marketing', 'product', 'project'],
            '合规质量': ['compliance', 'ra-qm', 'iso', 'gdpr', '合规', '质量'],
            '工程技术': ['engineering', 'figmirror', '工程', '架构'],
            'GitHub集成': ['github', 'git'],
            'Agent编排': ['swarm', 'agent', '编排'],
            '向量搜索': ['agentdb', 'vector', 'search', 'rag'],
            '强化学习': ['learning', 'rl', 'reinforcement'],
            '自动化工具': ['hooks', 'automation', 'stream', '自动'],
            '开发工具': ['skill-builder', 'sparc', 'pair', 'browser', '开发'],
            '质量验证': ['verification', 'quality', 'verify', '验证'],
            '项目管理': ['project', 'management', '项目'],
        }

        text = f"{name} {description}".lower()

        for category, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return category

        return '其他'

    def _scan_skills_dir(self, skills_dir: Path, scope: str = 'global') -> Dict[str, Dict]:
        """Scan a specific skills directory.

        Args:
            skills_dir: Directory to scan
            scope: 'global' or 'project'

        Returns:
            Dict of skill_id -> skill_metadata
        """
        skills = {}

        if not skills_dir.exists():
            return skills

        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            # Extract metadata
            metadata = self._extract_frontmatter(skill_md)
            if not metadata:
                continue

            # Build skill entry
            skill_id = f"{scope}:{skill_dir.name}" if scope == 'project' else skill_dir.name
            description = metadata.get('description', '')

            skill_entry = {
                'skill_id': skill_id,
                'name': metadata.get('name', skill_dir.name),
                'description': description,
                'trigger_words': self._extract_trigger_words(description),
                'category': self._categorize_skill(metadata.get('name', ''), description),
                'status': 'enabled',
                'scope': scope,
                'path': str(skill_dir),
                'installed_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'metrics': {
                    'invocations': 0,
                    'success_rate': 0.0,
                    'avg_execution_time_ms': 0.0
                }
            }

            skills[skill_id] = skill_entry

        return skills

    def scan_skills(self, include_project: bool = True) -> Dict[str, Dict]:
        """Scan all skills (global + project).

        Args:
            include_project: Whether to scan project-level skills

        Returns:
            Dict of skill_id -> skill_metadata
        """
        self.registry = {}

        # Scan global skills
        print(f"Scanning global skills: {self.GLOBAL_SKILLS_DIR}")
        global_skills = self._scan_skills_dir(self.GLOBAL_SKILLS_DIR, scope='global')
        self.registry.update(global_skills)
        print(f"  Found {len(global_skills)} global skills")

        # Scan project skills
        if include_project:
            project_skills_dir = self._get_project_skills_dir()
            print(f"Scanning project skills: {project_skills_dir}")
            project_skills = self._scan_skills_dir(project_skills_dir, scope='project')
            self.registry.update(project_skills)
            if project_skills:
                print(f"  Found {len(project_skills)} project skills")

        # Save registry
        self._save_registry()

        return self.registry

    def _save_registry(self):
        """Save registry to JSON file."""
        self.REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(self.REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)

        print(f"Registry saved: {len(self.registry)} skills")

    def list_skills(self, category: Optional[str] = None, status: Optional[str] = None,
                    scope: Optional[str] = None) -> List[Dict]:
        """List all skills, optionally filtered.

        Args:
            category: Filter by category
            status: Filter by status (enabled/disabled)
            scope: Filter by scope (global/project)

        Returns:
            List of skill metadata
        """
        skills = list(self.registry.values())

        if category:
            skills = [s for s in skills if s['category'] == category]

        if status:
            skills = [s for s in skills if s['status'] == status]

        if scope:
            skills = [s for s in skills if s.get('scope', 'global') == scope]

        return sorted(skills, key=lambda s: (s.get('scope', 'global'), s['name']))

    def search_skills(self, query: str, mode: str = 'keyword') -> List[Dict]:
        """Search skills by query."""
        results = []
        query_lower = query.lower()

        for skill_id, skill in self.registry.items():
            score = 0.0

            # Keyword matching
            if mode in ['keyword', 'hybrid']:
                # Check trigger words
                for trigger in skill['trigger_words']:
                    if trigger.lower() in query_lower:
                        score += 0.5

                # Check name and description
                if query_lower in skill['name'].lower():
                    score += 0.4
                if query_lower in skill['description'].lower():
                    score += 0.2

            if score > 0:
                results.append({
                    'skill': skill,
                    'score': score,
                    'match_type': 'keyword'
                })

        return sorted(results, key=lambda r: r['score'], reverse=True)

    def get_skill(self, skill_id: str) -> Optional[Dict]:
        """Get a specific skill by ID."""
        return self.registry.get(skill_id)

    def enable_skill(self, skill_id: str) -> bool:
        """Enable a skill."""
        if skill_id not in self.registry:
            return False

        self.registry[skill_id]['status'] = 'enabled'
        self._save_registry()
        return True

    def disable_skill(self, skill_id: str) -> bool:
        """Disable a skill."""
        if skill_id not in self.registry:
            return False

        self.registry[skill_id]['status'] = 'disabled'
        self._save_registry()
        return True

    def update_metrics(self, skill_id: str, success: bool, execution_time_ms: float):
        """Update skill metrics after invocation."""
        if skill_id not in self.registry:
            return

        metrics = self.registry[skill_id]['metrics']

        # Update invocation count
        metrics['invocations'] += 1

        # Update success rate (rolling average)
        prev_rate = metrics['success_rate']
        prev_count = metrics['invocations'] - 1
        new_rate = (prev_rate * prev_count + (1.0 if success else 0.0)) / metrics['invocations']
        metrics['success_rate'] = round(new_rate, 3)

        # Update average execution time (rolling average)
        prev_time = metrics['avg_execution_time_ms']
        new_time = (prev_time * prev_count + execution_time_ms) / metrics['invocations']
        metrics['avg_execution_time_ms'] = round(new_time, 1)

        self._save_registry()

    def get_stats(self) -> Dict:
        """Get overall registry statistics."""
        total = len(self.registry)
        enabled = sum(1 for s in self.registry.values() if s['status'] == 'enabled')

        categories = {}
        scopes = {'global': 0, 'project': 0}

        for skill in self.registry.values():
            cat = skill['category']
            categories[cat] = categories.get(cat, 0) + 1

            scope = skill.get('scope', 'global')
            scopes[scope] = scopes.get(scope, 0) + 1

        return {
            'total_skills': total,
            'enabled_skills': enabled,
            'disabled_skills': total - enabled,
            'categories': categories,
            'scopes': scopes,
            'project_root': str(self.project_root),
            'last_scan': datetime.now().isoformat()
        }


# CLI-friendly functions
def main():
    """Main entry point for CLI."""
    import argparse

    parser = argparse.ArgumentParser(description='Skill Registry Manager')
    parser.add_argument('command', choices=['scan', 'list', 'stats'],
                       help='Command to execute')
    parser.add_argument('--category', help='Filter by category')
    parser.add_argument('--status', help='Filter by status')
    parser.add_argument('--scope', help='Filter by scope (global/project)')
    parser.add_argument('--no-project', action='store_true', help='Skip project skills')

    args = parser.parse_args()

    registry = SkillRegistry()

    if args.command == 'scan':
        skills = registry.scan_skills(include_project=not args.no_project)
        print(f"\n✓ Scanned {len(skills)} skills")

    elif args.command == 'list':
        skills = registry.list_skills(category=args.category, status=args.status, scope=args.scope)
        print(f"\n{'Skill ID':<35} {'Name':<20} {'Scope':<10} {'Category':<15} {'Status'}")
        print('-' * 95)
        for skill in skills:
            scope = skill.get('scope', 'global')
            print(f"{skill['skill_id']:<35} {skill['name']:<20} {scope:<10} {skill['category']:<15} {skill['status']}")

    elif args.command == 'stats':
        stats = registry.get_stats()
        print(f"\n📊 Registry Statistics")
        print(f"  Total Skills: {stats['total_skills']}")
        print(f"  Enabled: {stats['enabled_skills']}")
        print(f"  Disabled: {stats['disabled_skills']}")
        print(f"\n  Scopes:")
        for scope, count in stats['scopes'].items():
            print(f"    {scope}: {count}")
        print(f"\n  Categories:")
        for cat, count in sorted(stats['categories'].items()):
            print(f"    {cat}: {count}")
        print(f"\n  Project Root: {stats['project_root']}")


if __name__ == '__main__':
    main()