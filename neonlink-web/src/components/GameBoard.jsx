// GameBoard.jsx
import React, { useEffect, useRef, useState, useCallback } from 'react';
import { TetrisEngine, GRID_WIDTH, GRID_HEIGHT } from '../game/TetrisEngine';
import KineticCamera from './KineticCamera';

const BLOCK_SIZE = 22;
const PLAY_WIDTH = GRID_WIDTH * BLOCK_SIZE;
const PLAY_HEIGHT = GRID_HEIGHT * BLOCK_SIZE;

export default function GameBoard() {
    const canvasRef = useRef(null);
    const engineRef = useRef(new TetrisEngine());

    // Audio Refs
    const bgmRef = useRef(null);
    const clearSoundRef = useRef(null);
    const dropSoundRef = useRef(null);
    const bombSoundRef = useRef(null);

    const [score, setScore] = useState(0);
    const [highScore, setHighScore] = useState(parseInt(localStorage.getItem('neonlink_hs') || '0'));
    const [vibe, setVibe] = useState(0.0);
    const [aiGesture, setAiGesture] = useState('NONE');
    const [isPaused, setIsPaused] = useState(false);
    const [hasStarted, setHasStarted] = useState(false); // New explicit start state
    const gameStartTimeRef = useRef(null);

    const lastTimeRef = useRef(performance.now());
    const fallTimeRef = useRef(0);
    const baseFallSpeed = 500; // ms
    const fistReleasedRef = useRef(true);
    const fistCooldownRef = useRef(0);

    // Load Audio
    useEffect(() => {
        bgmRef.current = new Audio('assets/bgm.wav');
        bgmRef.current.loop = true;
        bgmRef.current.volume = 0.5;

        clearSoundRef.current = new Audio('assets/clear.wav');
        dropSoundRef.current = new Audio('assets/drop.wav');
        bombSoundRef.current = new Audio('assets/bomb.wav');
    }, []);

    const playSound = (audioRef) => {
        if (audioRef.current) {
            audioRef.current.currentTime = 0;
            audioRef.current.play().catch(e => console.log("Audio play prevented:", e));
        }
    };

    const handleGesture = useCallback((gesture) => {
        setAiGesture(gesture);
        if (gesture !== 'CLOSED_FIST') {
            fistReleasedRef.current = true;
        }
    }, []);

    const startGame = () => {
        setHasStarted(true);
        if (gameStartTimeRef.current === null) {
            gameStartTimeRef.current = performance.now();
        }
        // Explicitly initialize AudioContext on user click
        if (bgmRef.current) {
            bgmRef.current.play().catch(console.error);
        }
    };

    // Keyboard Handle
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (!hasStarted) return;

            const engine = engineRef.current;

            if (e.key === 'p' || e.key === 'P') {
                setIsPaused(prev => !prev);
                return;
            }

            if (engine.gameOver && (e.key === 'r' || e.key === 'R')) {
                engineRef.current = new TetrisEngine();
                setScore(0);
                setVibe(0);
                fistReleasedRef.current = true;
                gameStartTimeRef.current = performance.now();
                if (bgmRef.current) bgmRef.current.play();
                return;
            }

            if (engine.gameOver || isPaused) return;

            let lines = 0;
            if (e.key === 'ArrowLeft') {
                engine.movePiece(-1, 0);
            } else if (e.key === 'ArrowRight') {
                engine.movePiece(1, 0);
            } else if (e.key === 'ArrowUp' || e.key.toLowerCase() === 'w') {
                engine.rotatePiece();
            } else if (e.key === 'ArrowDown') {
                playSound(dropSoundRef);
                lines = engine.movePiece(0, 1);
            }

            if (lines > 0) {
                setScore(engine.score);
                playSound(clearSoundRef);
            }

            setVibe(prev => Math.min(prev + 5, 100)); // Increase vibe on interaction
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isPaused, hasStarted]);

    // Main Game Loop using requestAnimationFrame
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return; // Prevent crash when on Splash Screen

        const ctx = canvas.getContext('2d');
        let requestID;

        const gameLoop = (time) => {
            const engine = engineRef.current;
            const deltaTime = time - lastTimeRef.current;
            lastTimeRef.current = time;

            if (hasStarted) {
                if (!isPaused && !engine.gameOver) {
                    fallTimeRef.current += deltaTime;
                    // --- Dynamic Speed & Danger Logic ---
                    let highestBlockRow = GRID_HEIGHT;
                    for (let r = 0; r < GRID_HEIGHT; r++) {
                        if (engine.grid[r].some(cell => cell !== null)) {
                            highestBlockRow = r;
                            break;
                        }
                    }

                    // 90% full is row 2 (since 0 is top, 20 is bottom. 20 * 0.1 = 2)
                    const isDanger = highestBlockRow <= 2;

                    // Base speed gets faster the longer the time playing. 
                    const elapsedSeconds = (time - (gameStartTimeRef.current || time)) / 1000;
                    // For every 30 seconds played, drop the interval by 50ms, cap at 100ms
                    let currentSpeed = Math.max(100, baseFallSpeed - (Math.floor(elapsedSeconds / 30) * 50));

                    if (isDanger) {
                        currentSpeed = 800; // Slow down drastically when in danger
                    }

                    if (fistCooldownRef.current > 0) {
                        fistCooldownRef.current -= deltaTime;
                    }

                    // Apply AI modifications
                    if (aiGesture === 'OPEN_PALM') {
                        currentSpeed *= 2.0; // Slow time
                    } else if (aiGesture === 'CLOSED_FIST' && fistReleasedRef.current && fistCooldownRef.current <= 0) {
                        fistReleasedRef.current = false;
                        fistCooldownRef.current = 1000; // 1000ms cooldown to prevent double slam
                        playSound(dropSoundRef);
                        const lines = engine.hardDrop();
                        if (lines > 0) {
                            playSound(clearSoundRef);
                        }
                        setScore(engine.score);
                        fallTimeRef.current = 0;
                    }

                    // Apply idle vibe decay
                    setVibe(prev => Math.max(0, prev - 0.2));

                    if (fallTimeRef.current > currentSpeed) {
                        fallTimeRef.current = 0;
                        engine.currentPiece.y += 1;
                        playSound(dropSoundRef);

                        if (!engine.validSpace(engine.currentPiece) && engine.currentPiece.y > 0) {
                            engine.currentPiece.y -= 1;
                            const lines = engine.lockPiece();
                            if (lines > 0) playSound(clearSoundRef);
                            setScore(engine.score);
                        }
                    }

                    // Handle Death trigger once
                    if (engine.gameOver && !engine.justDied) {
                        engine.justDied = true;
                        if (bgmRef.current) bgmRef.current.pause();
                        playSound(bombSoundRef);

                        if (engine.score > highScore) {
                            setHighScore(engine.score);
                            localStorage.setItem('neonlink_hs', engine.score);
                        }
                    }
                }
            }


            // -- DRAW ROUTINE -- //
            ctx.fillStyle = '#000000';
            ctx.fillRect(0, 0, PLAY_WIDTH, PLAY_HEIGHT);

            // Draw Grid blocks
            for (let i = 0; i < engine.grid.length; i++) {
                for (let j = 0; j < engine.grid[i].length; j++) {
                    if (engine.grid[i][j]) {
                        ctx.fillStyle = engine.grid[i][j];
                        ctx.fillRect(j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
                    }
                }
            }

            // Draw Active Piece
            if (engine.currentPiece && !engine.gameOver) {
                const shapePos = engine.convertShapeFormat(engine.currentPiece);
                ctx.fillStyle = engine.currentPiece.color;
                for (let i = 0; i < shapePos.length; i++) {
                    const { x, y } = shapePos[i];
                    if (y > -1) {
                        ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
                    }
                }
            }

            // Draw Grid Lines (Neon Vibe)
            ctx.strokeStyle = '#282828';
            ctx.lineWidth = 1;
            for (let i = 0; i <= GRID_HEIGHT; i++) {
                ctx.beginPath();
                ctx.moveTo(0, i * BLOCK_SIZE);
                ctx.lineTo(PLAY_WIDTH, i * BLOCK_SIZE);
                ctx.stroke();
            }
            for (let j = 0; j <= GRID_WIDTH; j++) {
                ctx.beginPath();
                ctx.moveTo(j * BLOCK_SIZE, 0);
                ctx.lineTo(j * BLOCK_SIZE, PLAY_HEIGHT);
                ctx.stroke();
            }

            // Draw Danger Pulse Overlay
            let highestBlockRow = GRID_HEIGHT;
            for (let r = 0; r < GRID_HEIGHT; r++) {
                if (engine.grid[r].some(cell => cell !== null)) {
                    highestBlockRow = r;
                    break;
                }
            }
            if (highestBlockRow <= 2 && !engine.gameOver) {
                // Pulse alpha between 0.0 and 0.3 based on time
                const pulseAlpha = (Math.sin(time / 200) + 1) / 2 * 0.3;
                ctx.fillStyle = `rgba(255, 0, 0, ${pulseAlpha})`;
                ctx.fillRect(0, 0, PLAY_WIDTH, PLAY_HEIGHT);
            }

            // Draw Game Over / Pause Overlays
            if (engine.gameOver || isPaused || !hasStarted) {
                ctx.fillStyle = 'rgba(0,0,0,0.7)';
                ctx.fillRect(0, 0, PLAY_WIDTH, PLAY_HEIGHT);

                ctx.fillStyle = engine.gameOver ? '#FF0000' : '#FFFFFF';
                ctx.font = 'bold 30px Courier Prime';
                ctx.textAlign = 'center';

                let overlayText = '';
                if (!hasStarted) overlayText = 'READY';
                else if (engine.gameOver) overlayText = 'GAME OVER';
                else if (isPaused) overlayText = 'PAUSED';

                ctx.fillText(overlayText, PLAY_WIDTH / 2, PLAY_HEIGHT / 2);

                if (engine.gameOver) {
                    ctx.fillStyle = '#FFFFFF';
                    ctx.font = '16px Courier Prime';
                    ctx.fillText('Press R to Restart', PLAY_WIDTH / 2, PLAY_HEIGHT / 2 + 40);
                }
            }

            requestID = requestAnimationFrame(gameLoop);
        };

        requestID = requestAnimationFrame(gameLoop);
        return () => cancelAnimationFrame(requestID);
    }, [aiGesture, isPaused, highScore, hasStarted]); // Added hasStarted to dependency array

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', height: '100vh', justifyContent: 'center' }}>
            {/* Title */}
            <h1 className="text-neon-cyan" style={{ fontSize: '2.5rem', marginBottom: '15px' }}>NEONLINK: KINETIC CORE</h1>

            {!hasStarted ? (
                <button
                    onClick={startGame}
                    className="border-neon-cyan text-neon-cyan"
                    style={{ padding: '20px 40px', background: '#000', fontSize: '24px', cursor: 'pointer', fontFamily: 'Courier Prime', marginTop: '50px' }}
                >
                    INITIALIZE SYSTEM
                </button>
            ) : (
                <div style={{ display: 'flex', gap: '50px', alignItems: 'flex-start' }}>
                    {/* Play Area */}
                    <div style={{ position: 'relative' }}>
                        <canvas
                            ref={canvasRef}
                            width={PLAY_WIDTH}
                            height={PLAY_HEIGHT}
                            className="border-neon-cyan"
                            style={{ display: 'block' }}
                        />
                    </div>

                    {/* HUD UI */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', width: '250px' }}>

                        <KineticCamera onGesture={handleGesture} />

                        <div>
                            <h2 className="text-neon-cyan">SCORE: {score}</h2>
                            <h2 className="text-neon-cyan">HIGH: {highScore}</h2>
                            <h3 style={{ color: aiGesture !== 'NONE' ? '#00FF00' : '#FFFFFF', marginTop: '10px' }}>
                                AI: {aiGesture}
                            </h3>
                        </div>

                        <div style={{ marginTop: '10px' }}>
                            <h3 className="text-neon-pink" style={{ marginBottom: '5px' }}>VIBE</h3>
                            <div style={{ width: '30px', height: '120px', background: '#282828', position: 'relative' }}>
                                <div style={{
                                    position: 'absolute',
                                    bottom: 0,
                                    width: '100%',
                                    height: `${vibe}%`,
                                    background: `rgb(${Math.floor(255 * (vibe / 100))}, 0, 255)`,
                                    transition: 'height 0.2s, background 0.2s'
                                }} />
                            </div>
                        </div>

                        <div style={{ marginTop: '10px', fontSize: '14px', lineHeight: '1.4' }}>
                            <h4 style={{ color: '#00FFFF' }}>CONTROLS</h4>
                            <div>Arrows/W: Move/Rotate</div>
                            <div>P       : Pause</div>
                            <div>AI OPEN : Slow Time</div>
                            <div>AI FIST : Kinetic Slam</div>
                        </div>

                    </div>
                </div>
            )}
        </div>
    );
}
