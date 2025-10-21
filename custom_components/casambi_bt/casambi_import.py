"""Casambi import helpers with runtime adjustments."""

from __future__ import annotations

from collections.abc import MutableSequence
from importlib import import_module
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


def _patch_supported_versions(client_module: Any, target_version: int) -> None:
    """Attempt to patch CasambiBt so it understands ``target_version``."""

    patched_any = False

    for attr in dir(client_module):
        if "VERSION" not in attr.upper():
            continue

        try:
            current_value = getattr(client_module, attr)
        except AttributeError:  # pragma: no cover - defensive
            continue

        modified = False

        if isinstance(current_value, int):
            if current_value < target_version:
                setattr(client_module, attr, target_version)
                modified = True
        elif isinstance(current_value, range):
            if current_value.stop <= target_version:
                setattr(
                    client_module,
                    attr,
                    range(current_value.start, target_version + 1),
                )
                modified = True
        elif isinstance(current_value, tuple):
            if target_version not in current_value:
                setattr(client_module, attr, (*current_value, target_version))
                modified = True
        elif isinstance(current_value, MutableSequence):
            if target_version not in current_value:
                current_value.append(target_version)
                modified = True

        if modified:
            patched_any = True
            _LOGGER.debug(
                "Patched CasambiBt.%s to support network version %s", attr, target_version
            )

    if not patched_any:
        _LOGGER.debug(
            "No CasambiBt network version related attributes required patching."
        )


def _patch_casambi_version_support(target_version: int) -> None:
    """Ensure the CasambiBt library accepts the required network version."""

    try:
        client_module = import_module("CasambiBt._client")
    except ImportError:  # pragma: no cover - defensive
        _LOGGER.debug("Unable to import CasambiBt._client for version patching.")
        return

    _patch_supported_versions(client_module, target_version)


_patch_casambi_version_support(11)

from CasambiBt import (  # noqa: E402  # pylint: disable=wrong-import-position
    Casambi,
    ColorSource,
    Group,
    Scene,
    Unit,
    UnitControlType,
    UnitState,
    _operation,
)

__all__ = [
    "Casambi",
    "ColorSource",
    "Group",
    "Scene",
    "Unit",
    "UnitControlType",
    "UnitState",
    "_operation",
]
