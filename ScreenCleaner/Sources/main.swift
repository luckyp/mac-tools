import Cocoa

// MARK: - App Delegate

class AppDelegate: NSObject, NSApplicationDelegate {
    var overlayWindows: [NSWindow] = []
    var localEventMonitor: Any?
    // 1cm ≈ 28.35pt（96dpi 标准），取整为 28pt 半径
    let unlockRadius: CGFloat = 28.0

    func applicationDidFinishLaunching(_ notification: Notification) {
        for screen in NSScreen.screens {
            let window = createOverlayWindow(for: screen)
            overlayWindows.append(window)
        }

        NSCursor.hide()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            NSCursor.unhide()
        }
    }

    func createOverlayWindow(for screen: NSScreen) -> NSWindow {
        let window = NSWindow(
            contentRect: screen.frame,
            styleMask: .borderless,
            backing: .buffered,
            defer: false,
            screen: screen
        )

        window.level = .statusBar + 1
        window.backgroundColor = .black
        window.isOpaque = true
        window.hasShadow = false
        window.ignoresMouseEvents = false
        window.acceptsMouseMovedEvents = true
        window.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]

        let contentView = CleanerView(appDelegate: self, screen: screen)
        window.contentView = contentView
        window.makeKeyAndOrderFront(nil)

        return window
    }

    func unlock() {
        if let monitor = localEventMonitor {
            NSEvent.removeMonitor(monitor)
            localEventMonitor = nil
        }

        for window in overlayWindows {
            window.orderOut(nil)
        }
        overlayWindows.removeAll()

        NSApplication.shared.terminate(nil)
    }
}

// MARK: - Cleaner View

class CleanerView: NSView {
    weak var appDelegate: AppDelegate?
    let screen: NSScreen
    init(appDelegate: AppDelegate, screen: NSScreen) {
        self.appDelegate = appDelegate
        self.screen = screen
        super.init(frame: NSRect(origin: .zero, size: screen.frame.size))
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func draw(_ dirtyRect: NSRect) {
        NSColor.black.setFill()
        bounds.fill()


        let screenCenter = NSPoint(x: bounds.midX, y: bounds.midY)
        let radius = appDelegate?.unlockRadius ?? 28.0

        let circleRect = NSRect(
            x: screenCenter.x - radius,
            y: screenCenter.y - radius,
            width: radius * 2,
            height: radius * 2
        )
        let circle = NSBezierPath(ovalIn: circleRect)

        // 灰色填充，与黑色背景形成对比
        NSColor(white: 0.65, alpha: 1.0).setFill()
        circle.fill()

        let hintText = "点击圆形区域退出或按下F11显示桌面"
        let attributes: [NSAttributedString.Key: Any] = [
            .font: NSFont.systemFont(ofSize: 13, weight: .light),
            .foregroundColor: NSColor(white: 0.55, alpha: 1.0)
        ]
        let textSize = hintText.size(withAttributes: attributes)
        let textPoint = NSPoint(
            x: screenCenter.x - textSize.width / 2,
            y: screenCenter.y - radius - textSize.height - 8
        )
        hintText.draw(at: textPoint, withAttributes: attributes)
    }

    override func acceptsFirstMouse(for event: NSEvent?) -> Bool {
        return true
    }

    override func mouseDown(with event: NSEvent) {
        guard let appDelegate = appDelegate else { return }

        // 获取点击位置（窗口坐标）
        let clickPoint = convert(event.locationInWindow, from: nil)

        // 屏幕中心（视图坐标）
        let center = NSPoint(x: bounds.midX, y: bounds.midY)

        // 计算距离
        let dx = clickPoint.x - center.x
        let dy = clickPoint.y - center.y
        let distance = sqrt(dx * dx + dy * dy)

        if distance <= appDelegate.unlockRadius {
            appDelegate.unlock()
        }
    }

    override var acceptsFirstResponder: Bool { return true }
}

// MARK: - Main Entry

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate

// 激活应用到前台
app.setActivationPolicy(.regular)
app.activate(ignoringOtherApps: true)

app.run()
