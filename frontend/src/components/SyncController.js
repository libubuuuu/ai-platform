import React, { useState } from 'react';
import axios from 'axios';
import API_URL from '../config';
import './SyncController.css';

const SyncController = ({ jobId, videoData, audioData, onSyncComplete }) => {
  const [snapMode, setSnapMode] = useState('major');
  const [tolerance, setTolerance] = useState(0.1);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);

  const handleSync = async () => {
    try {
      setSyncing(true);
      setProgress(0);
      setError(null);

      setProgress(30);

      const response = await axios.post(`${API_URL}/synchronize`, null, {
        params: {
          job_id: jobId,
          snap_mode: snapMode,
          tolerance: tolerance,
        },
      });

      setProgress(100);

      onSyncComplete({
        jobId: response.data.job_id,
        statistics: response.data.statistics,
        timelineLength: response.data.timeline_length,
        snapMode,
        tolerance,
      });

    } catch (err) {
      setError(err.message || 'Failed to synchronize');
      console.error('Sync error:', err);
    } finally {
      setSyncing(false);
    }
  };

  const handleToleranceChange = (e) => {
    const value = parseFloat(e.target.value);
    if (!isNaN(value) && value >= 0) {
      setTolerance(value);
    }
  };

  return (
    <div className="sync-controller card">
      <h2>🔗 Synchronize Video & Audio</h2>
      <p className="subtitle">Configure synchronization settings</p>

      <div className="settings-grid">
        <div className="setting-group">
          <label>Snap Mode</label>
          <div className="snap-options">
            <button
              className={`snap-btn ${snapMode === 'major' ? 'active' : ''}`}
              onClick={() => setSnapMode('major')}
              disabled={syncing}
            >
              Major Beats Only
            </button>
            <button
              className={`snap-btn ${snapMode === 'minor' ? 'active' : ''}`}
              onClick={() => setSnapMode('minor')}
              disabled={syncing}
            >
              Minor Beats
            </button>
            <button
              className={`snap-btn ${snapMode === 'all' ? 'active' : ''}`}
              onClick={() => setSnapMode('all')}
              disabled={syncing}
            >
              All Beats
            </button>
          </div>
          <p className="setting-description">
            {snapMode === 'major' && 'Snap video events to strong beats (recommended)'}
            {snapMode === 'minor' && 'Snap video events to minor beat subdivisions'}
            {snapMode === 'all' && 'Snap video events to any detected beat'}
          </p>
        </div>

        <div className="setting-group">
          <label>Tolerance (seconds)</label>
          <div className="tolerance-control">
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={tolerance}
              onChange={handleToleranceChange}
              disabled={syncing}
              className="tolerance-slider"
            />
            <input
              type="number"
              min="0"
              max="1"
              step="0.05"
              value={tolerance}
              onChange={handleToleranceChange}
              disabled={syncing}
              className="tolerance-input"
            />
          </div>
          <p className="setting-description">
            Maximum distance (in seconds) to snap events to beats. Lower = stricter alignment.
          </p>
        </div>
      </div>

      <div className="info-cards">
        <div className="info-card">
          <h4>Video Data</h4>
          <p>{videoData.large_motions} large motions</p>
          <p>{videoData.small_motions} small motions</p>
          <p>{videoData.scene_changes} scene changes</p>
          <p>{videoData.camera_movements} camera movements</p>
        </div>

        <div className="info-card">
          <h4>Audio Data</h4>
          <p>Tempo: {audioData.tempo.toFixed(0)} BPM</p>
          <p>{audioData.major_beats} major beats</p>
          <p>{audioData.minor_beats} minor beats</p>
          <p>{audioData.sections} sections</p>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {syncing && (
        <div className="syncing-status">
          <div className="spinner"></div>
          <p>Synchronizing...</p>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      )}

      <button
        className="button button-primary sync-button"
        onClick={handleSync}
        disabled={syncing}
      >
        {syncing ? 'Synchronizing...' : 'Start Synchronization'}
      </button>
    </div>
  );
};

export default SyncController;
