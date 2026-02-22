# Component Registry

The available animation components. Specs and builds should only reference components listed here. If you need a component that does not exist, add it to this registry first.

---

## Text Components

### TextReveal

Animates text appearing on screen, character by character or word by word.

**Props:**
- `text` (string) -- The text to display
- `position` (string) -- Where on screen: "center", "bottom-third", "top-third", "left", "right"
- `style` (string) -- "heading" uses {{HEADING_FONT}}, "body" uses {{BODY_FONT}}
- `revealMode` (string) -- "character", "word", or "line"
- `color` (string) -- Text color, hex value

### TextBlock

Static text block. No animation.

**Props:**
- `text` (string) -- The text to display
- `position` (string) -- Screen position
- `style` (string) -- "heading" or "body"
- `color` (string) -- Text color
- `maxWidth` (number) -- Maximum width as percentage of frame (default: 80)

### Caption

Lower-third caption with background bar.

**Props:**
- `text` (string) -- Caption text
- `background` (string) -- Bar color (default: {{PRIMARY_COLOR}})
- `textColor` (string) -- Text color (default: white)

---

## Visual Components

### BackgroundGradient

Full-frame gradient background.

**Props:**
- `from` (string) -- Start color, hex
- `to` (string) -- End color, hex
- `direction` (string) -- "top-to-bottom", "left-to-right", "radial"

### LayerDiagram

Cross-section diagram showing stacked layers. Core component for Layered Reveal format.

**Props:**
- `layers` (array) -- List of layer objects: { name, color, icon }
- `activeLayer` (number) -- Which layer is currently highlighted (0-indexed)
- `revealMode` (string) -- "stack-down" (layers appear top to bottom) or "stack-up"
- `spacing` (number) -- Pixels between layers

### IconElement

A single icon or small illustration.

**Props:**
- `icon` (string) -- Icon name from the icon set
- `position` (string) -- Screen position
- `size` (number) -- Size in pixels
- `color` (string) -- Icon color

### ImageFrame

Display an image with optional framing.

**Props:**
- `src` (string) -- Path to image file
- `frame` (string) -- "none", "phone", "browser", "monitor"
- `position` (string) -- Screen position
- `scale` (number) -- Scale factor (1.0 = full size)

---

## Motion Components

### SlideIn

Slides an element into frame from outside.

**Props:**
- `direction` (string) -- "left", "right", "top", "bottom"
- `duration` (number) -- Frames to complete the slide
- `easing` (string) -- Easing function (default: "ease-out")

### FadeTransition

Fades between two states or elements.

**Props:**
- `duration` (number) -- Frames for the fade
- `from` (number) -- Starting opacity (0-1)
- `to` (number) -- Ending opacity (0-1)

### ScaleUp

Scales an element from small to full size (or vice versa).

**Props:**
- `from` (number) -- Starting scale (e.g., 0.5)
- `to` (number) -- Ending scale (e.g., 1.0)
- `duration` (number) -- Frames
- `easing` (string) -- Easing function

### TapRipple

Expanding circle from a touch point. Used for "user taps something" moments.

**Props:**
- `origin` (string) -- Where the tap occurs
- `color` (string) -- Ripple color
- `expandTo` (number) -- How large the ripple grows (multiplier)
- `duration` (number) -- Frames

---

## Layout Components

### SplitScreen

Divides the frame into two panels.

**Props:**
- `split` (string) -- "vertical" or "horizontal"
- `ratio` (string) -- "50-50", "60-40", "70-30"
- `gap` (number) -- Pixels between panels

### FullBleed

Element fills the entire frame edge to edge.

**Props:**
- `padding` (number) -- Inner padding in pixels (default: 0)

### Overlay

Positions an element on top of existing content.

**Props:**
- `position` (string) -- "center", "top-left", "bottom-right", etc.
- `opacity` (number) -- Background overlay opacity (0-1)
- `blur` (number) -- Background blur in pixels (default: 0)

---

## Adding Components

To add a new component, follow this format:

1. Choose the right category (Text, Visual, Motion, Layout)
2. Give it a PascalCase name
3. Write a one-sentence description
4. List all props with types and defaults
5. Add it to this registry before referencing it in any spec
