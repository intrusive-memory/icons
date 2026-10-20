import Testing
@testable import Icons

#if canImport(AppKit)
import AppKit

@Test(arguments: Icon.allCases)
func symbolLoads(_ icon: Icon) {
    #expect(NSImage(symbolName: icon.rawValue, bundle: Icon.bundle, variableValue: 1) != nil)
}
#elseif canImport(UIKit)
import UIKit

@Test(arguments: Icon.allCases)
func symbolLoads(_ icon: Icon) {
    #expect(UIImage(named: icon.rawValue, in: Icon.bundle, with: nil) != nil)
}
#endif
