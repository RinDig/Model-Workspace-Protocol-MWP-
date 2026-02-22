# Color Palette

All colors as 6-digit hex. Use without `#` prefix in PptxGenJS code. Use with `#` prefix in HTML/CSS.

## Primary Colors

| Role | Hex | Usage |
|------|-----|-------|
| Primary | {{PRIMARY_COLOR}} | Headers, key shapes, accent bars |
| Secondary | {{SECONDARY_COLOR}} | Supporting shapes, secondary headers |
| Accent | {{ACCENT_COLOR}} | Call-outs, highlights, interactive elements |

## Neutrals

| Role | Hex | Usage |
|------|-----|-------|
| Background | {{BG_COLOR}} | Slide background |
| Text | {{TEXT_COLOR}} | Body text, default text color |

## Chart Colors

Use these in order for multi-series charts. Derived from primary palette:

```
chartColors: ["{{PRIMARY_COLOR}}", "{{SECONDARY_COLOR}}", "{{ACCENT_COLOR}}"]
```

## Contrast Rules

- Body text on background must have minimum 4.5:1 contrast ratio
- Heading text on colored shapes must have minimum 3:1 contrast ratio
- Never place light text on light backgrounds or dark text on dark backgrounds
