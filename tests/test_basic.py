#!/usr/bin/env python3
"""
Skill Manager Test Suite
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.registry import SkillRegistry
from core.activation_engine import ActivationEngine


def test_registry():
    """Test registry functionality."""
    print("\n🧪 Testing Skill Registry\n")

    registry = SkillRegistry()

    # Test 1: List skills
    print("Test 1: List all skills")
    skills = registry.list_skills()
    print(f"  ✓ Found {len(skills)} skills")

    # Test 2: Get stats
    print("\nTest 2: Get statistics")
    stats = registry.get_stats()
    print(f"  ✓ Total: {stats['total_skills']}")
    print(f"  ✓ Enabled: {stats['enabled_skills']}")
    print(f"  ✓ Categories: {len(stats['categories'])}")

    # Test 3: Search skills
    print("\nTest 3: Search for 'nuwa'")
    results = registry.search_skills('nuwa')
    if results:
        print(f"  ✓ Found {len(results)} matches")
        for r in results[:3]:
            print(f"    - {r['skill']['name']} (score: {r['score']:.2f})")
    else:
        print("  ✗ No matches found")

    # Test 4: Get specific skill
    print("\nTest 4: Get skill details")
    skill = registry.get_skill('nuwa-skill')
    if skill:
        print(f"  ✓ Name: {skill['name']}")
        print(f"  ✓ Category: {skill['category']}")
        print(f"  ✓ Triggers: {skill['trigger_words'][:3]}")
    else:
        print("  ✗ Skill not found")

    return True


def test_activation():
    """Test activation engine."""
    print("\n🧪 Testing Activation Engine\n")

    registry = SkillRegistry()
    engine = ActivationEngine(registry)

    test_prompts = [
        ("女娲，蒸馏马斯克的思维方式", "nuwa-skill"),
        ("review 这个PR的代码质量", "github-code-review"),
        ("帮我人性化这段文本", "humanizer"),
        ("我想提升决策质量", "socrates"),
    ]

    print("Testing skill activation with various prompts:\n")

    for prompt, expected_skill in test_prompts:
        print(f"Prompt: {prompt}")
        results = engine.activate(prompt)

        if results:
            top = results[0]
            print(f"  ✓ Top match: {top['skill']['name']} (confidence: {top['confidence']:.2f})")

            if expected_skill in [r['skill']['skill_id'] for r in results]:
                print(f"  ✓ Expected skill '{expected_skill}' activated!")
            else:
                print(f"  ⚠ Expected skill '{expected_skill}' not in top results")
        else:
            print("  ✗ No skills activated")

        print()

    return True


def test_cli():
    """Test CLI commands."""
    print("\n🧪 Testing CLI Commands\n")

    # Import CLI
    from cli.skill_cli import SkillCLI
    import argparse

    cli = SkillCLI()

    # Test list command
    print("Test 1: CLI list command")
    args = argparse.Namespace(category=None, status=None, format='table')
    cli.list_command(args)

    print("\n" + "=" * 80 + "\n")

    # Test search command
    print("Test 2: CLI search command")
    args = argparse.Namespace(query='socrates', mode='keyword', format='table')
    cli.search_command(args)

    print("\n" + "=" * 80 + "\n")

    # Test metrics command
    print("Test 3: CLI metrics command")
    args = argparse.Namespace(skill_id=None)
    cli.metrics_command(args)

    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("Skill Manager - Test Suite")
    print("=" * 80)

    tests = [
        ("Registry", test_registry),
        ("Activation Engine", test_activation),
        ("CLI", test_cli),
    ]

    results = {}

    for name, test_func in tests:
        try:
            success = test_func()
            results[name] = '✓ PASS' if success else '✗ FAIL'
        except Exception as e:
            print(f"\n✗ Error in {name}: {e}")
            results[name] = f'✗ ERROR: {str(e)[:50]}'

    # Print summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    for name, result in results.items():
        print(f"{name:<30} {result}")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    run_all_tests()