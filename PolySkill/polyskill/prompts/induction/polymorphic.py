"""
Prompts for polymorphic, abstract-class-first skill induction (PolySkill paper section 3.3).

The mechanism: instead of inducing a skill as an isolated function, induction first
registers a method SIGNATURE on a per-domain abstract interface ``Abstract{Domain}Site``,
THEN defines the concrete implementation in a site-specific subclass. This yields skills
that are structurally consistent implementations of a shared domain concept; compositional
skills (that compose other skills) live ONLY on the abstract class and rely on polymorphic
dispatch.
"""

from typing import List, Optional


# Domain-id -> abstract class name. Title-case fallback applies for unmapped domains.
_DOMAIN_CLASS_MAP = {
    "shopping": "AbstractShoppingSite",
    "dev_tools": "AbstractDevPlatform",
}


def domain_to_class_name(domain: str) -> str:
    """Map a domain id to its abstract interface class name.

    Known domains use a curated mapping; otherwise a title-cased fallback of the
    form ``Abstract<TitleCasedDomain>Site`` is produced.
    """
    if not domain:
        return "AbstractWebSite"
    key = domain.strip().lower()
    if key in _DOMAIN_CLASS_MAP:
        return _DOMAIN_CLASS_MAP[key]
    # Title-case fallback: split on non-alphanumerics, CamelCase the pieces.
    parts = [p for p in _split_identifier(domain) if p]
    camel = "".join(p[:1].upper() + p[1:].lower() for p in parts)
    return f"Abstract{camel}Site"


def site_to_class_name(site: str) -> str:
    """Map a site id to a CamelCase concrete subclass name (e.g. ``webarena_shopping`` -> ``WebarenaShopping``)."""
    if not site:
        return "ConcreteSite"
    parts = [p for p in _split_identifier(site) if p]
    return "".join(p[:1].upper() + p[1:].lower() for p in parts)


def _split_identifier(text: str) -> List[str]:
    """Split an id like ``webarena_shopping`` / ``dev-tools`` / ``MySite`` into word pieces."""
    import re
    # Split on underscores, hyphens, spaces, dots.
    rough = re.split(r"[_\-\s\.]+", text.strip())
    pieces: List[str] = []
    for chunk in rough:
        if not chunk:
            continue
        # Further split camelCase / PascalCase boundaries.
        pieces.extend(re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z0-9]+|[A-Z]+|[0-9]+", chunk) or [chunk])
    return pieces


POLYMORPHIC_SYSTEM_PROMPT = """You are an expert at building reusable, polymorphic skill libraries for web automation agents.

You design skills using an ABSTRACT-CLASS-FIRST pattern:
1. Every web domain (e.g. shopping, dev tools) has a single abstract interface class, named
   `Abstract{Domain}Site`, that declares method SIGNATURES with docstrings — one per atomic
   skill — plus COMPOSITIONAL skills whose bodies call other methods via `self` (polymorphic
   dispatch). Compositional skills are defined ONLY on the abstract class.
2. Each concrete website is a subclass `{Site}(Abstract{Domain}Site)` that IMPLEMENTS the
   atomic method signatures using BrowserGym primitives. Concrete subclasses never redefine
   compositional skills — they inherit them.

BrowserGym primitives you may use inside concrete method bodies:
  click(bid)              # click the element with the given browsergym bid
  fill(bid, value)        # type `value` into the element with the given bid
  keyboard_press(key)     # press a keyboard key, e.g. 'Enter'
  select(bid, option)     # select an option in a dropdown

Rules:
- Output exactly ONE python code block (```python ... ```).
- The block must contain the abstract class (declaring the new method signature + a concise
  docstring, keeping any compositional skills on the abstract class) FIRST, then the concrete
  subclass implementing that ONE new method using the primitives derived from the trajectory.
- Use clear, snake_case method names and typed parameters. Generalize literal values from the
  trajectory into method parameters where it makes sense (e.g. a typed query string).
- Do NOT invent unrelated methods. Implement exactly the one skill demonstrated by the trajectory."""


_FEW_SHOT_EXAMPLE = '''Worked example (domain="shopping", site="amazon"):

```python
class AbstractShoppingSite:
    def search_product(self, query: str):
        """Searches for a product."""
    def add_to_cart(self, item_id: str, quantity: int):
        """Adds a specified item to the shopping cart."""
    def checkout(self):
        """Initiates the checkout process."""
    # Compositional skills (defined ONLY here; rely on polymorphic dispatch)
    def find_and_add_to_cart(self, query: str, item_id: str):
        self.search_product(query); self.add_to_cart(item_id)
    def purchase_item(self, query: str, item_id: str):
        self.find_and_add_to_cart(query, item_id); self.checkout()

class AmazonWebsite(AbstractShoppingSite):
    def search_product(self, query: str):
        click(search_bar_id); fill(search_bar_id, query); keyboard_press('Enter')
    def add_to_cart(self, item_id: str, quantity: int):
        click(add_to_cart_button_id)
    def checkout(self):
        self.view_cart(); click(checkout_button_id)
```'''


def build_polymorphic_prompt(
    task: str,
    trajectory_actions: List[str],
    domain: str,
    site: str,
    abstract_methods: Optional[List[str]] = None,
) -> str:
    """Build the user prompt instructing the model to emit an abstract-class-first skill.

    Args:
        task: Natural-language goal of the successful trajectory.
        trajectory_actions: Ordered BrowserGym-style action strings from the trajectory.
        domain: Domain id (e.g. "shopping"); maps to the abstract interface class.
        site: Site id (e.g. "webarena_shopping"); maps to the concrete subclass name.
        abstract_methods: Names of method signatures already on the abstract interface,
            so the model can extend (rather than reduplicate) the interface.

    Returns:
        A fully formatted user prompt string.
    """
    abstract_class = domain_to_class_name(domain)
    concrete_class = site_to_class_name(site)
    abstract_methods = abstract_methods or []

    actions_block = "\n".join(f"    {a}" for a in trajectory_actions) or "    (no actions)"
    if abstract_methods:
        existing = ", ".join(abstract_methods)
        existing_block = (
            f"The abstract interface `{abstract_class}` already declares these method "
            f"signatures: {existing}.\n"
            "Extend the interface only if the new skill is genuinely new; otherwise implement "
            "an existing signature in the concrete subclass.\n"
        )
    else:
        existing_block = (
            f"The abstract interface `{abstract_class}` has no methods yet; declare the new "
            "signature on it.\n"
        )

    return f"""{_FEW_SHOT_EXAMPLE}

Now induce a polymorphic skill for the following SUCCESSFUL trajectory.

Domain: {domain}  ->  abstract interface class: `{abstract_class}`
Site:   {site}  ->  concrete subclass: `{concrete_class}({abstract_class})`

Task goal:
    {task}

Successful trajectory actions (BrowserGym primitives, in order):
{actions_block}

{existing_block}
Produce exactly ONE ```python``` block with:
1. `class {abstract_class}:` declaring the new method's signature + a one-line docstring
   describing the domain-level intent (keep any compositional skills on this class).
2. `class {concrete_class}({abstract_class}):` implementing that ONE method concretely from the
   trajectory actions above, using the BrowserGym primitives.
"""
