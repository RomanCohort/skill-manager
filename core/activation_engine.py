"""
Skill Manager - Activation Engine Module

This module implements multi-level skill activation strategies.
"""

import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json

from .registry import SkillRegistry


class ActivationEngine:
    """Multi-level skill activation engine."""

    def __init__(self, registry: SkillRegistry):
        """Initialize activation engine.

        Args:
            registry: SkillRegistry instance
        """
        self.registry = registry
        self.activation_history: List[Dict] = []
        self.history_file = Path.home() / ".claude" / "skill-manager" / "data" / "activation_history.json"
        self._load_history()

    def _load_history(self):
        """Load activation history from file."""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.activation_history = json.load(f)

    def _save_history(self):
        """Save activation history to file."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.activation_history[-100:], f, indent=2, ensure_ascii=False)  # Keep last 100

    def keyword_match(self, prompt: str, skill: Dict) -> Tuple[bool, float]:
        """Level 1: Keyword matching.

        Args:
            prompt: User input
            skill: Skill metadata

        Returns:
            Tuple of (matched, confidence)
        """
        prompt_lower = prompt.lower()

        # Check trigger words
        for trigger in skill.get('trigger_words', []):
            if trigger.lower() in prompt_lower:
                return True, 1.0

        # Check skill name
        if skill['name'].lower() in prompt_lower:
            return True, 0.9

        return False, 0.0

    def semantic_similarity(self, prompt: str, skill: Dict) -> Tuple[bool, float]:
        """Level 2: Semantic similarity (placeholder for future implementation).

        Args:
            prompt: User input
            skill: Skill metadata

        Returns:
            Tuple of (matched, confidence)
        """
        # Placeholder - would use vector embeddings
        # For now, use keyword-based heuristics

        prompt_lower = prompt.lower()
        desc_lower = skill['description'].lower()

        # Extract key terms from description
        key_terms = re.findall(r'\b[a-z]{4,}\b', desc_lower)
        key_terms = [t for t in key_terms if t not in {'this', 'that', 'when', 'use', 'with', 'from', 'skill'}]

        matches = sum(1 for term in key_terms[:10] if term in prompt_lower)

        if matches > 0:
            confidence = min(0.75, matches * 0.15)
            return True, confidence

        return False, 0.0

    def context_aware(self, prompt: str, context: Dict, skill: Dict) -> Tuple[bool, float]:
        """Level 3: Context-aware matching.

        Args:
            prompt: User input
            context: Context dict with file types, project type, history
            skill: Skill metadata

        Returns:
            Tuple of (matched, confidence)
        """
        score = 0.0

        # Check recent skill usage
        recent_skills = context.get('recent_skills', [])
        if skill['skill_id'] in recent_skills[-5:]:
            score += 0.3

        # Check file type associations
        file_types = context.get('file_types', [])
        skill_keywords = skill.get('trigger_words', [])

        file_skill_map = {
            '.py': ['python', 'engineering', 'code'],
            '.js': ['javascript', 'frontend', 'web'],
            '.md': ['markdown', 'document', 'writing'],
            '.json': ['config', 'data'],
        }

        for ext in file_types:
            if ext in file_skill_map:
                if any(kw in ' '.join(skill_keywords).lower() for kw in file_skill_map[ext]):
                    score += 0.2

        # Check category relevance
        project_type = context.get('project_type', '')
        category = skill.get('category', '')

        project_category_map = {
            'web': '工程技术',
            'research': '学术研究',
            'business': '商业运营',
            'compliance': '合规质量',
        }

        if project_type in project_category_map:
            if category == project_category_map[project_type]:
                score += 0.25

        return score > 0.5, score

    def learned_patterns(self, prompt: str, skill: Dict) -> Tuple[bool, float]:
        """Level 4: Learned pattern matching.

        Args:
            prompt: User input
            skill: Skill metadata

        Returns:
            Tuple of (matched, confidence)
        """
        # Check activation history for patterns
        skill_id = skill['skill_id']

        # Find successful activations of this skill
        successful = [h for h in self.activation_history
                     if h['skill_id'] == skill_id and h['success']]

        if not successful:
            return False, 0.0

        # Extract common patterns from successful prompts
        common_keywords = []
        for record in successful[-10:]:
            keywords = record.get('prompt_keywords', [])
            common_keywords.extend(keywords)

        # Check if current prompt matches patterns
        prompt_lower = prompt.lower()
        matches = sum(1 for kw in common_keywords if kw in prompt_lower)

        if matches >= 2:
            confidence = min(matches / len(common_keywords), 0.85)
            return True, confidence

        return False, 0.0

    def activate(self, prompt: str, context: Optional[Dict] = None) -> List[Dict]:
        """Activate skills based on prompt and context.

        Args:
            prompt: User input
            context: Optional context dict

        Returns:
            List of activation results with skills and confidence
        """
        if context is None:
            context = {}

        results = []

        for skill_id, skill in self.registry.registry.items():
            if skill['status'] != 'enabled':
                continue

            # Multi-level matching
            matched_levels = []
            total_confidence = 0.0

            # Level 1: Keyword
            kw_match, kw_conf = self.keyword_match(prompt, skill)
            if kw_match:
                matched_levels.append('keyword')
                total_confidence += kw_conf * 0.5  # Weight: 50%

            # Level 2: Semantic
            sem_match, sem_conf = self.semantic_similarity(prompt, skill)
            if sem_match:
                matched_levels.append('semantic')
                total_confidence += sem_conf * 0.25  # Weight: 25%

            # Level 3: Context
            ctx_match, ctx_conf = self.context_aware(prompt, context, skill)
            if ctx_match:
                matched_levels.append('context')
                total_confidence += ctx_conf * 0.15  # Weight: 15%

            # Level 4: Learned
            learn_match, learn_conf = self.learned_patterns(prompt, skill)
            if learn_match:
                matched_levels.append('learned')
                total_confidence += learn_conf * 0.10  # Weight: 10%

            if matched_levels:
                results.append({
                    'skill': skill,
                    'confidence': round(total_confidence, 3),
                    'matched_levels': matched_levels,
                    'recommendation': 'primary' if total_confidence > 0.7 else 'secondary'
                })

        # Sort by confidence
        results = sorted(results, key=lambda r: r['confidence'], reverse=True)

        # Record activation
        if results:
            self._record_activation(prompt, results[:5])

        return results

    def _record_activation(self, prompt: str, activations: List[Dict]):
        """Record activation event for learning.

        Args:
            prompt: User prompt
            activations: List of activation results
        """
        # Extract keywords from prompt
        keywords = re.findall(r'\b[a-z一-鿿]{2,}\b', prompt.lower())
        keywords = [kw for kw in keywords if kw not in {'这个', '那个', '什么', '怎么'}]

        record = {
            'timestamp': str(Path.home()),
            'prompt_keywords': keywords[:10],
            'activations': [
                {
                    'skill_id': a['skill']['skill_id'],
                    'confidence': a['confidence'],
                    'levels': a['matched_levels']
                }
                for a in activations
            ],
            'success': False  # Will be updated later
        }

        self.activation_history.append(record)
        self._save_history()

    def mark_success(self, skill_id: str, success: bool):
        """Mark an activation as successful or not.

        Args:
            skill_id: Skill that was activated
            success: Whether it was successful
        """
        if self.activation_history:
            # Update most recent activation of this skill
            for record in reversed(self.activation_history):
                for activation in record['activations']:
                    if activation['skill_id'] == skill_id:
                        record['success'] = success
                        break

        self._save_history()


def main():
    """Test activation engine."""
    registry = SkillRegistry()
    engine = ActivationEngine(registry)

    test_prompts = [
        "女娲，蒸馏马斯克的思维方式",
        "review 这个PR",
        "帮我优化这段代码的性能",
        "我想提升决策质量",
    ]

    print("\n🧪 Testing Activation Engine\n")

    for prompt in test_prompts:
        print(f"Prompt: {prompt}")
        results = engine.activate(prompt)

        if results:
            print(f"  ✓ Activated {len(results)} skills:")
            for r in results[:3]:
                print(f"    - {r['skill']['name']} (confidence: {r['confidence']}, levels: {r['matched_levels']})")
        else:
            print("  ✗ No skills activated")
        print()


if __name__ == '__main__':
    main()