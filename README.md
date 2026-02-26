# NeonLink: Kinetic Core

A next-generation modernization of the classic block-falling puzzle, featuring cutting-edge artificial intelligence, neon cyberpunk aesthetics, and a unique kinetic gameplay twist. Originally built in Python/Pygame and ported to a React web app for widespread accessibility!

---

## 🕹️ PLAY ONLINE NOW
**Experience the AI physics directly in your browser:**
👉 [https://yapyap06.github.io/NeonLink-KineticCore/](https://yapyap06.github.io/NeonLink-KineticCore/)

---

## Key Features

* **AI Gesture Control:** Harness the power of Google's MediaPipe Tasks Vision. Use your webcam to physically control the flow of the game!
    * 🖐️ **Open Palm:** Bend time itself! Slow down the game clock to plan your next strategic placement.
    * ✊ **Closed Fist:** Execute a "Kinetic Slam"! Instantly hard-drop the active block into place with a satisfying neon explosion.
* **Neon Aesthetics:** Immerse yourself in a beautifully stylized cyberpunk HUD. Vibrant glowing grids, reactive UI elements, and a dedicated "Vibe Meter" that dynamically responds to your actions.
* **Collaborative Logic:** Designed for dual-input mastery. While the **Physicist** manipulates gravity via the camera, the **Processor** manages precise placement via the keyboard.
* **Cozy Soundtrack:** A custom-generated, lo-fi electric piano chord progression (Cmaj9 -> Fmaj9) with a warm acoustic envelope creates the perfect relaxing backdrop to the intense puzzle action.

## Technical Stack

NeonLink features two distinct architectures, showcasing a bridge between desktop AI and web-native performance:

**1. Desktop Core (Python)**
* `Python 3.x`
* `Pygame-CE` (High-performance rendering and audio engine)
* `OpenCV` (Webcam capture pipeline)
* `MediaPipe` (Real-time hand tracking and gesture recognition)

**2. Web Port (React)**
* `React.js` (Component-based HUD and application state)
* `Vite` (Lightning-fast frontend tooling)
* `HTML5 Canvas/JavaScript` (Core game logic and 60FPS rendering loop)
* `@mediapipe/tasks-vision` (WebAssembly-powered AI model for browser-native camera processing)

## Setup Instructions

Choose the platform you wish to deploy!

### 🖥️ Running the Python Desktop Version (Local)

1.  **Initialize Virtual Environment:**
    ```bash
    python -m venv venv
    ```
2.  **Activate Environment:**
    * Windows: `.\venv\Scripts\activate`
    * Mac/Linux: `source venv/bin/activate`
3.  **Install Dependencies:**
    ```bash
    pip install pygame-ce opencv-python mediapipe
    ```
4.  **Launch the Game:**
    ```bash
    python main.py
    ```

### 🌐 Running the React Web Port (Dev)

1.  **Navigate to the Web Directory:**
    ```bash
    cd neonlink-web
    ```
2.  **Install Node Modules:**
    ```bash
    npm install
    ```
3.  **Start the Development Server:**
    ```bash
    npm run dev
    ```
4.  Open your browser to `http://localhost:5173`. Click **INITIALIZE SYSTEM** to grant audio/camera permissions and begin!

---
*Created as part of an exploration into AI-human collaborative interfaces.*
