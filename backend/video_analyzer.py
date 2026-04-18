import cv2
import numpy as np
from typing import List, Dict, Optional
import logging
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoAnalyzer:
    """Analyzes video for motion, scene changes, and camera movements."""
    
    def __init__(self):
        self.prev_gray_for_global = None
        self.prev_gray_for_small = None
        self.prev_gray_for_scene = None
        self.prev_gray_for_camera = None
        
    def analyze_video(self, video_path: str, sample_rate: int = 2) -> Dict:
        """
        Analyze entire video for movements, scene changes, and camera motion.
        
        Args:
            video_path: Path to video file
            sample_rate: Process every Nth frame to speed up analysis
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")

            fps = cap.get(cv2.CAP_PROP_FPS)
            if not fps or fps <= 0:
                fps = 30.0

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Reset trackers for each new analysis run
            self.prev_gray_for_global = None
            self.prev_gray_for_small = None
            self.prev_gray_for_scene = None
            self.prev_gray_for_camera = None
            
            frame_count = 0
            large_motions = []
            small_motions = []
            scene_changes = []
            camera_movements = []
            
            logger.info(f"Starting video analysis: {video_path}")
            logger.info(f"FPS: {fps}, Total frames: {total_frames}")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                if frame_count % sample_rate == 0:
                    timestamp = frame_count / fps
                    
                    # Detect large motions (body movements)
                    large_motion = self._detect_large_motion(frame)
                    if large_motion:
                        large_motions.append({
                            'frame': frame_count,
                            'timestamp': timestamp,
                            'confidence': large_motion['confidence'],
                            'type': large_motion['type']
                        })
                    
                    # Detect small motions (hand, facial movements)
                    small_motion = self._detect_small_motion(frame, large_motion)
                    if small_motion:
                        small_motions.append({
                            'frame': frame_count,
                            'timestamp': timestamp,
                            'confidence': small_motion['confidence'],
                            'type': small_motion['type']
                        })
                    
                    # Detect scene changes
                    scene_change = self._detect_scene_change(frame)
                    if scene_change:
                        scene_changes.append({
                            'frame': frame_count,
                            'timestamp': timestamp,
                            'confidence': scene_change['confidence'],
                            'magnitude': scene_change['magnitude']
                        })
                    
                    # Detect camera movements
                    camera_movement = self._detect_camera_movement(frame)
                    if camera_movement:
                        camera_movements.append({
                            'frame': frame_count,
                            'timestamp': timestamp,
                            'type': camera_movement['type'],
                            'magnitude': camera_movement['magnitude']
                        })
                
                frame_count += 1
                if frame_count % 100 == 0:
                    logger.info(f"Processed {frame_count}/{total_frames} frames")
            
            cap.release()
            
            return {
                'video_path': video_path,
                'fps': fps,
                'total_frames': total_frames,
                'duration': (total_frames / fps) if total_frames > 0 else 0.0,
                'large_motions': large_motions,
                'small_motions': small_motions,
                'scene_changes': scene_changes,
                'camera_movements': camera_movements
            }
            
        except Exception as e:
            logger.error(f"Error analyzing video: {e}")
            raise
    
    def _detect_large_motion(self, frame: np.ndarray) -> Optional[Dict]:
        """Detect large/global motion using frame differencing."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.prev_gray_for_global is None:
            self.prev_gray_for_global = gray
            return None

        diff = cv2.absdiff(self.prev_gray_for_global, gray)
        motion_score = float(np.mean(diff) / 255.0)

        self.prev_gray_for_global = gray

        if motion_score > 0.08:
            return {
                'confidence': min(motion_score * 3.0, 1.0),
                'type': 'global_motion'
            }

        return None
    
    def _detect_small_motion(self, frame: np.ndarray, large_motion: Dict = None) -> Optional[Dict]:
        """Detect small local motions (hands, facial features)."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.prev_gray_for_small is None:
            self.prev_gray_for_small = gray
            return None
        
        # Calculate optical flow for motion detection
        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray_for_small, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        # Calculate magnitude and angle
        mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        
        # Detect local maxima (small motions)
        mean_mag = float(np.mean(mag))
        if mean_mag > 0.35 and (large_motion is None or large_motion.get('confidence', 0.0) < 0.4):
            self.prev_gray_for_small = gray
            return {
                'confidence': min(mean_mag / 3.0, 1.0),
                'type': 'local_motion'
            }
        
        self.prev_gray_for_small = gray
        return None
    
    def _detect_scene_change(self, frame: np.ndarray) -> Optional[Dict]:
        """Detect scene/shot changes using histogram comparison."""
        current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.prev_gray_for_scene is None:
            self.prev_gray_for_scene = current_gray
            return None
        
        # Compute histogram
        hist_current = cv2.calcHist([current_gray], [0], None, [64], [0, 256])
        hist_previous = cv2.calcHist([self.prev_gray_for_scene], [0], None, [64], [0, 256])
        
        # Normalize histograms
        cv2.normalize(hist_current, hist_current)
        cv2.normalize(hist_previous, hist_previous)
        
        # Compare histograms
        diff = float(cv2.compareHist(hist_current, hist_previous, cv2.HISTCMP_BHATTACHARYYA))
        
        self.prev_gray_for_scene = current_gray
        
        if diff > 0.45:  # Threshold for scene change
            return {
                'confidence': min(diff, 1.0),
                'magnitude': diff
            }
        
        return None
    
    def _detect_camera_movement(self, frame: np.ndarray) -> Optional[Dict]:
        """Detect camera movements (pan, zoom, tilt)."""
        current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.prev_gray_for_camera is None:
            self.prev_gray_for_camera = current_gray
            return None

        # Track corners using Lucas-Kanade optical flow
        prev_points = cv2.goodFeaturesToTrack(
            self.prev_gray_for_camera,
            maxCorners=200,
            qualityLevel=0.01,
            minDistance=7,
            blockSize=7
        )

        if prev_points is None:
            self.prev_gray_for_camera = current_gray
            return None

        next_points, status, _ = cv2.calcOpticalFlowPyrLK(
            self.prev_gray_for_camera,
            current_gray,
            prev_points,
            None
        )

        if next_points is None or status is None:
            self.prev_gray_for_camera = current_gray
            return None

        status_mask = status.reshape(-1) == 1
        if int(np.sum(status_mask)) < 10:
            self.prev_gray_for_camera = current_gray
            return None

        valid_prev = prev_points[status_mask].reshape(-1, 2)
        valid_next = next_points[status_mask].reshape(-1, 2)

        movement = np.mean(valid_next - valid_prev, axis=0)
        magnitude = float(np.linalg.norm(movement))

        self.prev_gray_for_camera = current_gray

        if magnitude > 1.5:
            movement_type = 'pan' if abs(movement[0]) > abs(movement[1]) else 'tilt'
            return {
                'type': movement_type,
                'magnitude': magnitude
            }
        
        return None
