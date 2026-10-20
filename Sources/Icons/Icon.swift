import SwiftUI

/// Custom SF Symbols shipped in this package's asset catalog.
///
/// The raw value is the symbolset name in `Resources/Icons.xcassets`.
public enum Icon: String, CaseIterable, Sendable {
    /// A single storyboard panel with caption lines.
    case storyboard
    /// The storyboard panel framing a head and shoulders.
    case storyboardCharacter = "storyboard.character"
    /// The storyboard panel framing an isometric cube.
    case storyboardProp = "storyboard.prop"
    /// A storyboard panel stacked behind another, pierced by a left-to-right arrow.
    case storyboardSequence = "storyboard.sequence"

    /// The bundle holding the compiled symbols, for AppKit/UIKit lookups.
    public static var bundle: Bundle { .module }
}

public extension Image {
    /// A custom symbol from this package. Responds to `.font`, `.imageScale`,
    /// `.fontWeight` and `.symbolRenderingMode` like a system symbol.
    init(icon: Icon) {
        self.init(icon.rawValue, bundle: .module)
    }
}

public extension Label where Title == Text, Icon == Image {
    init(_ title: LocalizedStringKey, icon: Icons.Icon) {
        self.init {
            Text(title)
        } icon: {
            Image(icon: icon)
        }
    }
}
