import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';

function CommentAssistant({ apiUrl, cart, remixJob }) {
  const [targetsText, setTargetsText] = useState('launch thread\ncomment reply');
  const [context, setContext] = useState('');
  const [tone, setTone] = useState('professional');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const contextOrigin = useRef(null);

  useEffect(() => {
    if (contextOrigin.current === 'user') {
      return;
    }

    if (remixJob?.summary) {
      const nextContext = `Remix summary: ${remixJob.summary}`;
      if (context !== nextContext || contextOrigin.current !== 'remix') {
        setContext(nextContext);
        contextOrigin.current = 'remix';
      }
      return;
    }

    if (cart.length) {
      const nextContext = cart.map((item) => `${item.platform_name}: ${item.title}`).join('\n');
      if (context !== nextContext || contextOrigin.current !== 'cart') {
        setContext(nextContext);
        contextOrigin.current = 'cart';
      }
      return;
    }

    if (context) {
      setContext('');
      contextOrigin.current = null;
    }
  }, [cart, remixJob, context]);

  const setContextValue = (value) => {
    setContext(value);
    contextOrigin.current = 'user';
  };

  const targets = targetsText
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean);

  const useCartTargets = () => {
    setTargetsText(cart.map((item) => item.title).join('\n'));
  };

  const useCartContext = () => {
    const joined = cart.map((item) => `${item.platform_name}: ${item.summary}`).join('\n');
    setContextValue(joined);
  };

  const useRemixContext = () => {
    if (!remixJob?.summary) {
      return;
    }
    setContextValue(`Remix summary: ${remixJob.summary}`);
  };

  const handleGenerateComments = async (event) => {
    event.preventDefault();
    try {
      setLoading(true);
      setError(null);

      if (!targets.length) {
        throw new Error('Add at least one target before generating comments.');
      }

      const response = await axios.post(`${apiUrl}/api/comments/suggestions`, {
        targets,
        context,
        tone,
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate comments');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card section">
      <div className="section-head">
        <div>
          <p className="eyebrow">AI Comment Assistant</p>
          <h2>Generate review-ready comment suggestions</h2>
        </div>
      </div>

      <div className="grid-two comment-results">
        <div className="comment-card">
          <div className="stack-head">
            <strong>Comment request</strong>
            <span className="tag neutral">{tone}</span>
          </div>
          <form onSubmit={handleGenerateComments} className="canvas-form">
            <label>
              <span className="small-note">Targets</span>
              <textarea
                className="text-area"
                value={targetsText}
                onChange={(e) => setTargetsText(e.target.value)}
                placeholder="One target per line"
              />
            </label>
            <div className="context-actions">
              <button type="button" className="button secondary" onClick={useCartTargets} disabled={!cart.length}>
                Use Cart Targets
              </button>
              <button type="button" className="button secondary" onClick={useCartContext} disabled={!cart.length}>
                Use Cart Context
              </button>
              <button type="button" className="button secondary" onClick={useRemixContext} disabled={!remixJob?.summary}>
                Use Remix Context
              </button>
            </div>
            <label>
              <span className="small-note">Context</span>
              <textarea
                className="text-area large"
                value={context}
                onChange={(e) => setContextValue(e.target.value)}
                placeholder="Add post context, product notes, or moderation guidance"
              />
            </label>
            <label>
              <span className="small-note">Tone</span>
              <select className="text-input" value={tone} onChange={(e) => setTone(e.target.value)}>
                <option value="professional">Professional</option>
                <option value="friendly">Friendly</option>
                <option value="persuasive">Persuasive</option>
                <option value="bold">Bold</option>
              </select>
            </label>
            <button className="button primary" type="submit" disabled={loading}>
              {loading ? 'Generating...' : 'Generate Suggestions'}
            </button>
          </form>

          <p className="small-note">
            Suggestions are for human review only. This assistant does not post comments automatically.
          </p>
        </div>

        <div className="comment-card">
          <div className="stack-head">
            <strong>Generated output</strong>
            {result ? <span className="tag accent">{result.job_id}</span> : <span className="tag neutral">Idle</span>}
          </div>

          {error && <div className="banner banner-error">{error}</div>}

          {result ? (
            <div className="draft-box-list">
              <div className="saved-draft">
                <strong>Safety note</strong>
                <p>{result.safety_note}</p>
              </div>

              <div className="saved-draft">
                <strong>Shared points</strong>
                <div className="bullet-list">
                  {result.shared_points?.map((point) => (
                    <div key={point} className="bullet-item">
                      <span className="bullet-dot" />
                      <span>{point}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="draft-box-list">
                {result.suggestions?.map((item) => (
                  <article key={`${item.target}-${item.angle}`} className="comment-card">
                    <div className="stack-head">
                      <strong>{item.target}</strong>
                      <span className="tag cool">{item.angle}</span>
                    </div>
                    <p>{item.comment}</p>
                  </article>
                ))}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              Run the assistant to generate comment suggestions for your targets.
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

export default CommentAssistant;
