"""
Planning tools for AI coding projects.

This module contains planning-related MCP tool functions that can be
registered with an MCP server for project planning and task breakdown.
"""


def planning(prompt: str) -> str:
    return f"""
    Requirements: {prompt}

    ## Planning
    But I want you first to think deep and plan the project,
    **Parallel and small tasks** Then create multiple tasks that can be done simultaneously in parallel which means no tasks should have dependency to each others, and tasks should be small and limited to one file,
    **Readme and Tasks** Create a readme file that contains information about the project and tasks,
    **Coding Tool** For each tasks share the readme and dependency files needed to **code_with_multiple_ai** tool so it can has knowledge about it
    **Coding Tool** For coding simultaneously use **code_with_multiple_ai** but just run 4 tasks at same time, For coding just one file use **code_with_ai**
    **Coding Tool** which they are not depended on each others,

    **Task Branches** I suggest you to create takes branches, which each branch work on different part of the app and they have no dependency, then run tasks one by one from different branches together, (like task 1 of different branches at same time, then task 2 and ...)

    **Step by Step** Consider small tasks, and consider developing the app step by step,
    **Sprints** Which means, I need to have sprints,
    after each sprint we need to have a runnable game, and I want you to use browser tool to run it so we can see,
    for example sprint 1 can just load the game with nothing inside (but proper working)
    then sprint 2, we might have the bird that can jump, with no wall
    then sprint 3 we add the walls and movements
    ....
    **Runnable app** So all the time I can see the result.

    **Limitation of Coding tools** If you need to run any command line, use your command line tool, don't give command running to our coder it can't run commands, it can just code
    **Limitation of coding ** don't code yourself, even if you need to review and if you find something is wrong don't fix it yourself, ask **code_with_ai** to fix it
    **Rule file for repeated mistakes** If you found it is doing some mistakes all the time, then create a rule for it, and as part of prompt give it to it in next time run.
    **Interfaces for tasks** Also consider giving each task the methods and interfaces , method name, inputs and outputs, this way when they connect to each other they don't have issue

    **Load docs in context window** If there is any /docs or /doc folder or any readme or md file, be sure to read from it before you start
    """


# sdsd
def plan_from_scratch(prompt: str) -> str:
    return f"""
    Requirements: {prompt}

    ## Preparation
    Before start, you need to check for requirements and dependencies and technologies, then use Context7 MCP tool and get required information and save them in /docs folder and already read from them
    If there is any github repo mentioned in requirements, use command line tool to clone it in /docs folder and read from it

    ## Planning
    But I want you first to think deep and plan the project,
    **Parallel and small tasks** Then create multiple tasks that can be done simultaneously in parallel which means no tasks should have dependency to each others, and tasks should be small and limited to one file,
    **Readme and Tasks** Create a readme file that contains information about the project and tasks,
    **Coding Tool** For each tasks share the readme and dependency files needed to **code_with_multiple_ai** tool so it can has knowledge about it
    **Coding Tool** For coding simultaneously use **code_with_multiple_ai** but just run 4 tasks at same time, For coding just one file use **code_with_ai**
    **Coding Tool** which they are not depended on each others,

    **Task Branches** I suggest you to create takes branches, which each branch work on different part of the app and they have no dependency, then run tasks one by one from different branches together, (like task 1 of different branches at same time, then task 2 and ...)

    **Step by Step** Consider small tasks, and consider developing the app step by step,
    **Sprints** Which means, I need to have sprints,
    after each sprint we need to have a runnable game, and I want you to use browser tool to run it so we can see,
    for example sprint 1 can just load the game with nothing inside (but proper working)
    then sprint 2, we might have the bird that can jump, with no wall
    then sprint 3 we add the walls and movements
    ....
    **Runnable app** So all the time I can see the result.

    **Limitation of Coding tools** If you need to run any command line, use your command line tool, don't give command running to our coder it can't run commands, it can just code
    **Limitation of coding ** don't code yourself, even if you need to review and if you find something is wrong don't fix it yourself, ask **code_with_ai** to fix it
    **Rule file for repeated mistakes** If you found it is doing some mistakes all the time, then create a rule for it, and as part of prompt give it to it in next time run.
    **Interfaces for tasks** Also consider giving each task the methods and interfaces , method name, inputs and outputs, this way when they connect to each other they don't have issue

    **Load docs in context window** If there is any /docs or /doc folder or any readme or md file, be sure to read from it before you start
    """
