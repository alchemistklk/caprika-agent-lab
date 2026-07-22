# General Product Visual Prompt Workflow

## Purpose

Create a visual for a product concept, feature surface, workflow artifact, or
technical capability. This differs from a poster or profile header: the image
should make the product's workflow and value legible.

## Variables

```text
Product:
Feature or workflow:
User role:
Core value:
Input artifacts:
Process artifacts:
Output artifacts:
Brand palette:
Main metaphor:
Interface surfaces:
Engineering signals:
Forbidden elements:
```

## Reusable Prompt Template

```text
Generate a product visual for [PRODUCT].

Purpose:
Show how [FEATURE OR WORKFLOW] helps [USER ROLE] achieve [CORE VALUE]. The
image should communicate the workflow and product surface, not just look like a
generic technology illustration.

Workflow:
Represent the flow from [INPUT ARTIFACTS] through [PROCESS ARTIFACTS] into
[OUTPUT ARTIFACTS]. Make the transformation visible through concrete objects,
interface surfaces, and artifact previews.

Brand system:
Use [BRAND PALETTE]. Keep the image aligned with [PRODUCT]'s product language:
[INTERFACE SURFACES].

Composition:
Use [MAIN METAPHOR] as the organizing idea. Balance product clarity with visual
energy. The image should be inspectable enough that a viewer can infer what the
product does.

Engineering signals:
[ENGINEERING SIGNALS]

Avoid:
[FORBIDDEN ELEMENTS]
```

## Example Preset: Agent-Native Visual Build Workflow

```text
Product: Open Design / Caprika visual build workflow
Feature or workflow: turning product work and AI sessions into visual artifacts
User role: maintainer, agent developer, designer-engineer
Core value: make real engineering and product progress visible, reusable, and publishable
Input artifacts: PRs, release notes, product screenshots, prompts, local files, links
Process artifacts: agent workflow nodes, model routing, terminal panes, design canvases, cursor actions
Output artifacts: posters, profile headers, B-roll cards, visual notes, publishable screenshots
Brand palette: black/charcoal base, off-white surfaces, neon green signal color,
restrained blue/magenta/orange accents
Main metaphor: a local engineering desk dissolving into an animated visual artifact pipeline
Interface surfaces: browser windows, code panes, prompt cards, file drawers,
preview panels, canvas frames, selection handles, graph nodes
Engineering signals: local storage cubes, status lights, workflow traces,
terminal fragments, model cards, artifact previews
Forbidden elements: generic AI cloud, abstract glowing brain, fake unreadable
dashboard, large central robot, large slogan text, empty decoration
```

## Filled Prompt: Agent-Native Visual Build Workflow

```text
Generate a product visual for an agent-native visual build workflow.

Purpose:
Show how a maintainer or designer-engineer can turn real product work and AI
sessions into visual artifacts that are reusable and publishable. The image
should communicate a workflow surface, not a generic technology illustration.

Workflow:
Represent the flow from PRs, release notes, screenshots, prompts, local files,
and links through agent workflow nodes, model routing, terminal panes, design
canvases, and cursor actions into finished posters, profile headers, B-roll
cards, visual notes, and publishable screenshots.

Brand system:
Use a black/charcoal base, off-white surfaces, neon green signal color, and
restrained blue/magenta/orange accents. Keep the image aligned with a product
language of browser windows, code panes, prompt cards, file drawers, preview
panels, canvas frames, selection handles, and graph nodes.

Composition:
Use a local engineering desk dissolving into an animated visual artifact
pipeline as the organizing metaphor. Balance product clarity with cinematic
energy. The image should be inspectable enough that a viewer can infer what the
product does.

Engineering signals:
local storage cubes, status lights, workflow traces, terminal fragments, model
cards, cursor operations, and artifact previews.

Avoid:
generic AI cloud, abstract glowing brain, fake unreadable dashboard, large
central robot, large slogan text, and empty decoration.
```

