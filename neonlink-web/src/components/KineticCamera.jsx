import { useEffect, useRef, useState } from 'react';
import { FilesetResolver, GestureRecognizer } from '@mediapipe/tasks-vision';

export default function KineticCamera({ onGesture }) {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [recognizer, setRecognizer] = useState(null);
    const [cameraEnabled, setCameraEnabled] = useState(false);

    useEffect(() => {
        // Initialize MediaPipe Tasks Vision GestureRecognizer
        const initializeRecognizer = async () => {
            try {
                const vision = await FilesetResolver.forVisionTasks(
                    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3/wasm"
                );

                const gestureRecognizer = await GestureRecognizer.createFromOptions(vision, {
                    baseOptions: {
                        modelAssetPath: "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task",
                        delegate: "GPU"
                    },
                    runningMode: "VIDEO",
                    numHands: 1
                });
                setRecognizer(gestureRecognizer);
            } catch (e) {
                console.error("WASM Load Error: ", e);
            }
        };

        initializeRecognizer();
    }, []);

    const enableCamera = async () => {
        if (!recognizer) return;
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                // Explicitly tell the video to play
                videoRef.current.play().catch(e => console.error("Video play failed", e));
            }
        } catch (err) {
            console.error("Failed to access webcam:", err);
        }
    };

    const handleVideoLoad = () => {
        setCameraEnabled(true);
        predictWebcam();
    };

    const predictWebcam = async () => {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        if (!video || !canvas || !recognizer) return;

        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        console.log("Canvas setup size:", canvas.width, "x", canvas.height); // Log to trigger prediction loop manually if needed later

        let lastVideoTime = -1;

        const renderLoop = (now, metadata) => {
            if (!video || !recognizer) return;

            // Dynamically sync canvas size (videoWidth can be 0 initially)
            if (video.videoWidth > 0 && canvas.width !== video.videoWidth) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            }

            if (video.currentTime !== lastVideoTime && canvas.width > 0) {
                lastVideoTime = video.currentTime;

                // 1. ALWAYS draw the raw webcam feed first, regardless of AI status
                ctx.save();
                ctx.scale(-1, 1);
                ctx.translate(-canvas.width, 0);
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                // 2. Attempt AI recognition
                try {
                    // Use metadata timestamp if available from modern callback, otherwise fallback
                    const timestampMs = metadata ? metadata.presentationTime : performance.now();
                    const results = recognizer.recognizeForVideo(video, timestampMs);

                    let detectedState = "NONE";

                    if (results && results.gestures && results.gestures.length > 0) {
                        const categoryName = results.gestures[0][0].categoryName;
                        const score = results.gestures[0][0].score;

                        if (score > 0.6) {
                            if (categoryName === "Open_Palm") detectedState = "OPEN_PALM";
                            else if (categoryName === "Closed_Fist") detectedState = "CLOSED_FIST";
                            else if (categoryName === "Thumb_Up") detectedState = "THUMB_UP";
                        }

                        // Draw hand landmarks (Neon pink overlay)
                        if (results.landmarks) {
                            for (const landmarks of results.landmarks) {
                                ctx.fillStyle = '#FF00FF';
                                for (const pt of landmarks) {
                                    const x = pt.x * canvas.width;
                                    const y = pt.y * canvas.height;
                                    ctx.beginPath();
                                    ctx.arc(x, y, 5, 0, 2 * Math.PI);
                                    ctx.fill();
                                }
                            }
                        }
                    }

                    if (onGesture) {
                        onGesture(detectedState);
                    }
                } catch (e) {
                    // Fail silently so the video feed doesn't freeze
                    // console.error("Frame recognition expected warning:", e);
                }
                ctx.restore(); // Restore context after all drawing is complete
            }

            // Loop using the modern video API
            if (video.requestVideoFrameCallback) {
                video.requestVideoFrameCallback(renderLoop);
            } else {
                requestAnimationFrame(() => renderLoop(performance.now(), null));
            }
        };

        if (video.requestVideoFrameCallback) {
            video.requestVideoFrameCallback(renderLoop);
        } else {
            requestAnimationFrame(() => renderLoop(performance.now(), null));
        }
    };

    return (
        <div style={{ position: 'relative', width: '240px', height: '180px', border: '2px solid #FF00FF', boxShadow: '0 0 10px #FF00FF' }}>
            <video
                ref={videoRef}
                style={{ display: 'none' }}
                autoPlay
                playsInline
                muted
                onLoadedData={handleVideoLoad}
            />
            <canvas
                ref={canvasRef}
                style={{ width: '100%', height: '100%', display: cameraEnabled ? 'block' : 'none' }}
            />
            {!cameraEnabled && (
                <button
                    onClick={enableCamera}
                    disabled={!recognizer}
                    style={{ width: '100%', height: '100%', background: '#000', color: '#00FFFF', border: 'none', fontFamily: 'Courier Prime', fontSize: '16px', cursor: 'pointer' }}
                >
                    {recognizer ? "INITIALIZE GHOST LINK" : "LOADING AI..."}
                </button>
            )}
        </div>
    );
}
