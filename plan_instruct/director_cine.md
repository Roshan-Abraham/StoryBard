# Director and Cinematographer Assistant (Detailed Version)

## Program Plan for Scene Structuring and Visual Execution

### Main Objective
To prepare story scripts for cinematic execution by organizing scenes within acts, creating detailed plot sequences, and defining how each scene is visually captured. This includes maintaining narrative consistency, visual coherence, and ensuring the storytelling aligns with audience expectations.

### Key Goals
1. **Scene Structuring and Management:** Organize scenes into acts and sequences, ensuring logical transitions and narrative pacing.
2. **Detailed Visual Planning:** Provide detailed shot lists, including shot types, angles, lighting, and transitions.
3. **Narrative Consistency Tracking:** Track and maintain consistency across scenes, ensuring alignment with plot and character development.
4. **Viewer Information Flow Management:** Design strategies to control when and how information is revealed to viewers.
5. **Exportable Scene Documents:** Create detailed documents to guide production, including headers, footers, and technical notes.

---

### Tools and Actions

#### **RAG Tools**
- **LangGraph Framework:** For mapping scene dependencies, shot sequences, and visual elements.
- **Cinematography Libraries:** For standard practices in lighting, camera setups, and framing.
- **Database Reference:** To store and track scene, shot, and viewer information data.

#### **Actions**
- **File Operations:** Writing and exporting scene documents in required formats.
- **Database Queries:** Fetching and updating data for scenes, shots, and consistency checks.
- **API Calls:** Invoking functions or external APIs for cinematic notes or diagram generation.
- **Validation Functions:** Ensuring consistency across visual and narrative elements.
- **Visualization Functions:** Generating graphs or diagrams for production planning.

---

### Modules and Functional Components

#### 1. **Scene Structuring Module**
   - Parse scripts into individual scenes and group them into acts.
   - Assign headers (e.g., INT./EXT., location, time of day) and footers (transition notes).

#### 2. **Shot Planning Engine**
   - Define:
     - **Shot Types:** Wide shot, close-up, medium shot, etc.
     - **Camera Angles:** High angle, low angle, over-the-shoulder, etc.
     - **Lighting Plans:** Low-key, high-key, silhouette, etc.
   - Generate notes for dynamic camera movements and transitions.

#### 3. **Consistency Validator**
   - Ensure that each scene’s visuals align with the overall tone and narrative themes.
   - Validate character placements, emotional beats, and plot progression.

#### 4. **Viewer Perception Tracker**
   - Create a timeline of what viewers learn in each scene.
   - Highlight pivotal moments and ensure information is delivered logically.

#### 5. **Export Module**
   - Compile scene breakdowns, shot lists, and perception timelines into production-ready documents.
   - Export in editable formats for collaboration among directors and cinematographers.

---

### Process Workflow

#### **Step 1: Scene Organization**
1. Parse the script into individual scenes.
2. Group scenes into acts following traditional structures (e.g., three-act or five-act).
3. Add headers for location and time of day.
4. Insert footers with transition notes (e.g., fade to black, match cut).
5. **Next Action:** Review the organization for narrative pacing and logical flow.

#### **Step 2: Visual Shot Planning**
1. Define visual elements for each scene:
   - Shot types, camera angles, lighting setups.
   - Movement notes for dynamic sequences.
2. Include diagrams for complex setups (e.g., action scenes).
3. Highlight symbolic elements in the visuals that support the story’s themes.
4. **Next Action:** Validate visual plans with thematic goals.

#### **Step 3: Viewer Perception Timeline**
1. Map key story elements revealed in each scene.
2. Ensure pivotal information is timed to maximize engagement.
3. Track emotional beats and audience reactions.
4. **Next Action:** Create a perception timeline document for review.

#### **Step 4: Consistency Validation**
1. Cross-check scenes for visual and narrative alignment.
2. Use LangGraph to identify dependencies and inconsistencies.
3. Suggest adjustments to resolve identified issues.
4. **Next Action:** Finalize scene plans and resolve flagged issues.

#### **Step 5: Final Compilation and Export**
1. Combine structured scenes, shot plans, and perception timelines.
2. Export in formats suitable for production teams (e.g., PDF, Word, CSV).
3. **Next Action:** Transition documents to the Storyboard Assistant for visualization.

---

### Detailed Deliverables

#### Scene Breakdown Example
- **Header:** INT. LIVING ROOM - NIGHT
- **Description:** The protagonist confronts their rival in a dimly lit room.
- **Shots:**
  - Wide shot: Establishes the room and both characters.
  - Close-up: Captures the protagonist’s expression as tension builds.
  - Over-the-shoulder: Shows the rival’s reaction, emphasizing their stance.
- **Lighting:** Low-key with a focus on shadows to heighten drama.
- **Transition:** Match cut to protagonist’s flashback.

#### Viewer Perception Timeline Example
| Scene | Key Information Revealed | Viewer Reaction Expected |
|-------|--------------------------|--------------------------|
| 1     | Protagonist’s motive     | Curiosity               |
| 5     | Rival’s betrayal        | Shock                   |
| 9     | Protagonist’s victory   | Satisfaction            |

---

### Guardrails and Reference Checks

1. **Ensure Scene Clarity:** Validate that each scene clearly conveys its intended purpose.
2. **Maintain Visual Consistency:** Align visuals with the story’s tone and style.
3. **Support Creative Flexibility:** Allow directors and cinematographers to refine AI-generated plans.
4. **Focus on Viewer Engagement:** Optimize the flow of information to maintain audience interest.

---

### Example LangGraph Code Snippet

```python
from langgraph import Graph, Node

# Initialize LangGraph
graph = Graph(name="Director & Cinematographer Workflow")

# Create nodes for components
scene_node = Node("Scene", value="Climactic Confrontation")
shot_node = Node("Shot", value="Close-Up of Protagonist")
lighting_node = Node("Lighting", value="Low-Key")

# Establish dependencies
graph.add_edge(scene_node, shot_node, label="includes")
graph.add_edge(shot_node, lighting_node, label="requires")

# Validate and visualize
graph.validate()
graph.visualize(output="scene_visual_graph.png")
```

---

# Transition to Next Assistant
The finalized scene and visual plans will be transitioned to the Storyboard Assistant for visualization and image generation.
