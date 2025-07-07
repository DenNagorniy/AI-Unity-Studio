"""Analytics agents package."""
from importlib import import_module

user_feedback = import_module("agents.analytics.user_feedback")
self_improver = import_module("agents.analytics.self_improver")
self_monitor = import_module("agents.analytics.self_monitor")
