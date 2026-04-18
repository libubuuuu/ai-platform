import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import API_URL from '../config';
import './Analyzer.css';

const AudioAnalyzer = ({ jobId, file, onComplete }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);

  const analyzeAudio = useCallback(async () => {
    try {
      setAnalyzing(true);
      setProgress(0);
      setError(null);

      if (!file) {
        throw new Error('Audio file not selected');
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('job_id', jobId);

      setProgress(20);

      const response = await axios.post(`${API_URL}/analyze/audio`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setProgress(100);
      setResults(response.data.results);
      
      // Notify parent component
      onComplete({
        type: 'audio',
        data: response.data.results,
        jobId: response.data.job_id,
      });

    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to analyze audio');
      console.error('Audio analysis error:', err);
    } finally {
      setAnalyzing(false);
    }
  }, [file, jobId, onComplete]);

  useEffect(() => {
    if (jobId && file) {
      analyzeAudio();
    }
  }, [jobId, file, analyzeAudio]);

  return (
    <div className="analyzer card">
      <h3>🎵 Audio Analysis</h3>
      
      {analyzing && (
        <div className="analyzing">
          <div className="spinner"></div>
          <p>Analyzing audio...</p>
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
          
          <div className="tempo-info">
            <span className="metric-label">Tempo (BPM)</span>
            <span className="metric-value" style={{ display: 'inline-block' }}>
              {results.tempo.toFixed(0)}
            </span>
          </div>

          <div className="beats-info">
            <div className="beat-item">
              <span className="beat-label">Major Beats</span>
              <span className="beat-count">{results.major_beats}</span>
            </div>
            <div className="beat-item">
              <span className="beat-label">Minor Beats</span>
              <span className="beat-count">{results.minor_beats}</span>
            </div>
            <div className="beat-item">
              <span className="beat-label">Total Beats</span>
              <span className="beat-count">{results.total_beats}</span>
            </div>
          </div>

          <div className="duration">
            Duration: {results.duration.toFixed(2)} seconds
          </div>
          <div className="duration">
            Sections detected: {results.sections}
          </div>
          <div className="success">✓ Analysis Complete</div>
        </div>
      )}
    </div>
  );
};

export default AudioAnalyzer;
