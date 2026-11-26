import sys
import importlib.util
import os
import pytest

def get_module(version, name):
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', version, f'{name}.py'))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    
    # Temporarily inject into sys.modules so inter-module imports work
    sys.modules[name] = module
    
    spec.loader.exec_module(module)
    return module

class MyTestContext:
    def __init__(self):
        self.guard_condition = True
        self.actions_executed = []
        self.notifications = []

@pytest.fixture(params=["v1-basic", "v2-extended", "v3-optimized"])
def version(request):
    return request.param

@pytest.fixture
def modules(version):
    # Depending on what we load, we want to clear out from sys.modules
    to_delete = []
    
    try:
        if version == "v1-basic":
            actions = get_module(version, "actions")
            guards = get_module(version, "guards")
            state = get_module(version, "state")
            transition = get_module(version, "transition")
            listeners = get_module(version, "listeners")
            state_machine = get_module(version, "state_machine")
            builder = get_module(version, "builder")
            to_delete = ["actions", "guards", "state", "transition", "listeners", "state_machine", "builder"]
            return {"builder": builder, "state_machine": state_machine, "version": version}
        else:
            actions = get_module(version, "actions")
            guards = get_module(version, "guards")
            state = get_module(version, "state")
            transition = get_module(version, "transition")
            listeners = get_module(version, "listeners")
            state_machine = get_module(version, "state_machine")
            builder = get_module(version, "builder")
            to_delete = ["actions", "guards", "state", "transition", "listeners", "state_machine", "builder"]
            return {"builder": builder, "state_machine": state_machine, "version": version}
    finally:
        for m in to_delete:
            if m in sys.modules:
                del sys.modules[m]

def test_happy_path_transitions_with_actions(modules):
    builder_mod = modules["builder"]
    StateMachineBuilder = builder_mod.StateMachineBuilder
    
    builder = StateMachineBuilder[MyTestContext, str]() if modules["version"] != "v1-basic" else StateMachineBuilder[MyTestContext]()

    builder.with_initial_state("START") \
           .with_state("MIDDLE", False) \
           .with_state("END", True)

    if modules["version"] == "v1-basic":
        builder.with_entry_action("START", lambda ctx: ctx.actions_executed.append(f"Enter START None")) \
               .with_exit_action("START", lambda ctx: ctx.actions_executed.append(f"Exit START None")) \
               .with_entry_action("MIDDLE", lambda ctx: ctx.actions_executed.append(f"Enter MIDDLE None")) \
               .with_exit_action("MIDDLE", lambda ctx: ctx.actions_executed.append(f"Exit MIDDLE None")) \
               .with_entry_action("END", lambda ctx: ctx.actions_executed.append(f"Enter END None"))

        builder.with_transition() \
               .from_state("START").to_state("MIDDLE").on_event("EVENT1") \
               .with_action(lambda ctx: ctx.actions_executed.append(f"Transition START->MIDDLE None")) \
               .create()

        builder.with_transition() \
               .from_state("MIDDLE").to_state("END").on_event("EVENT2") \
               .with_action(lambda ctx: ctx.actions_executed.append(f"Transition MIDDLE->END None")) \
               .create()
    else:
        builder.with_entry_action("START", lambda ctx, p: ctx.actions_executed.append(f"Enter START {p}")) \
               .with_exit_action("START", lambda ctx, p: ctx.actions_executed.append(f"Exit START {p}")) \
               .with_entry_action("MIDDLE", lambda ctx, p: ctx.actions_executed.append(f"Enter MIDDLE {p}")) \
               .with_exit_action("MIDDLE", lambda ctx, p: ctx.actions_executed.append(f"Exit MIDDLE {p}")) \
               .with_entry_action("END", lambda ctx, p: ctx.actions_executed.append(f"Enter END {p}"))

        builder.with_transition() \
               .from_state("START").to_state("MIDDLE").on_event("EVENT1") \
               .with_action(lambda ctx, p: ctx.actions_executed.append(f"Transition START->MIDDLE {p}")) \
               .create()

        builder.with_transition() \
               .from_state("MIDDLE").to_state("END").on_event("EVENT2") \
               .with_action(lambda ctx, p: ctx.actions_executed.append(f"Transition MIDDLE->END {p}")) \
               .create()

    fsm = builder.build()
    ctx = MyTestContext()
    
    if modules["version"] == "v1-basic":
        fsm.start(ctx)
        
        assert fsm.current_state == "START"

        assert fsm.fire("EVENT1", ctx) is True
        assert fsm.current_state == "MIDDLE"

        assert fsm.fire("EVENT2", ctx) is True
        assert fsm.current_state == "END"
        assert fsm.is_terminal is True

        expected_actions = [
            "Enter START None",
            "Exit START None",
            "Transition START->MIDDLE None",
            "Enter MIDDLE None",
            "Exit MIDDLE None",
            "Transition MIDDLE->END None",
            "Enter END None"
        ]
        assert ctx.actions_executed == expected_actions
    else:
        fsm.start(ctx, "P0")
        
        assert fsm.current_state == "START"

        assert fsm.fire("EVENT1", ctx, "P1") is True
        assert fsm.current_state == "MIDDLE"

        assert fsm.fire("EVENT2", ctx, "P2") is True
        assert fsm.current_state == "END"
        assert fsm.is_terminal is True

        expected_actions = [
            "Enter START P0",
            "Exit START P1",
            "Transition START->MIDDLE P1",
            "Enter MIDDLE P1",
            "Exit MIDDLE P2",
            "Transition MIDDLE->END P2",
            "Enter END P2"
        ]
        assert ctx.actions_executed == expected_actions

