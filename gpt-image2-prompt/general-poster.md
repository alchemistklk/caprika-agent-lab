# General Poster Prompt Workflow

## Purpose

Create a high-impact social poster for a product milestone, launch, release, or
public proof point. The poster should communicate one strong claim first, then
support it with brand signals, product objects, and metrics.

## Variables

```text
Project:
Milestone:
Time window:
Primary claim:
Secondary claim:
Audience:
Brand palette:
Main visual metaphor:
Product objects:
Metrics:
Forbidden elements:
```

## Reusable Prompt Template

```text
Generate a [WIDTH]x[HEIGHT] high-impact social poster for [PROJECT].

Purpose:
The poster should announce [PRIMARY CLAIM] and make it feel like a credible,
memorable milestone rather than a generic marketing graphic.

Brand system:
Use [BRAND PALETTE]. Keep the image aligned with [PROJECT]'s product language:
[PRODUCT OBJECTS]. Use one dominant signal color for the milestone and keep
secondary accents controlled.

Main copy:
[MAIN COPY]

Secondary copy:
[SECONDARY COPY]

Composition:
Create a strong poster hierarchy. The main milestone should be the first thing
people read. Use [MAIN VISUAL METAPHOR] as the central visual idea. The metaphor
should support the claim without making the poster confusing. Keep enough
negative space for readable typography.

Metrics:
[METRICS]

Style:
[STYLE DIRECTION]. Make it readable at social feed scale. Balance artistic
energy with product clarity.

Avoid:
[FORBIDDEN ELEMENTS]
```

## Example Preset: Open Design 80K Poster

```text
Project: Open Design
Milestone: 80K GitHub stars
Time window: 84 days
Primary claim: 80K stars in 84 days
Secondary claim: Open · Local · Agent-native
Audience: developers, designers, agent builders, open-source community
Brand palette: black/charcoal, off-white, neon green, restrained blue/magenta/orange
Main visual metaphor: a winding neon growth path through an abstract product map
Product objects: UI fragments, selection handles, cursor forms, geometric panels,
agent workflow artifacts, product-canvas surfaces
Metrics: 9.2K Forks, Apache-2.0, 386 Contributors, 1,991 Community PRs
Forbidden elements: generic AI sci-fi, photoreal climbing, conservative dashboards,
large destination icon, 60K/70K labels, excessive arrows or noisy linework
```

## Filled Prompt: Open Design 80K Poster

```text
Generate a 1024x1536 high-impact social poster for Open Design.

Purpose:
The poster should announce 80K stars in 84 days and make it feel like a
credible, memorable milestone rather than a generic marketing graphic.

Brand system:
Use deep black/charcoal background, off-white surfaces and typography, neon
green as the primary signal, and restrained blue, magenta, and orange product
art accents. Keep the image aligned with Open Design's product language: UI
fragments, selection handles, cursor forms, geometric panels, agent workflow
artifacts, and product-canvas surfaces.

Main copy:
Open Design
80K★
GitHub stars in 84 days

Secondary copy:
Open · Local · Agent-native

Composition:
Create a vivid abstract map-like product terrain. A neon green winding road
acts as the GitHub growth curve. The road should feel like a completed path
that has already crossed the 80K milestone and continues forward into future
possibilities. Place "80K stars in 84 days" as part of the path narrative, not
as an unreachable destination marker. Do not place a large icon at the end of
the path.

Metrics:
9.2K Forks
Apache-2.0
386 Contributors
1,991 Community PRs

Style:
High-contrast, artistic, energetic, premium, playful, and readable at social
feed scale. Blend modern product graphics with expressive painterly motion.

Avoid:
generic AI sci-fi, photoreal mountain climbing, conservative dashboards, 60K
and 70K labels, large destination icons, excessive arrows, and noisy linework.
```

## Iteration Notes

- A literal climbing metaphor communicated effort, but moved away from the
  product brand.
- A pure metric dashboard was clear, but not expressive enough.
- A product-map path gave the right balance: milestone, journey, product
  surface, and future movement.

