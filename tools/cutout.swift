// Lift the subject(s) out of a photo with Apple Vision (same model as Photos' "Lift subject").
// Usage: swift cutout.swift <input image> <output prefix>
// Writes <prefix>-all.png (every foreground instance) and <prefix>-<n>.png per instance.
import CoreImage
import Foundation
import ImageIO
import Vision

let args = CommandLine.arguments
guard args.count == 3 else {
    print("usage: cutout.swift <input> <output-prefix>")
    exit(1)
}
let inURL = URL(fileURLWithPath: args[1])
let outPrefix = args[2]

guard let src = CGImageSourceCreateWithURL(inURL as CFURL, nil),
      let cg = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
    print("could not load \(inURL.path)")
    exit(1)
}
let props = CGImageSourceCopyPropertiesAtIndex(src, 0, nil) as? [CFString: Any]
let orientRaw = (props?[kCGImagePropertyOrientation] as? UInt32) ?? 1
let orientation = CGImagePropertyOrientation(rawValue: orientRaw) ?? .up

let handler = VNImageRequestHandler(cgImage: cg, orientation: orientation)
let request = VNGenerateForegroundInstanceMaskRequest()
try handler.perform([request])
guard let obs = request.results?.first else {
    print("no subject found")
    exit(2)
}

let ctx = CIContext()
let srgb = CGColorSpace(name: CGColorSpace.sRGB)!

func write(_ instances: IndexSet, _ suffix: String) throws {
    let buf = try obs.generateMaskedImage(ofInstances: instances, from: handler, croppedToInstancesExtent: true)
    let image = CIImage(cvPixelBuffer: buf)
    let url = URL(fileURLWithPath: "\(outPrefix)-\(suffix).png")
    try ctx.writePNGRepresentation(of: image, to: url, format: .RGBA8, colorSpace: srgb)
    print("\(url.lastPathComponent): \(Int(image.extent.width))x\(Int(image.extent.height))")
}

print("instances: \(obs.allInstances.count)")
try write(obs.allInstances, "all")
for i in obs.allInstances where obs.allInstances.count > 1 {
    try write(IndexSet(integer: i), String(i))
}
