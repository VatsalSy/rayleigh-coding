# Font Pairing Reference

Curated pairings by aesthetic tone. Never use these verbatim across projects — they're starting points.

## Editorial / Luxury
| Display | Body | Feel |
|---|---|---|
| Playfair Display | Source Serif 4 | Classic, editorial, trust |
| Cormorant | Jost | Refined, high fashion |
| Libre Baskerville | Lato | Journalistic authority |

## Modern / Technical
| Display | Body | Feel |
|---|---|---|
| Cabinet Grotesk | Fraunces | Humanist, warm tech |
| Syne | DM Sans | Editorial geometric |
| Clash Display | Plus Jakarta Sans | Sharp, bold startup |

## Expressive / Playful
| Display | Body | Feel |
|---|---|---|
| Unbounded | Nunito | Bold, rounded, energetic |
| Dela Gothic One | Noto Sans | Japanese-influenced, strong |
| Space Mono | IBM Plex Sans | Terminal aesthetic |

## Brutalist / Raw
| Display | Body | Feel |
|---|---|---|
| Monument Extended | Grotesk | Maximalist authority |
| Anton | Barlow Condensed | Compressed, dense |
| Bebas Neue | Raleway | Poster, structured |

## Soft / Organic
| Display | Body | Feel |
|---|---|---|
| Gilda Display | Crimson Pro | Elegant, literary |
| Zodiak | Epilogue | Organic, modern |
| Canela Deck | Neue Haas Unica | Luxury editorial |

---

## How to load variable fonts efficiently

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cabinet+Grotesk:wght@100..900&family=Fraunces:ital,opsz,wght@0,9..144,100..900;1,9..144,100..900&display=swap" rel="stylesheet">
```

```css
:root {
  --font-display: 'Cabinet Grotesk', sans-serif;
  --font-body: 'Fraunces', serif;
}
```

Always use CSS variables. Never hardcode font-family strings in component styles.