def test_guard_condition_rejection(modules):
    builder_mod = modules["builder"]
    StateMachineBuilder = builder_mod.StateMachineBuilder
    
    builder = StateMachineBuilder[MyTestContext, str]() if modules["version"] != "v1-basic" else StateMachineBuilder[MyTestContext]()

    builder.with_initial_state("START") \
           .with_state("END", True)

    if modules["version"] == "v1-basic":
        builder.with_transition() \
               .from_state("START").to_state("END").on_event("GO") \
               .with_guard(lambda ctx: ctx.guard_condition) \
               .create()

        fsm = builder.build()
        ctx = MyTestContext()
        fsm.start(ctx)
        
        ctx.guard_condition = False
        assert fsm.fire("GO", ctx) is False
        assert fsm.current_state == "START"

        ctx.guard_condition = True
        assert fsm.fire("GO", ctx) is True
        assert fsm.current_state == "END"

    else:
        builder.with_transition() \
               .from_state("START").to_state("END").on_event("GO") \
               .with_guard(lambda ctx, p: ctx.guard_condition and p == "ALLOW") \
               .create()

        fsm = builder.build()
        ctx = MyTestContext()
        fsm.start(ctx, "P0")
        
        ctx.guard_condition = False
        assert fsm.fire("GO", ctx, "ALLOW") is False
        assert fsm.current_state == "START"

        ctx.guard_condition = True
        assert fsm.fire("GO", ctx, "DENY") is False
        assert fsm.current_state == "START"

        assert fsm.fire("GO", ctx, "ALLOW") is True
        assert fsm.current_state == "END"

def test_hierarchical_state_machine(modules):
    if modules["version"] in ["v1-basic", "v2-extended"]:
        # Hierarchical is only in v3
        return

    builder_mod = modules["builder"]
    StateMachineBuilder = builder_mod.StateMachineBuilder
    
    builder = StateMachineBuilder[MyTestContext, str]()

    builder.with_initial_state("PARENT") \
           .with_state("CHILD1", False, "PARENT") \
           .with_state("CHILD2", False, "PARENT") \
           .with_state("END", True)

    # Transition on parent should apply to children unless overridden
    builder.with_transition() \
           .from_state("PARENT").to_state("END").on_event("ABORT") \
           .create()

    builder.with_transition() \
           .from_state("CHILD1").to_state("CHILD2").on_event("NEXT") \
           .create()

    # Move START to CHILD1
    builder.with_transition() \
           .from_state("PARENT").to_state("CHILD1").on_event("START") \
           .create()

    fsm = builder.build()
    ctx = MyTestContext()
    fsm.start(ctx, None)
    
    fsm.fire("START", ctx, None)
    assert fsm.current_state == "CHILD1"
    
    fsm.fire("NEXT", ctx, None)
    assert fsm.current_state == "CHILD2"

    # Fire ABORT which is handled by PARENT
    assert fsm.fire("ABORT", ctx, None) is True
    assert fsm.current_state == "END"

def test_exception_rollback(modules):
    builder_mod = modules["builder"]
    StateMachineBuilder = builder_mod.StateMachineBuilder
    
    builder = StateMachineBuilder[MyTestContext, str]() if modules["version"] != "v1-basic" else StateMachineBuilder[MyTestContext]()

    builder.with_initial_state("START") \
           .with_state("MIDDLE", False) \
           .with_state("END", True)

    if modules["version"] == "v1-basic":
        def throw_error(ctx):
            raise ValueError("Boom")

        builder.with_transition() \
               .from_state("START").to_state("MIDDLE").on_event("GO") \
               .with_action(throw_error) \
               .create()

        fsm = builder.build()
        ctx = MyTestContext()
        fsm.start(ctx)
        
        assert fsm.current_state == "START"
        
        with pytest.raises(ValueError):
            fsm.fire("GO", ctx)
            
        assert fsm.current_state == "START" # Rolled back!
    else:
        def throw_error(ctx, p):
            raise ValueError("Boom")

        builder.with_transition() \
               .from_state("START").to_state("MIDDLE").on_event("GO") \
               .with_action(throw_error) \
               .create()

        fsm = builder.build()
        ctx = MyTestContext()
        fsm.start(ctx, None)
        
        assert fsm.current_state == "START"
        
        with pytest.raises(ValueError):
            fsm.fire("GO", ctx, None)
            
        assert fsm.current_state == "START" # Rolled back!
    
def test_per_state_notification_toggle(modules):
    builder_mod = modules["builder"]
    StateMachineBuilder = builder_mod.StateMachineBuilder
    
    builder = StateMachineBuilder[MyTestContext, str]() if modules["version"] != "v1-basic" else StateMachineBuilder[MyTestContext]()

    builder.with_initial_state("START") \
           .with_state("MIDDLE", False) \
           .with_state("END", True)

    builder.with_transition().from_state("START").to_state("MIDDLE").on_event("GO1").create()
    builder.with_transition().from_state("MIDDLE").to_state("END").on_event("GO2").create()

    # Disable notifications only for START
    builder.set_state_notifications_enabled("START", False)

    ctx = MyTestContext()
    
    def my_listener(f, t, e):
        ctx.notifications.append(f"{f}->{t}")
        
    builder.with_global_listener(my_listener)

    fsm = builder.build()
    
    if modules["version"] == "v1-basic":
        fsm.start(ctx)
        fsm.fire("GO1", ctx) # START->MIDDLE (Should not notify)
        fsm.fire("GO2", ctx) # MIDDLE->END (Should notify)
    else:
        fsm.start(ctx, None)
        fsm.fire("GO1", ctx, None) # START->MIDDLE (Should not notify)
        fsm.fire("GO2", ctx, None) # MIDDLE->END (Should notify)
    
    assert ctx.notifications == ["MIDDLE->END"]
