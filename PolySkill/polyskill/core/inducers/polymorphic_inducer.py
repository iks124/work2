"""
Polymorphic, Abstract-Class-First Skill Inducer (PolySkill paper, section 3.3).

This is the central contribution of the PolySkill paper. Rather than inducing a skill as an
isolated function, induction proceeds in two coupled steps:

1. Register / extend a per-domain abstract interface ``Abstract{Domain}Site`` with the new
   method SIGNATURE (and keep compositional skills, which dispatch over ``self``, on the
   abstract class).
2. Define the CONCRETE implementation of that method in a site-specific subclass
   ``{Site}(Abstract{Domain}Site)`` using BrowserGym primitives, grounded in a successful
   trajectory's actions.

The resulting skills are structurally consistent implementations of a shared domain concept,
which makes them composable and transferable across sites.
"""

import ast
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from ..base import (
    Skill, SkillType, SkillFormat, SkillInductionResult,
    SkillMetadata, TrajectoryExample,
)
from .llm_inducer import LLMBasedInducer, LLMInducerConfig
from ...prompts.induction.polymorphic import (
    POLYMORPHIC_SYSTEM_PROMPT,
    build_polymorphic_prompt,
    domain_to_class_name,
    site_to_class_name,
)

logger = logging.getLogger(__name__)


