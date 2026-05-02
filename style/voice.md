# Voice and Style Guide

This file is the canonical style reference for every writing skill in the toolkit. Run-of-show docs, research briefs, co-host briefs, show notes, clip captions, and distribution copy all check against these rules before shipping.

The default rules live here. Per-show extensions go in `config/podcast.yaml` under the `voice:` block.

## Voice principles

- Active voice. Short sentences. Direct address.
- Write like a person talks, not like a press release.
- Lead with the point. Cut the warm-up.
- Concrete beats abstract. Number beats adjective.
- One idea per sentence.
- Trust the reader to follow without scaffolding.

## Format rules

- No semicolons. Use a period or a dash.
- No emojis in body copy.
- No hashtags in body copy. Tags belong at the end of social posts where the platform expects them.
- No metaphor-heavy openers ("In a world where...", "Imagine if...", "Picture this...").
- No closing throat-clears ("In conclusion", "In summary", "To wrap up", "All in all").

## Banned words

Avoid these words entirely. They mark AI-generated copy and they fluff up sentences without adding meaning.

Connectives and softeners:

- accordingly
- additionally
- arguably
- certainly
- consequently
- hence
- however
- indeed
- moreover
- nevertheless
- thus
- undoubtedly

Empty adjectives:

- adept
- commendable
- dynamic
- efficient
- ever-evolving
- exciting
- exemplary
- innovative
- invaluable
- robust
- seamless
- synergistic
- transformative
- vibrant
- vital

Empty nouns:

- efficiency
- innovation
- integration
- implementation
- landscape
- optimization
- realm
- tapestry
- transformation

Empty verbs:

- aligns
- augment
- delve
- embark
- facilitate
- maximize
- underscores
- utilize

## Banned phrases

- "a testament to"
- "it's worth noting"
- "specifically"
- "on the contrary"
- "in today's fast-paced world"
- "in the world of"
- "needless to say"
- "at the end of the day"
- "navigate the complexities of"
- "unlock the potential"
- "game-changer"
- "level up"
- "deep dive"
- "moving forward"

## When a banned word is the right word

A few of these words have legitimate uses. A research brief about a transformer-architecture paper may need to say "transformative" once. A finance segment may need "efficiency" because that is what the source document says.

Rule: if a banned word is the only honest way to say what you mean, use it once. If you find yourself using it twice in a piece, you are reaching. Rewrite.

## Active voice quick check

Before shipping any draft, scan for these patterns and rewrite them:

- "is being [verb]ed by" → make the actor the subject
- "there is" / "there are" at the start of a sentence → start with the noun
- "it is important to note that" → cut the phrase, keep the note
- "due to the fact that" → "because"

## Extending these rules per show

Hosts can add show-specific banned words and phrases in `config/podcast.yaml`:

```yaml
voice:
  banned_words_extra:
    - quick
    - just
  banned_phrases_extra:
    - "as we discussed last episode"
  required_phrases:
    - "the build"
```

Writing skills load this file plus the per-show extensions and check against the union of both lists.
