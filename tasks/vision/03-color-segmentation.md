# Task: Color Segmentation + Object Selection Node

## Description
Write a ROS 2 node that segments the camera image by color, finds the largest blob of a target color, and publishes its position in the image and in the world. Used to pick up game elements (cubes, balls) by color. Output must be clean enough that a downstream pick / approach behavior can use the position directly.

## Desired Output
- New node `color_segmenter.py` in `src/myrobot_control/myrobot_control/` (or `myrobot_vision` if created).
- Subscribes to `/camera/image_raw`.
- Publishes:
  - `/color/blob/image_debug` — image with the selected blob drawn.
  - `/color/blob/pose` — pose (or 2D pixel + estimated depth) of the largest blob.
- Parameters in YAML: target color (HSV lower/upper), min area, blur kernel size, depth source.

## Input
- Camera image topic from `tasks/simulation/04-camera-on-robot.md`.
- OpenCV (`cv2`) for HSV mask + contour find.
- For depth: either stereo (not available) or assume ground plane and use blob's y position in image. Document the assumption.

## Configuration
- HSV range: default red (`(0, 120, 70)` to `(10, 255, 255)`), exposed as YAML.
- Min blob area: 500 px (tune from sim image).
- Blur kernel: 5x5.
- Depth assumption: blob sits on the floor at known z. Document the camera height and tilt used for the projection.

## Docs Needed
- [ ] Node README section in the package that hosts it.
- [ ] Screenshot in `tasks/vision/` showing the detected blob overlay.
