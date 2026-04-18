import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import API_URL from '../config';
import './Analyzer.css';

const VideoAnalyzer = ({ jobId, file, onComplete }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);

  const analyzeVideo = useCallback(async () => {
    try {
      setAnalyzing(true);
      setProgress(0);
      setError(null);

      if (!file) {
        throw new Error('Video file not selected');
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('job_id', jobId);

      setProgress(20);

      const response = await axios.post(`${API_URL}/analyze/video`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setProgress(100);
      setResults(response.data.results);
      
      // Notify parent component
      onComplete({
        type: 'video',
        data: response.data.results,
        jobId: response.data.job_id,
      });

    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to analyze video');
      console.error('Video analysis error:', err);
    } finally {
      setAnalyzing(false);
    }
  }, [file, jobId, onComplete]);

  useEffect(() => {
    if (jobId && file) {
      analyzeVideo();
    }
  }, [jobId, file, analyzeVideo]);

  return (
    <div className="analyzer card">
      <h3>🎬 Video Analysis</h3>
      
      {analyzing && (
        <div className="analyzing">
          <div className="spinner"></div>
          <p>Analyzing video...</p>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {results && !analyzing && (
        <div className="results">
          <h4>Analysis Results</h4>
          <div className="metrics">
            <div className="metric">
              <span className="metric-label">Large Motions</span>
              <span className="metric-value">{results.large_motions}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Small Motions</span>
              <span className="metric-value">{results.small_motions}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Scene Changes</span>
              <span className="metric-value">{results.scene_changes}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Camera Movements</span>
              <span className="metric-value">{results.camera_movements}</span>
            </div>
          </div>
          <div className="duration">
            Duration: {results.duration.toFixed(2)} seconds
          </div>
          <div className="success">✓ Analysis Complete</div>
        </div>
      )}
    </div>
  );
};

export default VideoAnalyzer;
