"""
Skill Manager - CLI Interface

Main command-line interface for skill management.
"""

import argparse
import json
from pathlib import Path
from typing import Optional

from ..core.registry import SkillRegistry
from ..core.activation_engine import ActivationEngine


class SkillCLI:
    """Command-line interface for Skill Manager."""

    def __init__(self):
        """Initialize CLI."""
        self.registry = SkillRegistry()
        self.activation_engine = ActivationEngine(self.registry)

    def list_command(self, args):
        """List all skills."""
        skills = self.registry.list_skills(category=args.category, status=args.status)

        if args.format == 'json':
            print(json.dumps(skills, indent=2, ensure_ascii=False))
            return

        # Table format
        print(f"\n{'Skill ID':<30} {'Name':<20} {'Category':<15} {'Status':<10} {'Invocations'}")
        print('=' * 95)

        for skill in skills:
            invocations = skill['metrics']['invocations']
            print(f"{skill['skill_id']:<30} {skill['name']:<20} {skill['category']:<15} {skill['status']:<10} {invocations}")

        print(f"\nTotal: {len(skills)} skills")

    def search_command(self, args):
        """Search skills by query."""
        results = self.registry.search_skills(args.query, mode=args.mode)

        if not results:
            print(f"\n✗ No skills found for query: '{args.query}'")
            return

        if args.format == 'json':
            print(json.dumps(results, indent=2, ensure_ascii=False))
            return

        print(f"\n🔍 Search Results for '{args.query}' ({len(results)} matches)\n")
        print(f"{'Skill':<25} {'Score':<8} {'Category':<15} {'Triggers'}")
        print('-' * 80)

        for result in results[:10]:
            skill = result['skill']
            triggers = ', '.join(skill['trigger_words'][:3])
            print(f"{skill['name']:<25} {result['score']:<8.2f} {skill['category']:<15} {triggers}")

    def info_command(self, args):
        """Show skill details."""
        skill = self.registry.get_skill(args.skill_id)

        if not skill:
            print(f"\n✗ Skill not found: '{args.skill_id}'")
            return

        if args.format == 'json':
            print(json.dumps(skill, indent=2, ensure_ascii=False))
            return

        print(f"\n📋 Skill: {skill['name']}\n")
        print(f"ID: {skill['skill_id']}")
        print(f"Category: {skill['category']}")
        print(f"Status: {skill['status']}")
        print(f"Path: {skill['path']}")
        print(f"\nDescription:\n  {skill['description'][:200]}...")

        print(f"\nTrigger Words:")
        for trigger in skill['trigger_words']:
            print(f"  • {trigger}")

        if args.metrics:
            metrics = skill['metrics']
            print(f"\n📊 Metrics:")
            print(f"  Invocations: {metrics['invocations']}")
            print(f"  Success Rate: {metrics['success_rate']:.1%}")
            print(f"  Avg Execution Time: {metrics['avg_execution_time_ms']}ms")

    def enable_command(self, args):
        """Enable a skill."""
        if self.registry.enable_skill(args.skill_id):
            print(f"\n✓ Skill enabled: {args.skill_id}")
        else:
            print(f"\n✗ Failed to enable skill: {args.skill_id}")

    def disable_command(self, args):
        """Disable a skill."""
        if self.registry.disable_skill(args.skill_id):
            print(f"\n✓ Skill disabled: {args.skill_id}")
        else:
            print(f"\n✗ Failed to disable skill: {args.skill_id}")

    def scan_command(self, args):
        """Scan and rebuild registry."""
        print("\n🔄 Scanning skills directory...")
        skills = self.registry.scan_skills()

        print(f"\n✓ Registry rebuilt: {len(skills)} skills")
        stats = self.registry.get_stats()
        print(f"\n📊 Statistics:")
        print(f"  Enabled: {stats['enabled_skills']}")
        print(f"  Disabled: {stats['disabled_skills']}")
        print(f"\n  Categories:")
        for cat, count in sorted(stats['categories'].items()):
            print(f"    {cat}: {count}")

    def recommend_command(self, args):
        """Recommend skills based on context."""
        prompt = args.prompt or ""
        context = {}

        # Build context from current directory
        cwd = Path.cwd()
        file_types = [f.suffix for f in cwd.glob('*') if f.is_file()][:5]
        context['file_types'] = file_types
        context['project_type'] = self._detect_project_type(cwd)

        results = self.activation_engine.activate(prompt, context)

        if not results:
            print("\n✗ No skill recommendations available")
            return

        print(f"\n💡 Skill Recommendations\n")
        print(f"{'Skill':<25} {'Confidence':<12} {'Match Types':<20} {'Recommendation'}")
        print('-' * 85)

        for result in results[:5]:
            skill = result['skill']
            levels = ', '.join(result['matched_levels'])
            print(f"{skill['name']:<25} {result['confidence']:<12.2f} {levels:<20} {result['recommendation']}")

    def auto_command(self, args):
        """Manage auto-activation."""
        if args.action == 'on':
            print("\n✓ Auto-activation enabled")
            print("  Skills will be automatically recommended based on your prompts")

        elif args.action == 'off':
            print("\n✓ Auto-activation disabled")
            print("  Skills will only activate when explicitly invoked")

        elif args.action == 'history':
            history = self.activation_engine.activation_history
            limit = args.limit or 10

            print(f"\n📜 Activation History (last {limit})\n")
            print(f"{'Timestamp':<20} {'Skills':<30} {'Success'}")
            print('-' * 70)

            for record in history[-limit:]:
                skills = ', '.join([a['skill_id'] for a in record['activations'][:3]])
                success = '✓' if record['success'] else '?'
                print(f"{record['timestamp'][:19]:<20} {skills:<30} {success}")

        elif args.action == 'strategy':
            print(f"\n⚙️  Activation Strategy: {args.strategy}")
            strategies = {
                'conservative': 'Only activate skills with >90% confidence',
                'balanced': 'Activate skills with >70% confidence (recommended)',
                'aggressive': 'Activate skills with >50% confidence'
            }
            print(f"  {strategies.get(args.strategy, 'Unknown strategy')}")

    def metrics_command(self, args):
        """Show performance metrics."""
        if args.skill_id:
            skill = self.registry.get_skill(args.skill_id)
            if not skill:
                print(f"\n✗ Skill not found: {args.skill_id}")
                return

            metrics = skill['metrics']
            print(f"\n📊 Metrics for {skill['name']}\n")
            print(f"  Invocations: {metrics['invocations']}")
            print(f"  Success Rate: {metrics['success_rate']:.1%}")
            print(f"  Avg Execution Time: {metrics['avg_execution_time_ms']:.1f}ms")

        else:
            stats = self.registry.get_stats()

            # Calculate aggregate metrics
            all_skills = list(self.registry.registry.values())
            total_invocations = sum(s['metrics']['invocations'] for s in all_skills)
            avg_success = sum(s['metrics']['success_rate'] for s in all_skills) / len(all_skills) if all_skills else 0

            print(f"\n📊 Overall Metrics\n")
            print(f"  Total Invocations: {total_invocations}")
            print(f"  Average Success Rate: {avg_success:.1%}")
            print(f"  Total Skills: {stats['total_skills']}")
            print(f"  Active Skills: {stats['enabled_skills']}")

            # Top skills by invocations
            top_skills = sorted(all_skills, key=lambda s: s['metrics']['invocations'], reverse=True)[:5]

            if top_skills and top_skills[0]['metrics']['invocations'] > 0:
                print(f"\n🏆 Top Skills by Usage\n")
                for i, skill in enumerate(top_skills, 1):
                    inv = skill['metrics']['invocations']
                    rate = skill['metrics']['success_rate']
                    print(f"  {i}. {skill['name']}: {inv} invocations ({rate:.1%} success)")

    def _detect_project_type(self, path: Path) -> str:
        """Detect project type from directory contents.

        Args:
            path: Project root path

        Returns:
            Project type string
        """
        # Check for specific files/directories
        indicators = {
            'web': ['package.json', 'node_modules', 'src/'],
            'research': ['requirements.txt', 'data/', 'notebooks/', 'paper.md'],
            'business': ['financial/', 'reports/', 'metrics.json'],
            'compliance': ['docs/', 'policies/', 'audit/'],
        }

        for project_type, files in indicators.items():
            if any((path / f).exists() for f in files):
                return project_type

        return 'general'


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description='Skill Manager CLI - Manage Claude Code skills',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  skill list --category "思维方法"
  skill search "代码审查"
  skill info nuwa-skill --metrics
  skill recommend "我想优化性能"
  skill auto history --limit 20
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List command
    list_parser = subparsers.add_parser('list', help='List all skills')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--status', choices=['enabled', 'disabled'], help='Filter by status')
    list_parser.add_argument('--format', choices=['table', 'json'], default='table', help='Output format')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search skills')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--mode', choices=['keyword', 'semantic', 'hybrid'], default='keyword')
    search_parser.add_argument('--format', choices=['table', 'json'], default='table')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show skill details')
    info_parser.add_argument('skill_id', help='Skill ID')
    info_parser.add_argument('--metrics', action='store_true', help='Show performance metrics')
    info_parser.add_argument('--format', choices=['table', 'json'], default='table')

    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable a skill')
    enable_parser.add_argument('skill_id', help='Skill ID')

    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Disable a skill')
    disable_parser.add_argument('skill_id', help='Skill ID')

    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Rebuild skill registry')

    # Recommend command
    recommend_parser = subparsers.add_parser('recommend', help='Recommend skills')
    recommend_parser.add_argument('prompt', nargs='?', default='', help='User prompt')

    # Auto command
    auto_parser = subparsers.add_parser('auto', help='Manage auto-activation')
    auto_parser.add_argument('action', choices=['on', 'off', 'history', 'strategy'],
                            help='Auto-activation action')
    auto_parser.add_argument('--limit', type=int, help='History limit')
    auto_parser.add_argument('--strategy', choices=['conservative', 'balanced', 'aggressive'],
                            help='Activation strategy')

    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Show performance metrics')
    metrics_parser.add_argument('skill_id', nargs='?', help='Skill ID (optional)')

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = SkillCLI()

    # Dispatch commands
    command_map = {
        'list': cli.list_command,
        'search': cli.search_command,
        'info': cli.info_command,
        'enable': cli.enable_command,
        'disable': cli.disable_command,
        'scan': cli.scan_command,
        'recommend': cli.recommend_command,
        'auto': cli.auto_command,
        'metrics': cli.metrics_command,
    }

    handler = command_map.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()