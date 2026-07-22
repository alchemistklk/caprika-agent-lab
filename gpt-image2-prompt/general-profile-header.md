# General Profile Header Prompt Workflow

## Purpose

Create a wide profile header for a personal or project account. The header
should communicate positioning and taste without becoming a poster or a resume.

## Variables

```text
Account identity:
Role:
Positioning:
Platform:
Canvas size:
Avatar safe area:
Brand palette:
Visual metaphor:
Objects and artifacts:
Optional typography:
Forbidden elements:
```

## Reusable Prompt Template

```text
Create a wide [PLATFORM] profile header background, [WIDTH]x[HEIGHT] safe-crop
composition.

Identity:
The header should express [ACCOUNT IDENTITY] and [POSITIONING]. It should feel
like a visual identity system, not a sales banner.

Brand system:
Use [BRAND PALETTE]. Keep the image aligned with these artifacts:
[OBJECTS AND ARTIFACTS].

Layout:
Keep [AVATAR SAFE AREA] quiet and avatar-safe. Add only subtle low-contrast
atmosphere there so it does not feel blank, but do not compete with the avatar.
Place the main visual energy in [MAIN ENERGY AREA].

Composition:
Build [VISUAL METAPHOR]. Use layered depth, strong shape language, and refined
negative space. The composition should be interesting after cropping.

Typography:
[OPTIONAL TYPOGRAPHY]. If typography is included, keep it minimal and secondary
to the image.

Avoid:
[FORBIDDEN ELEMENTS]
```

## Example Preset: Open Design Maintainer Header

```text
Account identity: Open Design maintainer
Role: maintainer, agent developer, visual build-note author
Positioning: systems, agents, craft
Platform: X/Twitter
Canvas size: 1500x500
Avatar safe area: lower-left
Brand palette: black/charcoal, off-white, neon green, restrained cobalt/cyan,
magenta, and warm orange
Visual metaphor: surreal design atelier with cubist product construction
Objects and artifacts: faceted canvas planes, split-perspective design panels,
sculptural geometric blocks, impossible arches, glass UI fragments,
selection-handle corners, cursor-compass artifacts, product-canvas depth
Optional typography: Open Design maintainer / systems · agents · craft
Forbidden elements: people, mountains, roads, large arrows, readable generated
text, generic AI sci-fi, noisy linework
```

## Filled Prompt: Open Design Maintainer Header

```text
Create a wide X/Twitter profile header background, 1500x500 safe-crop
composition.

Identity:
The header should express an Open Design maintainer identity: systems, agents,
and craft. It should feel like a visual identity system, not a sales banner.

Brand system:
Use deep black and charcoal base, off-white construction surfaces, neon green
as the primary accent, and restrained cobalt blue, cyan, magenta, and warm
orange details. Keep the image aligned with design/product artifacts: faceted
canvas planes, split-perspective design panels, sculptural geometric blocks,
impossible arches, glass UI fragments, floating selection-handle corners, small
cursor-compass artifacts, and product-canvas depth.

Layout:
Keep the lower-left area quiet and avatar-safe. Add only subtle low-contrast
atmosphere there: faint grid planes, soft geometric shadows, small neon green
control points, and distant cubist architectural silhouettes. Do not let this
area feel blank, but do not compete with the avatar. Place the main visual
energy in the center-right and upper-right.

Composition:
Build a surreal design atelier. Fuse early Cubist fragmentation and surreal
metaphysical space, without copying any specific painting. Emphasize design,
beauty, visual construction, and agent-native product work.

Typography:
Avoid readable text in the generated image. Add typography later as a separate
overlay if needed:
Open Design maintainer
systems · agents · craft

Avoid:
people, mountains, roads, large arrows, generated readable text, generic AI
sci-fi, and noisy linework.
```

## Typography Overlay Pattern

Use this only after the image is generated:

```text
Open Design maintainer
systems · agents · craft
```

The overlay should use clean sans-serif type, off-white text, subtle opacity,
and a thin neon green vertical rule or small control points. It should feel like
a gallery annotation, not a marketing headline.

