// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "Icons",
    platforms: [
        .macOS(.v14),
        .iOS(.v17),
    ],
    products: [
        .library(name: "Icons", targets: ["Icons"]),
    ],
    targets: [
        .target(
            name: "Icons",
            resources: [.process("Resources")]
        ),
        .testTarget(
            name: "IconsTests",
            dependencies: ["Icons"]
        ),
    ]
)
