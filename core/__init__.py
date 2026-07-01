"""
Skill Manager - Core Package
"""

from .registry import SkillRegistry
from .activation_engine import ActivationEngine

__version__ = '0.1.0'

__all__ = ['SkillRegistry', 'ActivationEngine']