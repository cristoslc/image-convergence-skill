---
name: image-convergence
description: Review a generated image for compliance with its original prompt, then iterate prompt + generation autonomously until convergence or the attempt cap. Use whenever an image-generation result must match its prompt — after any image generate call, when the returned image may drift from the request, or when the operator asks the image to match the prompt closely.
---

# Image Convergence Loop

You own the loop from first generation to final image. Each attempt is pre-approved work: generate, review, revise, and generate again, then present the final result. The operator receives one delivery — a converged image, or the best-scoring image when stopping short — with the attempt ledger that explains the journey.

## Definitions

- **Original prompt** — the image request as first stated, the ground truth every review measures against.
- **Attempt** — one generate-and-review cycle, numbered from 1.
- **Compliance dimensions** — subject, composition, style, detail, palette-and-lighting. Review every dimension on every image.
- **Convergence score** — the lowest score across the five dimensions, on a 0-10 scale. One weak dimension holds the whole attempt back, so the overall score adopts the weakest link.
- **Ledger** — the running record of attempts. One row per attempt: attempt number, full prompt used, per-dimension scores, overall score, tactic name, and the revision made. The final delivery quotes it in full.
- **Tactic** — the revision strategy in force for the current attempt (see Tactic menu below).

## Core loop on every attempt

1. **Review.** Look at the returned image against the ledger of satisfied elements from the original prompt. Score each dimension 0-10 with a one-line justification, and record the overall score as the lowest of the five. State the score before describing any revision; the score decides what happens next, and the description supports it.
2. **Revise.** Keep every element the image already satisfies by carrying its wording into the next prompt unchanged; the revision layer grows on top. Express each gap as an addition: name the element the prompt gains, with a concrete anchor (a specific noun, number, position, or style reference), and write it as a positive statement of what appears, in what place, in what form.
3. **Generate** the revised prompt and count the attempt.

Loop to convergence: the loop reaches **convergence** when the overall score is 8 or higher, with 8 as the default threshold; an operator-set threshold applies when named, and the first review states the threshold in use.

## Stall detection and tactic changes

Track the best overall score in the ledger. When three consecutive attempts elapse with the best score staying flat or lower, the current tactic is spent: switch tactics for the next revision and say which tactic you are switching to. A tactic change counts as creative movement, so it also applies when two attempts in a row show the same score with identical failure shape.

### Tactic menu (default order)

1. **baseline-revision** — targeted additions to the strongest scoring prompt, element by element.
2. **restructure** — rewrite the prompt around the failing dimension first, so the highest-weight wording leads the prompt.
3. **scene-decomposition** — split the image into an ordered scene description: foreground, midground, background, each with its own clause.
4. **style-anchor** — name a concrete style or medium reference ("in the manner of a 1960s silkscreen poster") and let it carry the palette and texture dimensions.
5. **concretize** — replace every ambiguous word with a countable or measurable form ("several trees" becomes "exactly seven poplars in a row").
6. **reseed** — hold the best prompt verbatim and vary only the generation seed, sampling one fresh variation.

Rotate through the menu in order per stall, holding each new tactic for at least two attempts before judging it. After the menu is exhausted, return to baseline-revision with the accumulated ledger wording.

## Stop conditions

Deliver, with the best-scoring image, in any of these cases:

- **converged** — overall score at or above the threshold.
- **attempt cap** — six attempts completed, with six as the default cap; an operator-set cap applies when named.
- **tactics exhausted** — all menu tactics tried and every one stalled for its holding window.

## Autonomy rules

- Treat every iteration as pre-approved work: assume approval and continue the loop from one attempt to the next.
- Present the ledger and the best image only after the loop reaches a stop condition; a mid-loop message goes out for a finished delivery, not for a checkpoint.
- State the stop reason and the final overall score in the delivery, plus one sentence naming the tactic family that produced the best image.
- Carry the best-scoring prompt forward as the final prompt, quoted verbatim at the end of the delivery for reuse.

## Positive-only prompting

Image-model inputs stay in prompt space: every change is an addition to the prompt text. The workflow steers content by stating desired attributes positively ("the image renders the tower at the third-floor line, brass-clad"), and scores the image on the same positive terms. This loop runs entirely on positive guidance for both the model and the agent: phrasing in the prompt, in reviews, and in the ledger records what is present and what arrives next.