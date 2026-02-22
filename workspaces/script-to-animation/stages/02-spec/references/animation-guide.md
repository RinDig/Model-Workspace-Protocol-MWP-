# Animation Guide

Principles for writing better animation specs. These apply whether you are building in Remotion, After Effects, or any other tool. Load this when writing specs to make visual decisions that serve the content.

---

## Core Principle: The Visual IS the Argument

The animation should not illustrate the narration. It should BE the explanation. If you muted the audio, the viewer should still follow the core idea from visuals alone.

- **Passing:** A cross-section showing data splitting and reassembling. Arrows showing flow between systems. A diagram that transforms as the narrator describes what happens.
- **Failing:** Text labels fading in with motion blur. Code snippets on dark backgrounds. Icons bouncing into frame.

When writing a spec, ask for each beat: "What does the visual PROVE?" If the answer is "it shows the name of the thing," the visual is a label, not an argument.

---

## Motion Principles

### 1. One Thing Moves at a Time

When two elements animate simultaneously, the viewer does not know where to look. Stagger entrances by 5-10 frames minimum. The exception: elements that are conceptually one unit (a label attached to a diagram element).

### 2. Entrances Are Slower Than Exits

Elements earn attention arriving. They should not demand attention leaving. A 20-frame entrance with a 10-frame exit feels natural. The reverse feels jarring.

### 3. Spring Physics Over Linear Easing

Linear motion (constant speed start to finish) looks robotic. Spring-based motion (fast start, gentle overshoot, settle) looks physical and alive.

When speccing motion, prefer:
- `spring` with moderate damping (10-15) for entrances
- `ease-out` for slides and position changes
- `ease-in` for exits (accelerate away)

Avoid: `linear` easing on anything except progress bars or continuous scrolls.

### 4. Hold After Entrance

When an element appears, pause 5-10 frames before anything else moves. This gives the viewer time to register the new element. Without the hold, sequences feel rushed even when the total duration is long.

### 5. Motion Should Have Direction

Elements entering from the left suggest "coming next." Elements entering from the bottom suggest "building up." Be consistent within a video. If layers stack downward, every layer should enter from above or appear in place. Mixing directions breaks the spatial logic.

---

## Visual Rhythm

### Vary the Pattern

If every beat uses the same animation (slide in from left, text appears, fade out), the sequence becomes predictable. Once the viewer can predict what is next, they lose the urgency to stay.

For each beat, vary at least one of:
- Entry direction (left, right, top, bottom, scale up, fade in)
- Color (alternate between primary and secondary)
- Visual element type (diagram, then text, then illustration, then diagram)
- Timing (one quick beat, then a longer one)

### Rescue at the Midpoint

The 3rd or 4th beat in a 5-7 beat sequence is where attention drops most. This is where you put the biggest visual shift: a color change, a zoom, a completely different element type. It rescues attention at the moment it needs it most.

### Breathing Room

Not every frame needs motion. Static moments (a held image, a pause between beats) let the viewer absorb what just happened. Dense motion without pauses is exhausting to watch.

---

## Layered Reveal Specifics

The layered reveal is the core format for this workspace. These principles apply specifically to that structure.

### Stack Direction

Layers stack downward by default. The first layer appears at the top of the frame. Each new layer appears below, pushing the visual "deeper." This creates a physical metaphor: surface to depth.

### Layer Consistency

Every layer should have the same visual structure: a colored bar or region, a label, and a brief visual showing what the layer does. The consistency creates a pattern. The variations within that pattern (different colors, different inner visuals) keep it interesting.

### The Descent Feel

The accumulation of layers IS the argument. Do not explain how each layer works internally. Name it, show what it does with one visual element, move on. The power is in the quantity and variety of layers, not the depth within any single one.

### Progressive Complexity

Early layers can be simple (just a label and a color). Later layers should get more visually complex: inner diagrams, data flowing through them, multiple sub-elements. This creates a sense of escalating complexity that mirrors the conceptual depth.

---

## Common Mistakes in Specs

**Over-speccing motion.** Writing detailed keyframe curves and exact pixel positions in the spec. The spec should describe what happens ("text slides in from left"), not the implementation details ("translateX from -200 to 0 over 18 frames with cubic-bezier(0.2, 0, 0.1, 1)"). Let the build stage handle implementation.

**Under-speccing visuals.** Writing "show a diagram" without describing what the diagram contains, how many elements, or what it proves. The spec should be detailed enough that two different animators would produce similar visuals.

**Ignoring audio sync.** The narration has natural pause points. Beats should align with these pauses. If a sentence is 3 seconds and the beat is 8 seconds, there are 5 seconds of visual-only time. Spec what happens during that time.

**Identical beats.** Writing the same animation for every beat. Even if the content structure is similar, the visual treatment should vary to maintain attention.
