// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "ScreenCleaner",
    platforms: [.macOS(.v13)],
    targets: [
        .executableTarget(
            name: "ScreenCleaner",
            path: "Sources",
            linkerSettings: [
                .unsafeFlags(["-Xlinker", "-sectcreate", "-Xlinker", "__TEXT", "-Xlinker", "__info_plist", "-Xlinker", "Sources/Info.plist"])
            ]
        )
    ]
)
