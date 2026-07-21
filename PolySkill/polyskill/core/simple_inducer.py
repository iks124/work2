#!/usr/bin/env python3
"""
Simple Skill Inducer for Online Learning

A minimal, hackable implementation that extracts reusable patterns from successful trajectories.
Focus: Simplicity over optimization.
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """Simple skill representation."""
    id: str
    name: str
    pattern: List[Dict[str, Any]]  # List of actions
    task_examples: List[str]  # Tasks where this skill was used
    success_count: int = 1
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'pattern': self.pattern,
            'task_examples': self.task_examples,
            'success_count': self.success_count,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Skill':
        return cls(**data)


class _KnowledgeBase:
    """Inner object exposing a read-only view of tested/stored skills."""

    def __init__(self, inducer: 'SimpleSkillInducer') -> None:
        self._inducer = inducer

    def get_tested_skills(self) -> List[Skill]:
        """Return all currently stored skills (treated as tested/validated)."""
        return self._inducer.skills.copy()


class SimpleSkillInducer:
    """
    Simple skill inducer that extracts action patterns from trajectories.

    Key principles:
    - Simple pattern matching
    - No complex ML - just basic heuristics
    - Fast and hackable
    - JSON-based storage
    """

    def __init__(
        self,
        storage_path: str = "./learned_skills/",
        min_actions: int = 2,
        max_actions: int = 8
    ):
        self.storage_path = Path(storage_path)
        self.min_actions = min_actions
        self.max_actions = max_actions
        self.skills_file = self.storage_path / "skills.json"
        self._state_file = self.storage_path / "inducer_state.json"

        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Induction history: list of dicts recording each induction event
        self.induction_history: List[Dict[str, Any]] = []

        # Knowledge-base accessor
        self.knowledge_base = _KnowledgeBase(self)

        # Load existing skills
        self.skills = self._load_skills()
        
    def _load_skills(self) -> List[Skill]:
        """Load existing skills from storage."""
        if not self.skills_file.exists():
            return []
        
        try:
            with open(self.skills_file, 'r') as f:
                data = json.load(f)
            
            return [Skill.from_dict(skill_data) for skill_data in data.get('skills', [])]
        except Exception as e:
            logger.warning(f"Failed to load skills: {e}")
            return []
    
    def _save_skills(self) -> None:
        """Save skills to storage."""
        data = {
            'skills': [skill.to_dict() for skill in self.skills],
            'metadata': {
                'last_updated': datetime.now().isoformat(),
                'total_skills': len(self.skills),
                'total_tasks_processed': sum(skill.success_count for skill in self.skills)
            }
        }
        
        with open(self.skills_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {len(self.skills)} skills to {self.skills_file}")
    
    def extract_actions_from_trajectory(self, trajectory_data: Any) -> List[Dict[str, Any]]:
        """Extract action sequence from trajectory data.

        Handles three shapes:
          * a :class:`~polyskill.trajectory.Trajectory` (its ``.actions`` is a
            list of plain BrowserGym action strings),
          * legacy/protobuf-style objects whose ``.actions`` items expose an
            ``.action`` attribute,
          * a dict with an ``"actions"`` key (already list-of-dicts).
        """
        actions: List[Dict[str, Any]] = []

        if hasattr(trajectory_data, 'actions'):
            for action_data in trajectory_data.actions:
                # Trajectory.actions yields strings; protobuf yields objects.
                if isinstance(action_data, str):
                    if action_data.strip():
                        actions.append({'type': 'action', 'action': action_data, 'timestamp': 0})
                elif isinstance(action_data, dict):
                    a = action_data.get('action')
                    if a:
                        actions.append({'type': action_data.get('type', 'action'),
                                        'action': a,
                                        'timestamp': action_data.get('timestamp', 0)})
                elif hasattr(action_data, 'action') and action_data.action:
                    actions.append({
                        'type': 'action',
                        'action': action_data.action,
                        'timestamp': getattr(action_data, 'timestamp', 0),
                    })
        elif isinstance(trajectory_data, dict) and 'actions' in trajectory_data:
            # Dict-based trajectory
            actions = trajectory_data.get('actions', [])

        return actions
    
    def extract_skill_from_actions(
        self,
        actions: List[Dict[str, Any]],
        task: str
    ) -> Optional[Skill]:
        """Extract a skill from action sequence."""
        if len(actions) < self.min_actions or len(actions) > self.max_actions:
            return None
        
        # Simple pattern: take the first few meaningful actions
        meaningful_actions = []
        
        for action in actions[:self.max_actions]:
            if isinstance(action, dict):
                # Extract essential parts of the action
                action_type = action.get('type', 'unknown')
                action_content = action.get('action', '')
                
                # Skip empty or trivial actions
                if not action_content:
                    continue
                
                # Create a simplified pattern
                pattern_action = {
                    'type': action_type,
                    'action': action_content[:200]  # Limit length
                }
                meaningful_actions.append(pattern_action)
        
        if len(meaningful_actions) < self.min_actions:
            return None
        
        # Generate skill name based on actions and task
        skill_name = self._generate_skill_name(meaningful_actions, task)
        skill_id = f"skill_{len(self.skills) + 1:03d}"
        
        return Skill(
            id=skill_id,
            name=skill_name,
            pattern=meaningful_actions,
            task_examples=[task]
        )
    
    def _generate_skill_name(
        self,
        actions: List[Dict[str, Any]],
        task: str
    ) -> str:
        """Generate a descriptive name for the skill."""
        # Extract key words from actions
        action_types = []
        action_keywords = []
        
        for action in actions:
            action_str = str(action.get('action', '')).lower()
            
            # Common action patterns
            if 'click' in action_str:
                action_types.append('click')
            elif 'fill' in action_str or 'type' in action_str:
                action_types.append('fill')
            elif 'select' in action_str:
                action_types.append('select')
            elif 'navigate' in action_str or 'go' in action_str:
                action_types.append('navigate')
            
            # Extract potential element names
            if 'button' in action_str:
                action_keywords.append('button')
            elif 'form' in action_str or 'input' in action_str:
                action_keywords.append('form')
            elif 'menu' in action_str:
                action_keywords.append('menu')
        
        # Extract key words from task
        task_words = []
        task_lower = task.lower()
        if 'login' in task_lower:
            task_words.append('login')
        elif 'search' in task_lower:
            task_words.append('search')
        elif 'add' in task_lower or 'create' in task_lower:
            task_words.append('create')
        elif 'delete' in task_lower or 'remove' in task_lower:
            task_words.append('delete')
        
        # Combine to form skill name
        name_parts = []
        if action_types:
            name_parts.extend(action_types[:2])  # Max 2 action types
        if task_words:
            name_parts.extend(task_words[:1])   # Max 1 task word
        if action_keywords:
            name_parts.extend(action_keywords[:1])  # Max 1 keyword
        
        if name_parts:
            return '_'.join(name_parts)
        else:
            return f'pattern_{len(self.skills) + 1}'
    
    def induce_skill(
        self,
        trajectory_data: Any,
        task: str
    ) -> Optional[Skill]:
        """
        Main skill induction method.
        
        Args:
            trajectory_data: Trajectory data (protobuf or dict)
            task: Task description
            
        Returns:
            Induced skill or None
        """
        logger.info(f"Inducing skill from task: {task}")
        
        # Extract actions
        actions = self.extract_actions_from_trajectory(trajectory_data)
        if not actions:
            logger.warning("No actions found in trajectory")
            return None
        
        # Extract skill
        skill = self.extract_skill_from_actions(actions, task)
        if not skill:
            logger.info(f"No skill extracted (actions: {len(actions)})")
            return None
        
        # Check if similar skill already exists
        existing_skill = self._find_similar_skill(skill)
        if existing_skill:
            # Update existing skill
            existing_skill.success_count += 1
            if task not in existing_skill.task_examples:
                existing_skill.task_examples.append(task)
            logger.info(f"Updated existing skill: {existing_skill.name} (count: {existing_skill.success_count})")
            skill = existing_skill
        else:
            # Add new skill
            self.skills.append(skill)
            logger.info(f"Created new skill: {skill.name}")
        
        # Save skills
        self._save_skills()
        
        return skill
    
    def _find_similar_skill(self, new_skill: Skill) -> Optional[Skill]:
        """Find existing skill similar to the new one."""
        for existing_skill in self.skills:
            # Simple similarity: same number of actions and similar name
            if (len(existing_skill.pattern) == len(new_skill.pattern) and
                existing_skill.name == new_skill.name):
                return existing_skill
        return None
    
    def get_skills(self) -> List[Skill]:
        """Get all current skills."""
        return self.skills.copy()
    
    def _get_relevant_skills_by_overlap(self, task: str) -> List[Skill]:
        """Internal: word-overlap relevance filter (preserves original logic)."""
        relevant_skills = []
        task_lower = task.lower()

        for skill in self.skills:
            for example in skill.task_examples:
                example_lower = example.lower()
                task_words = set(task_lower.split())
                example_words = set(example_lower.split())
                overlap = task_words.intersection(example_words)
                if len(overlap) >= 2:
                    relevant_skills.append(skill)
                    break

        relevant_skills.sort(key=lambda s: s.success_count, reverse=True)
        return relevant_skills
    
    def export_skills_summary(self) -> str:
        """Export a summary of learned skills."""
        if not self.skills:
            return "No skills learned yet."

        summary = f"Learned Skills Summary ({len(self.skills)} skills):\n\n"

        for i, skill in enumerate(self.skills, 1):
            summary += f"{i}. {skill.name} (ID: {skill.id})\n"
            summary += f"   - Success count: {skill.success_count}\n"
            summary += f"   - Actions: {len(skill.pattern)}\n"
            summary += f"   - Task examples: {', '.join(skill.task_examples[:3])}\n"
            if len(skill.task_examples) > 3:
                summary += f"     ... and {len(skill.task_examples) - 3} more\n"
            summary += "\n"

        return summary

    # ------------------------------------------------------------------
    # Extended API for agent integration
    # ------------------------------------------------------------------

    def save_state(self) -> None:
        """Persist skills (via existing mechanism) and induction_history."""
        self._save_skills()
        state = {
            'induction_history': self.induction_history,
            'metadata': {
                'saved_at': datetime.now().isoformat()
            }
        }
        with open(self._state_file, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info(f"Saved inducer state to {self._state_file}")

    def load_state(self) -> None:
        """Load skills and induction_history from storage (no-op if absent)."""
        self.skills = self._load_skills()
        if not self._state_file.exists():
            return
        try:
            with open(self._state_file, 'r') as f:
                state = json.load(f)
            self.induction_history = state.get('induction_history', [])
            logger.info(f"Loaded inducer state ({len(self.induction_history)} history entries)")
        except Exception as e:
            logger.warning(f"Failed to load inducer state: {e}")

    def record_skill_usage(self, action: str, success: bool) -> None:
        """Increment usage/success counter on the skill whose name appears in *action*.

        Persists updated skills. Safe to call when no matching skill is found.
        """
        action_lower = action.lower()
        matched = False
        for skill in self.skills:
            if skill.name.lower() in action_lower:
                skill.success_count += (1 if success else 0)
                matched = True
                break
        if matched:
            self._save_skills()

    def induce_skills_from_agent_state(
        self,
        actions: List[str],
        task: str,
        success: bool
    ) -> Optional[Skill]:
        """Induce a skill from a list of action strings and a task description.

        Only induces when *success* is True.  Appends an entry to
        *induction_history* regardless of whether a skill was actually stored.

        Args:
            actions: Ordered list of action strings executed by the agent.
            task: Natural-language task description.
            success: Whether the task was completed successfully.

        Returns:
            The induced :class:`Skill` instance, or ``None``.
        """
        skill = None
        if success:
            # Convert plain strings into the dict format expected by
            # extract_skill_from_actions / induce_skill.
            trajectory_data = {
                'actions': [{'type': 'action', 'action': a} for a in actions]
            }
            skill = self.induce_skill(trajectory_data, task)

        self.induction_history.append({
            'task': task,
            'success': success,
            'actions_count': len(actions),
            'skill_induced': skill.name if skill else None,
            'timestamp': datetime.now().isoformat()
        })
        return skill

    def get_skills_for_task(self, task: str, max_skills: int = 5) -> List[Skill]:
        """Return up to *max_skills* stored skills relevant to *task*.

        Delegates to the existing word-overlap relevance logic; falls back to
        returning the most-recently-added (most-successful) skills when no
        overlap is found.
        """
        relevant = self.get_skills_relevant_to_task(task)
        if not relevant:
            # Fall back: return the most-used skills
            relevant = sorted(self.skills, key=lambda s: s.success_count, reverse=True)
        return relevant[:max_skills]

    def get_skills_relevant_to_task(self, task: str) -> List[Skill]:
        """Alias that replicates the original word-overlap relevance logic."""
        return self._get_relevant_skills_by_overlap(task)

    def export_skills_as_actions(self) -> str:
        """Return a Python source string containing a ``def`` for every skill.

        Each skill is represented as a function whose body documents the
        ordered action pattern.  Suitable for injecting into an agent prompt
        as executable pseudo-code.
        """
        if not self.skills:
            return "# No skills available\n"

        lines: List[str] = []
        for skill in self.skills:
            func_name = skill.name.replace('-', '_').replace(' ', '_')
            lines.append(f"def {func_name}():")
            lines.append(f'    """Skill {skill.id}: {skill.name} (used {skill.success_count}x)."""')
            for i, step in enumerate(skill.pattern, 1):
                action_str = step.get('action', '')
                lines.append(f"    # Step {i}: {action_str}")
            lines.append("")
        return "\n".join(lines)

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Return aggregate statistics about skills and induction history."""
        total_usage = sum(s.success_count for s in self.skills)
        return {
            'total_skills': len(self.skills),
            'total_inductions': len(self.induction_history),
            'successful_inductions': sum(
                1 for e in self.induction_history if e.get('success')
            ),
            'total_usage': total_usage,
            'average_usage_per_skill': (
                total_usage / len(self.skills) if self.skills else 0.0
            ),
            'storage_path': str(self.storage_path)
        }