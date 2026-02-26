import cv2
import mediapipe as mp
import threading
import time

class HandTracker:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        
        # MediaPipe Tasks API setup
        BaseOptions = mp.tasks.BaseOptions
        self.HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path='assets/hand_landmarker.task'),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=1)
            
        self.landmarker = self.HandLandmarker.create_from_options(options)
        
        self.running = False
        self.thread = None
        self.current_frame = None
        self.current_gesture = "NONE"
        
        # Thread safety lock
        self.lock = threading.Lock()
        
    def start(self):
        """Starts the camera feed and gesture recognition in a background thread."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_index}.")
            return False
            
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        return True
        
    def stop(self):
        """Stops the background thread and releases the camera."""
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
            
    def _update(self):
        """The loop running in the background thread."""
        while self.running:
            success, img = self.cap.read()
            if not success:
                time.sleep(0.1)
                continue
                
            # Flip image horizontally for natural (mirror) viewing
            img = cv2.flip(img, 1)
            
            # Convert BGR to RGB for mediapipe
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
            
            # Milliseconds timestamp
            frame_timestamp_ms = int(time.time() * 1000)
            
            try:
                results = self.landmarker.detect_for_video(mp_image, frame_timestamp_ms)
            except Exception as e:
                time.sleep(0.01)
                continue
            
            gesture = "NONE"
            
            if results.hand_landmarks:
                for hand_lms in results.hand_landmarks:
                    # Draw manual landmarks (cyan color)
                    for lm in hand_lms:
                        x, y = int(lm.x * img.shape[1]), int(lm.y * img.shape[0])
                        cv2.circle(img, (x, y), 4, (255, 255, 0), -1)
                    
                    gesture = self._detect_gesture(hand_lms)
            
            with self.lock:
                self.current_frame = img
                self.current_gesture = gesture
                
            # Sleep slightly to prevent 100% CPU usage
            time.sleep(0.01)
            
    def _detect_gesture(self, hand_landmarks):
        """
        Determines if the hand is OPEN_PALM, CLOSED_FIST, or THUMB_UP based on finger landmarks.
        """
        finger_tips = [4, 8, 12, 16, 20] # Thumb, Index, Middle, Ring, Pinky
        finger_pips = [3, 6, 10, 14, 18] # IP for thumb, PIP for others
        finger_mcps = [2, 5, 9, 13, 17]  # MCP for base comparison
        
        # Check fingers 1 to 4 (Index to Pinky)
        fingers_open = []
        for i in range(1, 5):
            # A finger is open if its tip is significantly higher (lower y) than its PIP
            # AND its PIP is higher than its MCP
            tip_y = hand_landmarks[finger_tips[i]].y
            pip_y = hand_landmarks[finger_pips[i]].y
            mcp_y = hand_landmarks[finger_mcps[i]].y
            
            is_open = tip_y < pip_y and pip_y < mcp_y
            fingers_open.append(is_open)
            
        open_count = sum(fingers_open)
        
        # Thumb Logic:
        # A thumb is "up" if its tip is higher than its IP joint.
        thumb_tip_y = hand_landmarks[finger_tips[0]].y
        thumb_ip_y = hand_landmarks[finger_pips[0]].y
        thumb_mcp_y = hand_landmarks[finger_mcps[0]].y
        
        # Also ensure the thumb is actually extended (distance between tip and mcp is large enough)
        thumb_extended = abs(thumb_tip_y - thumb_ip_y) > 0.05
        thumb_is_up = thumb_tip_y < thumb_ip_y and thumb_extended

        if open_count >= 3:
            return "OPEN_PALM"
            
        if open_count == 0:
            # If all 4 fingers are closed, we check the thumb to distinguish FIST vs THUMB_UP
            # For a fist, the thumb is usually tucked in (y distance is very small between tip and IP)
            # or pointing somewhat sideways/downwards.
            
            # If the thumb is definitively pointing up and extended
            if thumb_is_up and thumb_tip_y < hand_landmarks[finger_mcps[1]].y:
                return "THUMB_UP"
                
            return "CLOSED_FIST"
            
        return "NONE"
        
    def get_data(self):
        """Returns the latest frame and detected gesture safely."""
        with self.lock:
            # Return a copy of the frame or None, and the string gesture
            return (self.current_frame.copy() if self.current_frame is not None else None), self.current_gesture

if __name__ == "__main__":
    # Quick test
    tracker = HandTracker()
    if tracker.start():
        print("Camera started. Press Ctrl+C in terminal to stop.")
        try:
            while True:
                frame, gesture = tracker.get_data()
                if frame is not None:
                    cv2.putText(frame, f"Gesture: {gesture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow("Test AI Feed", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                time.sleep(0.03)
        except KeyboardInterrupt:
            pass
        finally:
            tracker.stop()
            cv2.destroyAllWindows()
