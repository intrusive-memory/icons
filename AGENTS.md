---
type: reference
title: AGENTS.md — Icons
---

# AGENTS.md — Icons

Instructions for AI agents working in this repo. See `PROJECT.md` for what the library is and how apps consume it.

## Layout

```
Sources/Icons/Icon.swift                 Icon enum + Image/Label helpers (public API)
Sources/Icons/Resources/Icons.xcassets   one <name>.symbolset per icon (the shipped artifacts)
Scripts/generate-*.py                    generators for script-built symbols
Scripts/preview.swift                    contact-sheet renderer used by `make preview`
Tests/IconsTests                         checks every Icon case loads from the bundle
```

## Commands

Always use `make` (`make help` lists the targets). Never run `swift build` or `swift test`.

| Target | Does |
|---|---|
| `make generate` | Rerun the generators and rewrite their symbolsets |
| `make validate` | Compile the catalog with `actool`; fails on any warning or error |
| `make preview` | Render every symbol to `build/preview.png` and open it in Preview |
| `make test` | `xcodebuild test` on macOS |

## Rules for symbols

- **Every icon is an SF Symbols template**, never a plain SVG. Required ids: `Ultralight-S`, `Regular-S` and `Black-S` groups under `Symbols`, plus matching `left-margin-*` and `right-margin-*` lines and `Baseline-*`/`Capline-*` guides. Xcode interpolates the other weights and scales from those three.
- **Filled outlines only.** SF Symbols ignores strokes, so convert every stroke to a filled path.
- **Same path structure in all three weights.** Same number of paths and the same command sequence, or interpolation breaks. The generators guarantee this by emitting identical commands with different numbers. Never add a branch that changes the command list based on weight.
- **Layers:** path class `monochrome-N multicolor-N:tintColor hierarchical-N:<primary|secondary|tertiary>`. Later paths draw on top.
- **Gaps instead of overlaps.** Where one shape crosses another (for example, the arrow in `storyboard.sequence`), cut a gap into the shape behind it so it still reads at 17pt.
- **Script-built symbols:** edit the generator, never the generated SVG. Hand-drawn symbols (exported from SF Symbols.app) are edited directly.
- **Check at 17pt Semibold** as well as large sizes; toolbar size is where icons fail.

## Adding an icon

1. Add `<name>.symbolset/` with the template SVG and a `Contents.json` (copy an existing one), or add it to a generator and run `make generate`.
2. Add a case to `Icon` in `Sources/Icons/Icon.swift`. The raw value is the symbolset name.
3. Add a row to the Symbols table in `PROJECT.md`.
4. Run `make validate`, `make preview` and `make test`. All three must pass, and look at the preview before committing.

## Repo

- `intrusive-memory/icons`, **public**.
- Default branch is `main`. Consumers track `main` until there are tagged releases, so don't push breaking renames of `Icon` cases or symbol names without asking.
