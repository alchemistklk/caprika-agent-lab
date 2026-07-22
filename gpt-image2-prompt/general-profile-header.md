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

