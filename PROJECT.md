---
type: project
title: Icons
author: Tom Stovall
created: 2026-10-20T00:00:00Z
description: "Custom SF Symbols for intrusive-memory apps, shipped as a Swift package so every project uses the same icons."
visibility: public
tags: [sf-symbols, icons, swiftui, swift-package]
---

# Icons

The intrusive-memory custom icon library. Every icon is a **custom SF Symbol**: an SF Symbols template SVG inside an asset catalog. That means it scales with Dynamic Type, follows `.fontWeight`, and supports the monochrome, hierarchical and multicolor rendering modes, just like a system symbol.

## Symbols

| Name | Swift | What it shows | Used by |
|---|---|---|---|
| `storyboard` | `Icon.storyboard` | One panel with two caption lines | Vinetas |
| `storyboard.sequence` | `Icon.storyboardSequence` | A half panel stacked behind a full one, pierced by a left-to-right arrow | Vinetas |

Run `make preview` to see every symbol at five weights and two sizes.

## Using it

Add the package:

```swift
.package(url: "https://github.com/intrusive-memory/icons.git", branch: "main")
```

```swift
import Icons

Image(icon: .storyboard)
Label("Sequence", icon: .storyboardSequence)

// AppKit / UIKit
NSImage(symbolName: Icon.storyboard.rawValue, bundle: Icon.bundle, variableValue: 1)
UIImage(named: Icon.storyboard.rawValue, in: Icon.bundle, with: nil)
```

Projects that don't use Swift can take the template SVGs straight from `Sources/Icons/Resources/Icons.xcassets/*.symbolset/`.

## Status

- Public. There are no tagged releases yet, so consumers track `main`.
- Platforms: macOS 14+, iOS 17+.
