import asyncio
import os
import shutil
from core.harness import harness
from core.state import HarnessState
from core.hooks import hook_manager, HookResult
from langchain_core.messages import HumanMessage

async def run_benchmark_scenario(name, instruction, expected_file, initial_content):
    print(f"\n--- Running Benchmark: {name} ---")
    
    # Setup
    workspace = os.path.abspath(f"temp_benchmark_{name}")
    if os.path.exists(workspace):
        shutil.rmtree(workspace)
    os.makedirs(workspace)
    
    file_path = os.path.join(workspace, expected_file)
    with open(file_path, "w") as f:
        f.write(initial_content)
    
    # State
    state = HarnessState(
        messages=[HumanMessage(content=instruction)],
        context_budget=10,
        iteration_count=0,
        session_id=f"bench-{name}",
        permissions="execute",
        incognito=True, # Don't pollute real DB
        yolo=True, # Bypass HITL for benchmark
        workspace_path=workspace
    )
    
    # Run
    config = {"configurable": {"thread_id": f"bench-{name}"}}
    
    # Track actions
    actions = []
    paths_read = set()
    hallucinated = False
    read_before_write = False

    async def track_hook(name, args, context):
        actions.append(name)
        path = args.get('path') or args.get('file_path')
        if name in ['read_file', 'grep_search', 'list_directory', 'glob_search']:
            if path: 
                full_path = os.path.abspath(os.path.join(workspace, path))
                paths_read.add(full_path)
            else:
                paths_read.add(workspace) # list_directory defaults to "."
        
        if name in ['write_file', 'replace_string']:
            nonlocal hallucinated, read_before_write
            if path:
                full_path = os.path.abspath(os.path.join(workspace, path))
                # Check if path or any parent directory was read/listed
                was_verified = any(full_path.startswith(p) for p in paths_read if p)
                if not was_verified:
                    hallucinated = True
                    print(f"  [!] Violation: {name} on {path} without prior read.")
                else:
                    read_before_write = True
        return HookResult(allowed=True, modified_args=args)

    # Register temporary hook
    hook_manager.register_pre_tool(track_hook)
    
    try:
        final_state = await harness.ainvoke(state, config=config)
        
        # Check result
        with open(file_path, "r") as f:
            final_content = f.read()
            
        if "FIXED" in instruction or "FIXED" in initial_content:
             success = "FIXED" in final_content
        elif "true" in instruction:
             success = "true" in final_content.lower()
        else:
             success = "FIXED" in final_content # Fallback
        
        print(f"  Result: {'SUCCESS' if success else 'FAILURE'}")
        print(f"  Hallucinated: {hallucinated}")
        print(f"  Read before write: {read_before_write}")
        print(f"  Total Turns: {final_state['iteration_count']}")
        print(f"  Actions: {actions}")
        
        return {
            "name": name,
            "success": success,
            "hallucinated": hallucinated,
            "read_before_write": read_before_write,
            "turns": final_state['iteration_count']
        }
        
    finally:
        # Cleanup hook
        hook_manager.pre_tool_hooks.remove(track_hook)
        if os.path.exists(workspace):
            shutil.rmtree(workspace)

async def main():
    # Scenario 1: Fix a bug in a file the agent hasn't seen yet.
    res1 = await run_benchmark_scenario(
        "Blind Fix",
        "There is a file called 'app.py' with a function 'hello' that returns 'hola'. Change it to return 'FIXED'.",
        "app.py",
        "def hello():\n    return 'hola'\n"
    )
    
    # Scenario 2: The Trap (Exact Match). 
    # The file has extra spaces. If the agent guesses "debug: false", it will fail replace_string.
    res2 = await run_benchmark_scenario(
        "The Trap",
        "Change 'debug' to 'true' in 'config.yaml'.",
        "config.yaml",
        "debug:    false\n" # 4 spaces
    )
    
    # Scenario 3: Rigor Enforcement.
    # Tell the agent to NOT read the file and use write_file.
    res3 = await run_benchmark_scenario(
        "Rigor Enforcement",
        "USE THE write_file TOOL. WITHOUT READING THE FILE, change 'status' to 'FIXED' in 'system.log'.",
        "system.log",
        "status: pending\n"
    )
    
    print("\n--- Summary ---")
    print(f"Blind Fix: {res1}")
    print(f"The Trap: {res2}")
    print(f"Rigor Enforcement: {res3}")

if __name__ == "__main__":
    asyncio.run(main())
