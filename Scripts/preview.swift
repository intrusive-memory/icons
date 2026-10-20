// Renders every symbol in a compiled asset catalog to a PNG contact sheet.
// Usage: preview <bundle-dir> <output.png> <symbol-name>...
// Columns are weights (Ultralight → Black); each symbol gets a 64pt
// hierarchical row and a 17pt monochrome row.
import AppKit

let args = CommandLine.arguments
guard args.count > 3, let bundle = Bundle(path: args[1]) else {
    print("usage: preview <bundle-dir> <output.png> <symbol-name>...")
    exit(2)
}
let output = args[2]
let names = Array(args.dropFirst(3))
let weights: [NSFont.Weight] = [.ultraLight, .light, .regular, .semibold, .black]
let cellW: CGFloat = 220, cellH: CGFloat = 130
let canvas = NSImage(size: NSSize(width: cellW * CGFloat(weights.count), height: cellH * CGFloat(names.count * 2)))
canvas.lockFocus()
NSColor.white.setFill()
NSRect(origin: .zero, size: canvas.size).fill()
for (row, name) in names.enumerated() {
    guard let base = NSImage(symbolName: name, bundle: bundle, variableValue: 1) else {
        print("missing symbol: \(name)")
        exit(1)
    }
    for (col, weight) in weights.enumerated() {
        for (sub, pointSize) in [CGFloat(64), 17].enumerated() {
            var config = NSImage.SymbolConfiguration(pointSize: pointSize, weight: weight)
            if sub == 0 { config = config.applying(.init(hierarchicalColor: .systemBlue)) }
            let img = base.withSymbolConfiguration(config)!
            let y = canvas.size.height - cellH * CGFloat(row * 2 + sub + 1)
            img.draw(in: NSRect(
                x: CGFloat(col) * cellW + (cellW - img.size.width) / 2,
                y: y + (cellH - img.size.height) / 2,
                width: img.size.width,
                height: img.size.height
            ))
        }
    }
}
canvas.unlockFocus()
let rep = NSBitmapImageRep(data: canvas.tiffRepresentation!)!
try rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: output))
print("wrote \(output)")
