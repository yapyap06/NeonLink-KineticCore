# WORKFLOW: NeonLink Kinetic Core (AI-Enhanced Co-op Tetris)

## [PROJECT OVERVIEW]
A Python-based collaborative Tetris game where:
- Player 1 (Processor): Uses Keyboard for precision movement.
- Player 2 (Physicist): Uses AI Camera (MediaPipe) for physics manipulation.
- Goal: Maintain harmony and clear lines using hand gestures.

---

## [PHASE 1: ENVIRONMENT SETUP]
- Initialize a Python project.
- Install dependencies: `pygame`, `opencv-python`, `mediapipe`.
- Create the core directory structure:
    - `/assets` (Neon sound effects/fonts)
    - `/src` (Core logic)
    - `/src/ai` (MediaPipe integration)

---

## [PHASE 2: THE KINETIC ENGINE (AI CAMERA)]
- Implement `HandTracker` class using `mediapipe.solutions.hands`.
- **Gesture Mapping:**
    - `OPEN_PALM`: Reduce gravity (Slow-motion mode).
    - `CLOSED_FIST`: Increase gravity (Kinetic Slam / Hard Drop).
- Run the camera feed in a separate thread to prevent game lag.



---

## [PHASE 3: THE PROCESSOR CORE (GAME LOGIC)]
- Build the Tetris grid logic (10x20).
- Implement standard tetromino shapes and rotation matrices.
- Map `Keyboard` inputs: `Left`, `Right`, `Up` (Rotate).
- Integrate the AI variables from Phase 2 into the `fall_speed` calculation.

---

## [PHASE 4: VIBE UI & FEEDBACK]
- Style the UI with a "Neon/Cyber" aesthetic.
- Add a "Vibe Meter" that grows when both players interact simultaneously.
- Display the camera feed in a corner "Ghost Window" with AI landmarks overlaid.

---

## [PHASE 5: PERSISTENCE & GITHUB PREP]
- Implement a High Score system.
- Generate a `README.md` with instructions on how to use the camera.
- Ensure the code is documented for GitHub upload.