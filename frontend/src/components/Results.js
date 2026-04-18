import React, { useState } from 'react';
import axios from 'axios';
import API_URL from '../config';
import './Results.css';

const Results = ({ syncData, videoData, audioData, onReset }) => {
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState(null);

  const handleExportFile = async (endpoint, filename, errorMessage) => {
    try {
      setExporting(true);
      setExportError(null);

      const response = await axios.get(endpoint, {
        responseType: 'blob',
      });

      downloadFile(response.data, getFilenameFromResponse(response, filename));
    } catch (err) {
      setExportError(errorMessage);
      console.error(err);
    } finally {
      setExporting(false);
    }
  };

  const handleExportJSON = () =>
    handleExportFile(
      `${API_URL}/export/${syncData.jobId}/json`,
      `sync_results_${syncData.jobId}.json`,
      'Failed to export JSON'
    );

  const handleExportCSV = () =>
    handleExportFile(
      `${API_URL}/export/${syncData.jobId}/csv`,
      `timeline_${syncData.jobId}.csv`,
      'Failed to export CSV'
    );

  const handleExportImage = () =>
    handleExportFile(
      `${API_URL}/export/${syncData.jobId}/image`,
      `sync_summary_${syncData.jobId}.png`,
      'Failed to export PNG image'
    );

  const handleExportVideo = () =>
    handleExportFile(
      `${API_URL}/export/${syncData.jobId}/video`,
      `sync_preview_${syncData.jobId}.mp4`,
      'Failed to export preview video'
    );

  const downloadFile = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const getFilenameFromResponse = (response, fallbackFilename) => {
    const header = response.headers?.['content-disposition'] || response.headers?.['Content-Disposition'];
    if (!header) {
      return fallbackFilename;
    }

    const match = header.match(/filename="?([^"]+)"?/i);
    return match ? match[1] : fallbackFilename;
  };

  const stats = syncData.statistics;

  return (
    <div className="results card">
      <h2>✨ Synchronization Complete!</h2>
      <p className="subtitle">Your video and audio are now perfectly synchronized</p>

      <div className="results-grid">
        <div className="stats-card">
          <h3>📊 Synchronization Statistics</h3>
          <div className="stat-row">
            <span className="stat-label">Total Events:</span>
            <span className="stat-value">{stats.total_events}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Successfully Synced:</span>
            <span className="stat-value success">{stats.snapped_events}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Sync Rate:</span>
            <span className="stat-value">{(stats.snap_rate * 100).toFixed(1)}%</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Avg Snap Distance:</span>
            <span className="stat-value">{stats.average_snap_distance.toFixed(3)}s</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Max Snap Distance:</span>
            <span className="stat-value">{stats.max_snap_distance.toFixed(3)}s</span>
          </div>
        </div>

        <div className="stats-card">
          <h3>📈 Events by Type</h3>
          {Object.entries(stats.by_type).map(([type, data]) => (
            <div key={type} className="type-stat">
              <div className="type-name">{type.replace(/_/g, ' ')}</div>
              <div className="type-details">
                <span>{data.snapped}/{data.total} synced</span>
                <span className="type-rate">({(data.snap_rate * 100).toFixed(0)}%)</span>
              </div>
              <div className="progress-bar" style={{ height: '4px' }}>
                <div 
                  className="progress-fill" 
                  style={{ width: `${data.snap_rate * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>

        <div className="summary-card">
          <h3>🎬 Video Summary</h3>
          <p><strong>Duration:</strong> {videoData.duration.toFixed(2)}s</p>
          <p><strong>Large Motions:</strong> {videoData.large_motions}</p>
          <p><strong>Small Motions:</strong> {videoData.small_motions}</p>
          <p><strong>Scene Changes:</strong> {videoData.scene_changes}</p>
          <p><strong>Camera Movements:</strong> {videoData.camera_movements}</p>
        </div>

        <div className="summary-card">
          <h3>🎵 Audio Summary</h3>
          <p><strong>Duration:</strong> {audioData.duration.toFixed(2)}s</p>
          <p><strong>Tempo:</strong> {audioData.tempo.toFixed(0)} BPM</p>
          <p><strong>Major Beats:</strong> {audioData.major_beats}</p>
          <p><strong>Minor Beats:</strong> {audioData.minor_beats}</p>
          <p><strong>Sections:</strong> {audioData.sections}</p>
        </div>
      </div>

      <div className="export-section">
        <h3>📥 Export Results</h3>
        <p>Save your synchronization data as JSON, CSV, PNG, or MP4</p>
        <div className="export-buttons">
          <button
            className="button button-primary"
            onClick={handleExportJSON}
            disabled={exporting}
          >
            📄 Export as JSON
          </button>
          <button
            className="button button-primary"
            onClick={handleExportCSV}
            disabled={exporting}
          >
            📊 Export as CSV
          </button>
          <button
            className="button button-secondary"
            onClick={handleExportImage}
            disabled={exporting}
          >
            🖼 Export as PNG
          </button>
          <button
            className="button button-secondary"
            onClick={handleExportVideo}
            disabled={exporting}
          >
            🎬 Export as MP4
          </button>
        </div>
      </div>

      {exportError && <div className="error">{exportError}</div>}

      <button
        className="button button-secondary reset-button"
        onClick={onReset}
        disabled={exporting}
      >
        ← Analyze Another Video
      </button>

      <div className="next-steps">
        <h4>🚀 Next Steps:</h4>
        <ul>
          <li>Download your synchronized data in JSON, CSV, PNG, or MP4 format</li>
          <li>Import the timeline data into your video editing software</li>
          <li>Use the annotated preview video to review event alignment</li>
          <li>Share the summary image for a quick visual report</li>
        </ul>
      </div>
    </div>
  );
};

export default Results;
