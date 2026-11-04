"""The panel gets HA's restored settings once after setup."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from custom_components.ipixel_color import common


class _States:
    def __init__(self, states):
        self._s = states

    def get(self, entity_id):
        value = self._s.get(entity_id)
        return SimpleNamespace(state=value) if value is not None else None


def _setup(monkeypatch, auto, power):
    states = {"switch.auto": auto, "switch.power": power}
    hass = SimpleNamespace(states=_States(states))
    ids = {"auto_update": "switch.auto", "power": "switch.power"}
    monkeypatch.setattr(common, "get_entity_id_by_unique_id", lambda h, a, suffix, p=None: ids.get(suffix))
    calls = []

    async def fake_update(h, name, api, text=None):
        calls.append(name)
        return True

    monkeypatch.setattr(common, "update_ipixel_display", fake_update)
    return hass, SimpleNamespace(_address="AA"), calls


@pytest.mark.asyncio
async def test_pushes_when_auto_update_on(monkeypatch):
    hass, api, calls = _setup(monkeypatch, "on", "on")
    assert await common.restore_panel_display(hass, "Panel", api) is True
    assert calls == ["Panel"]


@pytest.mark.asyncio
@pytest.mark.parametrize("auto,power", [("off", "on"), (None, "on"), ("on", "off")])
async def test_skips_when_auto_update_off_or_power_off(monkeypatch, auto, power):
    hass, api, calls = _setup(monkeypatch, auto, power)
    assert await common.restore_panel_display(hass, "Panel", api) is False
    assert calls == []
