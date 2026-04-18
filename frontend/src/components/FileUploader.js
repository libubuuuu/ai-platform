import React, { useRef, useState } from 'react';
import './FileUploader.css';

const FileUploader = ({ onJobCreated }) => {
  const videoInputRef = useRef(null);
  const audioInputRef = useRef(null);
  const [videoFile, setVideoFile] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleVideoSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setVideoFile(file);
      setError(null);
    }
  };

  const handleAudioSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAudioFile(file);
      setError(null);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!videoFile || !audioFile) {
      setError('Please select both video and audio files');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create shared job ID for video/audio analysis lifecycle
      const jobId = `job_${Date.now()}`;

      onJobCreated({
        jobId,
        videoFile,
        audioFile,
      });

      setLoading(false);

    } catch (err) {
      setError(err.message || 'Failed to process files');
      setLoading(false);
    }
  };

  return (
    <div className="file-uploader card">
      <h2>📁 Upload Files</h2>
      <p className="subtitle">Select your video and audio files to begin analysis</p>

      <div className="upload-area">
        <div className="upload-box">
          <div className="upload-icon">🎬</div>
          <h3>Video File</h3>
          <p>MP4, MOV, AVI, MKV</p>
          <input
            type="file"
            ref={videoInputRef}
            onChange={handleVideoSelect}
            accept="video/*"
            disabled={loading}
          />
          <button
            className="button button-secondary"
            onClick={() => videoInputRef.current?.click()}
            disabled={loading}
          >
            Choose Video
          </button>
          {videoFile && (
            <p className="selected-file success">✓ {videoFile.name}</p>
          )}
        </div>

        <div className="upload-box">
          <div className="upload-icon">🎵</div>
          <h3>Audio File</h3>
          <p>MP3, WAV, FLAC, AAC</p>
          <input
            type="file"
            ref={audioInputRef}
            onChange={handleAudioSelect}
            accept="audio/*"
            disabled={loading}
          />
          <button
            className="button button-secondary"
            onClick={() => audioInputRef.current?.click()}
            disabled={loading}
          >
            Choose Audio
          </button>
          {audioFile && (
            <p className="selected-file success">✓ {audioFile.name}</p>
          )}
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      <button
        className="button button-primary start-button"
        onClick={handleUploadAndAnalyze}
        disabled={loading || !videoFile || !audioFile}
      >
        {loading ? (
          <span className="loading">
            <span className="spinner"></span>
            Processing...
          </span>
        ) : (
          'Start Analysis'
        )}
      </button>

      <div className="info-box">
        <h4>ℹ️ How it works:</h4>
        <ol>
          <li>Upload your video and audio files</li>
          <li>AI analyzes video for movements, scenes, and camera changes</li>
          <li>AI analyzes audio for beats and tempo</li>
          <li>Automatically sync video events to audio beats</li>
          <li>Review and export results</li>
        </ol>
      </div>
    </div>
  );
};

export default FileUploader;
