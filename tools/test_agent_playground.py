import types
import sys

import agent_playground as ap


def test_load_agent(monkeypatch):
    module = types.SimpleNamespace(run=lambda x: {"ok": True})
    monkeypatch.setitem(sys.modules, "agents.tech.dummy", module)
    loaded = ap.load_agent("Dummy")
    assert loaded is module


def test_run_agent(monkeypatch):
    module = types.SimpleNamespace(run=lambda x: {"res": x.get("a")})
    monkeypatch.setitem(sys.modules, "agents.tech.simple", module)
    result = ap.run_agent("Simple", {"a": 1})
    assert result["res"] == 1
