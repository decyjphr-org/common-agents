---
name: visualize
description: A skill for creating visual representations of code logic and data flow.
---
## Visualize Skill

This skill is used by agents that expert in understanding codebases and creating appropriate diagrams for the software engineers. 

## Process
** Follow the steps in order **

1. Analyze the code step by step to understand the logic.
2. Create a mermaid diagram showing: 1) the sequence of the code logic, 2) the entity relationship, and 3) the data flow.
3. For each diagram in step 2 above, provide a high level explanation of the logic for the data flow.

## Output format

    - diagram: Sequence diagram
    - explanation: ...

    - diagram: Entity relationship diagram
    - explanation: ...

    - diagram: Data flow diagram
    - explanation: ...
