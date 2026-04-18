import numpy as np
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyncEngine:
    """Synchronizes video segments with audio beats."""
    
    def __init__(self):
        self.video_analysis = None
        self.audio_analysis = None
        self.sync_results = None
        
    def synchronize(
        self, 
        video_analysis: Dict, 
        audio_analysis: Dict,
        snap_mode: str = 'major',
        tolerance: float = 0.1
    ) -> Dict:
        """
        Synchronize video events with audio beats.
        
        Args:
            video_analysis: Results from VideoAnalyzer
            audio_analysis: Results from AudioAnalyzer
            snap_mode: 'major' (snap to major beats), 'minor' (snap to minor beats), 'all' (any beat)
            tolerance: Tolerance in seconds for snapping
            
        Returns:
            Dictionary containing synchronized events
        """
        self.video_analysis = video_analysis
        self.audio_analysis = audio_analysis
        
        logger.info(f"Starting synchronization with snap_mode={snap_mode}, tolerance={tolerance}")
        
        # Get beat timeline based on snap mode
        beat_timeline = self._get_beat_timeline(snap_mode)
        
        # Synchronize each video event type
        sync_results = {
            'video_path': video_analysis['video_path'],
            'audio_path': audio_analysis['audio_path'],
            'sync_config': {
                'snap_mode': snap_mode,
                'tolerance': tolerance
            },
            'synchronized_events': {}
        }
        
        # Sync large motions
        sync_results['synchronized_events']['large_motions'] = self._sync_events(
            video_analysis['large_motions'],
            beat_timeline,
            tolerance
        )
        
        # Sync small motions
        sync_results['synchronized_events']['small_motions'] = self._sync_events(
            video_analysis['small_motions'],
            beat_timeline,
            tolerance
        )
        
        # Sync scene changes
        sync_results['synchronized_events']['scene_changes'] = self._sync_events(
            video_analysis['scene_changes'],
            beat_timeline,
            tolerance
        )
        
        # Sync camera movements
        sync_results['synchronized_events']['camera_movements'] = self._sync_events(
            video_analysis['camera_movements'],
            beat_timeline,
            tolerance
        )
        
        # Generate timeline with all events
        sync_results['timeline'] = self._generate_timeline(
            sync_results['synchronized_events'],
            beat_timeline,
            video_analysis['duration']
        )
        
        self.sync_results = sync_results
        logger.info("Synchronization complete")
        
        return sync_results
    
    def _get_beat_timeline(self, snap_mode: str) -> List[float]:
        """Get list of beat timestamps based on snap mode."""
        beats = self.audio_analysis['beats']

        if snap_mode == 'major':
            timeline = [b['timestamp'] for b in beats['major']]
        elif snap_mode == 'minor':
            timeline = [b['timestamp'] for b in beats['minor']]
        else:  # 'all'
            timeline = beats['all']

        # Fallback: avoid empty timeline causing downstream failures
        if not timeline:
            timeline = beats.get('all', [])

        if not timeline:
            timeline = [0.0]

        return timeline
    
    def _sync_events(
        self, 
        events: List[Dict], 
        beat_timeline: List[float],
        tolerance: float
    ) -> List[Dict]:
        """
        Snap events to nearest beat within tolerance.
        
        Args:
            events: List of video events with timestamps
            beat_timeline: List of beat timestamps
            tolerance: Snapping tolerance in seconds
            
        Returns:
            List of synchronized events with beat information
        """
        synchronized = []
        
        for event in events:
            timestamp = event['timestamp']
            
            # Find nearest beat
            beat_diffs = np.abs(np.array(beat_timeline) - timestamp)
            nearest_idx = np.argmin(beat_diffs)
            distance = beat_diffs[nearest_idx]
            
            # Check if within tolerance
            if distance <= tolerance:
                sync_event = event.copy()
                sync_event['snapped_to_beat'] = True
                sync_event['nearest_beat_timestamp'] = float(beat_timeline[nearest_idx])
                sync_event['snap_distance'] = float(distance)
                sync_event['beat_index'] = int(nearest_idx)
                synchronized.append(sync_event)
            else:
                sync_event = event.copy()
                sync_event['snapped_to_beat'] = False
                sync_event['nearest_beat_timestamp'] = float(beat_timeline[nearest_idx])
                sync_event['snap_distance'] = float(distance)
                sync_event['beat_index'] = int(nearest_idx) if distance < 2 * tolerance else None
                synchronized.append(sync_event)
        
        return synchronized
    
    def _generate_timeline(
        self, 
        synchronized_events: Dict,
        beat_timeline: List[float],
        duration: float
    ) -> List[Dict]:
        """
        Generate comprehensive timeline with all events and beats.
        
        Args:
            synchronized_events: Dictionary of synchronized event lists
            beat_timeline: List of beat timestamps
            duration: Video duration in seconds
            
        Returns:
            Chronologically ordered timeline
        """
        timeline = []
        
        # Add all beats
        for i, beat_time in enumerate(beat_timeline):
            timeline.append({
                'time': beat_time,
                'type': 'beat',
                'beat_index': i,
                'data': None
            })
        
        # Add all events
        for event_type, events in synchronized_events.items():
            for event in events:
                timeline.append({
                    'time': event['timestamp'],
                    'type': event_type,
                    'snapped': event.get('snapped_to_beat', False),
                    'snap_distance': event.get('snap_distance', None),
                    'data': event
                })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['time'])
        
        return timeline
    
    def adjust_sync_tolerance(self, new_tolerance: float) -> Dict:
        """
        Re-synchronize with a different tolerance value.
        
        Args:
            new_tolerance: New tolerance in seconds
            
        Returns:
            Updated synchronization results
        """
        if self.sync_results is None:
            raise ValueError("No synchronization results available")
        
        snap_mode = self.sync_results['sync_config']['snap_mode']
        
        return self.synchronize(
            self.video_analysis,
            self.audio_analysis,
            snap_mode,
            new_tolerance
        )
    
    def get_sync_statistics(self) -> Dict:
        """
        Calculate statistics about synchronization quality.
        
        Returns:
            Dictionary with sync statistics
        """
        if self.sync_results is None:
            raise ValueError("No synchronization results available")
        
        stats = {
            'total_events': 0,
            'snapped_events': 0,
            'snap_rate': 0.0,
            'average_snap_distance': 0.0,
            'max_snap_distance': 0.0,
            'by_type': {}
        }
        
        all_snap_distances = []
        
        for event_type, events in self.sync_results['synchronized_events'].items():
            type_snapped = sum(1 for e in events if e.get('snapped_to_beat', False))
            stats['by_type'][event_type] = {
                'total': len(events),
                'snapped': type_snapped,
                'snap_rate': type_snapped / len(events) if events else 0
            }
            
            stats['total_events'] += len(events)
            stats['snapped_events'] += type_snapped
            
            # Collect snap distances
            for event in events:
                distance = event.get('snap_distance')
                if distance is not None:
                    all_snap_distances.append(distance)
        
        if all_snap_distances:
            stats['average_snap_distance'] = float(np.mean(all_snap_distances))
            stats['max_snap_distance'] = float(np.max(all_snap_distances))
        
        if stats['total_events'] > 0:
            stats['snap_rate'] = stats['snapped_events'] / stats['total_events']
        
        return stats
    
    def export_timeline_as_json(self) -> Dict:
        """Export synchronization results as JSON-compatible dictionary."""
        if self.sync_results is None:
            raise ValueError("No synchronization results available")
        
        return self.sync_results
    
    def export_timeline_as_csv(self) -> str:
        """Export timeline as CSV format."""
        if self.sync_results is None:
            raise ValueError("No synchronization results available")
        
        timeline = self.sync_results['timeline']
        
        csv_lines = ['time,type,beat_index,snapped_to_beat,snap_distance,confidence']
        
        for entry in timeline:
            time = entry['time']
            event_type = entry['type']
            beat_index = entry.get('beat_index', '')
            snapped = entry.get('snapped', '') if entry['type'] != 'beat' else 'N/A'
            snap_distance = entry.get('snap_distance', '') if entry['type'] != 'beat' else 'N/A'
            
            confidence = ''
            if entry['data'] and 'confidence' in entry['data']:
                confidence = entry['data']['confidence']
            
            csv_lines.append(
                f"{time},{event_type},{beat_index},{snapped},{snap_distance},{confidence}"
            )
        
        return '\n'.join(csv_lines)
