from importlib import import_module

# re-export most used tech agents
game_designer = import_module("agents.tech.game_designer")
project_manager = import_module("agents.tech.project_manager")
coder = import_module("agents.tech.coder")
tester = import_module("agents.tech.tester")
team_lead = import_module("agents.tech.team_lead")
