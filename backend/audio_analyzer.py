import librosa
import numpy as np
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """Analyzes audio for beat detection and tempo."""
    
    def __init__(self):
        self.sr = None
        self.y = None
        self.beat_times = np.array([])
        self.beat_strengths = np.array([])
        
    def analyze_audio(self, audio_path: str, sr: int = 22050) -> Dict:
        """
        Analyze audio for beat detection and tempo.
        
        Args:
            audio_path: Path to audio file or video file
            sr: Sample rate (default 22050 Hz)
            
        Returns:
            Dictionary containing beat analysis results
        """
        try:
            logger.info(f"Loading audio from: {audio_path}")
            
            # Load audio file
            self.y, self.sr = librosa.load(audio_path, sr=sr)
            duration = librosa.get_duration(y=self.y, sr=self.sr)
            
            logger.info(f"Audio loaded - Duration: {duration:.2f}s, SR: {self.sr}")
            
            # Detect beats and tempo
            tempo, beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sr)
            tempo = float(np.asarray(tempo).squeeze())
            
            # Convert beat frames to time
            beat_times = librosa.frames_to_time(beat_frames, sr=self.sr)
            
            # Detect onsets (transient events)
            onsets = librosa.onset.onset_detect(y=self.y, sr=self.sr, units='time')
            
            # Detect major and minor beats using onset strength
            onset_env = librosa.onset.onset_strength(y=self.y, sr=self.sr)
            
            # Calculate beat strengths
            beat_strengths = self._calculate_beat_strengths(beat_frames, onset_env)

            # Cache for utility methods
            self.beat_times = beat_times
            self.beat_strengths = beat_strengths
            
            # Separate major and minor beats
            major_beats, minor_beats = self._categorize_beats(
                beat_times, beat_strengths
            )
            
            # Detect sections (structural analysis)
            sections = self._detect_sections()
            
            return {
                'audio_path': audio_path,
                'duration': float(duration),
                'sample_rate': int(self.sr),
                'tempo': tempo,
                'beats': {
                    'all': beat_times.tolist(),
                    'major': major_beats,
                    'minor': minor_beats,
                    'strengths': beat_strengths.tolist()
                },
                'onsets': onsets.tolist(),
                'sections': sections
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audio: {e}")
            raise
    
    def _calculate_beat_strengths(self, beats: np.ndarray, onset_env: np.ndarray) -> np.ndarray:
        """Calculate strength of each beat based on onset strength."""
        if len(beats) == 0:
            return np.array([])

        strengths = np.zeros(len(beats))
        
        for i, beat in enumerate(beats):
            # Get strength window around beat
            window_start = max(0, beat - 2)
            window_end = min(len(onset_env), beat + 2)
            strengths[i] = np.mean(onset_env[window_start:window_end])
        
        return strengths
    
    def _categorize_beats(
        self, beat_times: np.ndarray, beat_strengths: np.ndarray
    ) -> tuple:
        """Categorize beats into major and minor based on strength."""
        if len(beat_times) == 0 or len(beat_strengths) == 0:
            return [], []

        threshold = np.mean(beat_strengths)
        std = np.std(beat_strengths)
        major_threshold = threshold + 0.5 * std
        
        major_beats = []
        minor_beats = []
        
        for time, strength in zip(beat_times, beat_strengths):
            if strength >= major_threshold:
                major_beats.append({
                    'timestamp': float(time),
                    'strength': float(strength)
                })
            else:
                minor_beats.append({
                    'timestamp': float(time),
                    'strength': float(strength)
                })
        
        return major_beats, minor_beats
    
    def _detect_sections(self) -> List[Dict]:
        """Detect structural sections in audio."""
        if self.y is None:
            return []
        
        try:
            # Compute chroma features
            chroma = librosa.feature.chroma_cqt(y=self.y, sr=self.sr)

            if chroma.shape[1] < 4:
                return []

            # Find segment boundaries using agglomerative segmentation
            k = min(8, max(2, chroma.shape[1] // 30))
            bound_frames = librosa.segment.agglomerative(chroma, k=k)

            # Ensure timeline has start and end anchors
            end_frame = chroma.shape[1] - 1
            bound_frames = np.unique(
                np.concatenate(([0], np.asarray(bound_frames), [end_frame]))
            )
            bound_times = librosa.frames_to_time(bound_frames, sr=self.sr)
            
            sections = []
            for i, bound_time in enumerate(bound_times[:-1]):
                sections.append({
                    'section': i,
                    'start_time': float(bound_time),
                    'end_time': float(bound_times[i + 1]),
                    'duration': float(bound_times[i + 1] - bound_time)
                })
            
            return sections
            
        except Exception as e:
            logger.warning(f"Could not detect sections: {e}")
            return []
    
    def get_beat_at_timestamp(self, timestamp: float, tolerance: float = 0.1) -> Dict:
        """
        Get beat information at a specific timestamp.
        
        Args:
            timestamp: Time in seconds
            tolerance: Tolerance window in seconds
            
        Returns:
            Beat information or None
        """
        if self.beat_times is None or len(self.beat_times) == 0:
            return None
        
        # Find nearest beat
        diffs = np.abs(self.beat_times - timestamp)
        min_idx = np.argmin(diffs)
        
        if diffs[min_idx] <= tolerance:
            is_major = False
            if self.beat_strengths is not None and len(self.beat_strengths) > 0:
                is_major = bool(self.beat_strengths[min_idx] > np.mean(self.beat_strengths))

            return {
                'timestamp': float(self.beat_times[min_idx]),
                'distance': float(diffs[min_idx]),
                'is_major': is_major
            }
        
        return None