class PolymorphicInducer(LLMBasedInducer):
    """LLM-powered skill inducer that emits abstract-class-first polymorphic skills."""

    def __init__(self, config: LLMInducerConfig):
        super().__init__(config)
        # Prefer the polymorphic system prompt over the inherited default.
        self.system_prompt = POLYMORPHIC_SYSTEM_PROMPT

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------
    def build_induction_prompt(
        self,
        task: str,
        trajectory_actions: List[str],
        domain: str,
        site: str,
        abstract_methods: Optional[List[str]] = None,
    ) -> str:
        """Build the abstract-class-first induction prompt for a single trajectory."""
        return build_polymorphic_prompt(
            task=task,
            trajectory_actions=trajectory_actions,
            domain=domain,
            site=site,
            abstract_methods=abstract_methods,
        )

    # ------------------------------------------------------------------
    # Parsing the LLM output
    # ------------------------------------------------------------------
    def _split_abstract_and_concrete(self, llm_code: str) -> Tuple[str, str, str]:
        """Split LLM output into (abstract_src, concrete_src, method_name).

        Robust to surrounding prose: a ```python``` fenced block is extracted first.
        The class WITHOUT a base (or named ``Abstract*``) is the abstract interface; the
        class WITH a base is the concrete subclass. ``method_name`` is the first non-dunder
        method defined in the concrete subclass.

        Raises:
            ValueError: if the abstract or concrete class cannot be located, or the concrete
                subclass defines no usable method.
        """
        code = self._extract_python_code(llm_code)

        try:
            module = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Could not parse LLM code as Python: {e}") from e

        class_defs = [n for n in module.body if isinstance(n, ast.ClassDef)]
        if not class_defs:
            raise ValueError("No class definitions found in LLM output")

        abstract_node: Optional[ast.ClassDef] = None
        concrete_node: Optional[ast.ClassDef] = None

        for node in class_defs:
            # Concrete subclass = a class whose base is a domain interface (Abstract*).
            # Abstract interface = the class without such a base (typically no base, or ABC).
            if _has_abstract_base(node):
                if concrete_node is None:
                    concrete_node = node
            elif abstract_node is None:
                abstract_node = node

        # Fallbacks for ambiguous output: classify by name / presence of any base.
        if abstract_node is None:
            for node in class_defs:
                if node is not concrete_node and node.name.startswith("Abstract"):
                    abstract_node = node
                    break
        if abstract_node is None:
            for node in class_defs:
                if node is not concrete_node and not node.bases:
                    abstract_node = node
                    break
        if concrete_node is None:
            for node in class_defs:
                if node is not abstract_node and node.bases:
                    concrete_node = node
                    break

        if abstract_node is None:
            raise ValueError("Could not locate the abstract interface class")
        if concrete_node is None:
            raise ValueError("Could not locate the concrete subclass")

        abstract_src = ast.get_source_segment(code, abstract_node) or ""
        concrete_src = ast.get_source_segment(code, concrete_node) or ""

        method_name = _first_public_method(concrete_node)
        if not method_name:
            raise ValueError("Concrete subclass defines no public method")

        return abstract_src, concrete_src, method_name

    def _extract_python_code(self, text: str) -> str:
        """Extract the python source from an LLM response.

        Prefers the inherited fenced-block extractor; if no fence is present, falls back to
        treating the whole text (from the first ``class`` keyword) as code.
        """
        blocks = self._extract_code_blocks(text)
        if blocks:
            # Prefer a block that actually defines a class.
            for block in blocks:
                if "class " in block:
                    return block
            return blocks[0]
        # No fence: try to salvage from the first class definition onward.
        idx = text.find("class ")
        if idx != -1:
            return text[idx:]
        return text

    # ------------------------------------------------------------------
    # Induction
    # ------------------------------------------------------------------
    def induce(
        self,
        task: str,
        trajectory_actions: List[str],
        domain: str,
        site: str,
        abstract_methods: Optional[List[str]] = None,
    ) -> Optional[Skill]:
        """Induce a single polymorphic skill from a successful trajectory.

        Returns a :class:`Skill` (skill_type CODE) whose content is the concrete method
        source, or ``None`` if generation/parsing fails.
        """
        prompt = self.build_induction_prompt(
            task=task,
            trajectory_actions=trajectory_actions,
            domain=domain,
            site=site,
            abstract_methods=abstract_methods,
        )

        responses = self._generate_polymorphic_responses(prompt)
        if not responses:
            self.logger.warning("Polymorphic induction: LLM returned no responses")
            return None

        abstract_class = domain_to_class_name(domain)
        concrete_class = site_to_class_name(site)

        for response in responses:
            try:
                abstract_src, concrete_src, method_name = self._split_abstract_and_concrete(response)
            except ValueError as e:
                self.logger.warning(f"Polymorphic induction: failed to split response: {e}")
                continue

            description = self._extract_method_docstring(abstract_src, method_name) or task

            skill = Skill(
                id=f"poly_{site_to_class_name(site)}_{method_name}",
                name=method_name,
                skill_type=SkillType.CODE,
                format=SkillFormat.PYTHON_FUNCTION,
                content=concrete_src,
                description=description,
                task_examples=[task],
                metadata=SkillMetadata(
                    source=self.__class__.__name__,
                    tags=["polymorphic", "concrete", domain, site],
                ),
            )
            # Stash the abstract interface alongside the concrete skill for persistence/reuse.
            skill.metadata.tags = list(skill.metadata.tags)
            skill_metadata_extra = {
                "domain": domain,
                "site": site,
                "abstract_class": abstract_class,
                "concrete_class": concrete_class,
                "abstract_source": abstract_src,
                "method_name": method_name,
            }
            skill.metadata.extra = skill_metadata_extra
            return skill

        self.logger.warning("Polymorphic induction: no response could be parsed into a skill")
        return None

    def _generate_polymorphic_responses(self, prompt: str) -> List[str]:
        """Call the configured LLM with the polymorphic system prompt + user prompt."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]
        responses: List[str] = []

        if self.llm_client is None:
            self.logger.error("Polymorphic induction: no LLM client available")
            return responses

        try:
            if hasattr(self.llm_client, "generate"):  # FoundationModel
                out = self.llm_client.generate(
                    messages=messages,
                    max_tokens=self.llm_config.max_tokens,
                    temperature=self.llm_config.temperature,
                )
                if isinstance(out, list):
                    responses.extend(out)
                else:
                    responses.append(out)
            elif hasattr(self.llm_client, "completion"):  # litellm module
                resp = self.llm_client.completion(
                    model=self.llm_config.model_name,
                    messages=messages,
                    temperature=self.llm_config.temperature,
                    max_tokens=self.llm_config.max_tokens,
                )
                responses.append(resp.choices[0].message.content)
        except Exception as e:
            self.logger.error(f"Polymorphic induction: LLM call failed: {e}")
            raise

        return responses

    @staticmethod
    def _extract_method_docstring(abstract_src: str, method_name: str) -> Optional[str]:
        """Pull the docstring of ``method_name`` from the abstract class source, if present."""
        if not abstract_src:
            return None
        try:
            module = ast.parse(abstract_src)
        except SyntaxError:
            return None
        for node in ast.walk(module):
            if isinstance(node, ast.FunctionDef) and node.name == method_name:
                doc = ast.get_docstring(node)
                if doc:
                    return doc.strip()
        return None

    # ------------------------------------------------------------------
    # BaseSkillInducer interface
    # ------------------------------------------------------------------
    def extract_skills(
        self,
        trajectories: List[Union[Dict[str, Any], TrajectoryExample]],
        task_context: Optional[str] = None,
    ) -> SkillInductionResult:
        """Induce one polymorphic skill per trajectory (thin wrapper over :meth:`induce`).

        Domain/site are read from each trajectory's metadata (keys ``domain``/``site``),
        defaulting to a generic ``web`` domain / the trajectory's task id as site.
        """
        result = SkillInductionResult(success=True)

        if not trajectories:
            result.add_error("No trajectories provided")
            return result

        for traj in trajectories:
            if isinstance(traj, dict):
                traj = self._dict_to_trajectory_example(traj)
            if not traj:
                continue

            metadata = traj.metadata or {}
            domain = metadata.get("domain", "web")
            site = metadata.get("site", traj.task_id or "site")
            task = task_context or traj.goal

            action_strings = [
                a.get("action", "") for a in traj.actions if a.get("action")
            ]

            try:
                skill = self.induce(
                    task=task,
                    trajectory_actions=action_strings,
                    domain=domain,
                    site=site,
                )
            except Exception as e:
                self.logger.error(f"Polymorphic extract_skills failed: {e}")
                skill = None

            if skill is not None:
                result.skills.append(skill)

        valid = self.validate_skills(result.skills)
        result.skills = valid
        if not result.skills:
            result.add_error("No valid polymorphic skills induced")
        return result


def _has_abstract_base(node: ast.ClassDef) -> bool:
    """True if *node* subclasses a domain interface (an ``Abstract*`` base).

    This marks *node* as a true concrete subclass (`Site(AbstractFooSite)`), as opposed to an
    abstract class that merely subclasses `ABC` / `object`.
    """
    for base in node.bases:
        name = _base_name(base)
        if name and name.startswith("Abstract"):
            return True
    return False


def _base_name(base: ast.expr) -> Optional[str]:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    return None


def _first_public_method(node: ast.ClassDef) -> Optional[str]:
    """Return the name of the first non-dunder method defined directly in *node*."""
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not (item.name.startswith("__") and item.name.endswith("__")):
                return item.name
    return None