## ImageMagick Overlay Command

```bash
magick input-header.png \
  -font /System/Library/Fonts/HelveticaNeue.ttc \
  -fill '#7CFF00B8' -draw "roundrectangle 146,108 151,203 2,2" \
  -fill '#F4F4EED8' -pointsize 36 -draw "text 174,148 'Open Design maintainer'" \
  -fill '#AEB5ADC8' -pointsize 22 -draw "text 174,190 'systems'" \
  -fill '#7CFF00D8' -draw "circle 275,184 278,184" \
  -fill '#AEB5ADC8' -pointsize 22 -draw "text 295,190 'agents'" \
  -fill '#7CFF00D8' -draw "circle 390,184 393,184" \
  -fill '#AEB5ADC8' -pointsize 22 -draw "text 410,190 'craft'" \
  output-header-typography.png
```

## Iteration Notes

- Profile headers need more negative space than posters.
- The avatar crop changes the composition; the lower-left must stay quiet.
- Generated readable text should usually be avoided. Add final text as a
  deterministic overlay.
- A Cubist-surreal design atelier gave a stronger identity than literal road or
  climbing metaphors.

## Preset: Distributed Agent Engineering Header

Use this when the profile should emphasize agents, LLM workflows, engineering,
local tools, PC/workstation surfaces, and cursor operations without becoming a
literal tool checklist.

```text
Create a wide X/Twitter profile header as a distributed agent-native engineering
atelier.

Do not use readable text. Treat "agent, LLM, PC, cursor, engineering" as
inspiration, not a strict checklist. Translate them into visual metaphors:
model-routing chips, local workstation fragments, terminal panes, file stacks,
artifact preview surfaces, cursor selection traces, workflow nodes, status
lights, and design canvas handles.

Composition:
Use a panoramic, evenly distributed layout across the full width. The left,
center, and right should all contain meaningful but breathable elements. Avoid
an empty left side and avoid a right-heavy cluster. Some details may sit behind
the profile portrait crop.

Style:
Dark Open Design-compatible visual system, charcoal black base, off-white
geometry, neon green control signals, restrained blue/magenta/orange accents,
refined product engineering atmosphere.

Avoid:
readable text, large logo, large human character, generic sci-fi, noisy line
webs, photorealism, cluttered dashboards, mountains, and roads.
```

## Preset: Animated Dream Engineering Header

Use this when the profile should feel more cinematic and emotional, with
animated dream-film color and motion, while still keeping the engineering
identity visible.

```text
Create a complete wide profile header for an Open Design maintainer and agent
engineer, inspired by dream-cinema energy, saturated color rhythm,
psychological montage, and reality-screen blending. Do not copy any specific
scene, character, costume, logo, or frame.

Scene:
A vivid cinematic dream sequence where a real engineering desk, browser
windows, code terminals, model cards, prompt blocks, cursor actions, design
canvases, file artifacts, and agent workflow nodes dissolve into a moving dream
parade of software objects. The world should feel like the boundary between a
computer desktop and a dream city has collapsed.

Subject:
No dominant human character. The main subject is a dreamlike agent-engineering
ecosystem: floating browser windows, local file drawers, terminal panels,
model-routing cards, cursor arrows, design-canvas frames, glowing workflow
nodes, artifact preview panes, graph constellations, color blocks, and screen
portals.

Composition:
Panoramic Twitter/X header. Fill the entire canvas with a complete image. No
deliberate avatar-safe blank space, no big empty circle, no right-heavy cluster.
Arrange objects in a sweeping diagonal dream flow from left to right, with
foreground, midground, and background layers. Make the image visually complete
even if the profile portrait overlaps part of it.

Color:
Saturated reds, warm yellows, cyan blues, violet shadows, magenta highlights,
neon green technical signals, deep indigo/black base.

Text:
No readable text, labels, pseudo-words, or slogans.

Avoid:
copying specific movie characters or frames, readable text, logos, large empty
areas, black avatar placeholder, generic cyberpunk, generic anime trope,
photorealism, cluttered unreadable dashboards, large central person, mountains,
and roads.
```

