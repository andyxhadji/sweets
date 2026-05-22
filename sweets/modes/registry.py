"""Mode auto-discovery and registry."""

import importlib
import pkgutil
from typing import Type

from sweets.modes.base import Mode

_registry: dict[str, Type[Mode]] = {}


def _discover_modes() -> None:
    """Scan modes package for Mode subclasses."""
    import sweets.modes as modes_package

    for _, module_name, _ in pkgutil.iter_modules(modes_package.__path__):
        if module_name in ("base", "registry"):
            continue

        module = importlib.import_module(f"sweets.modes.{module_name}")

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, Mode)
                and attr is not Mode
            ):
                _registry[attr.slug] = attr


def get_all_modes() -> dict[str, Type[Mode]]:
    """Return all discovered modes as {slug: ModeClass}."""
    if not _registry:
        _discover_modes()
    return _registry.copy()


def get_mode(slug: str) -> Mode:
    """Instantiate a mode by slug.

    Raises:
        KeyError: If mode slug not found
    """
    if not _registry:
        _discover_modes()

    if slug not in _registry:
        raise KeyError(f"Unknown mode: {slug}")

    return _registry[slug]()
