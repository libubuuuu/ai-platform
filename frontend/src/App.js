import React, { useEffect, useState } from 'react';
import axios from 'axios';
import API_URL from './config';
import PublishingCenter from './components/PublishingCenter';
import CommentAssistant from './components/CommentAssistant';
import './App.css';

const defaultRadarQuery = {
  region: 'domestic',
  platform_id: '',
  keyword: 'trend',
  limit: 6,
};

const defaultCanvasForm = {
  image_name: 'brand-poster.png',
  prompt_hint: 'clean editorial composition',
  count: 4,
  style: 'editorial',
};

const defaultRemixForm = {
  mode: 'merge',
  tone: 'professional',
  preserve_media: true,
};

function App() {
  const [overview, setOverview] = useState(null);
  const [platforms, setPlatforms] = useState([]);
  const [radarQuery, setRadarQuery] = useState(defaultRadarQuery);
  const [radarItems, setRadarItems] = useState([]);
  const [cart, setCart] = useState([]);
  const [canvasForm, setCanvasForm] = useState(defaultCanvasForm);
  const [canvasJob, setCanvasJob] = useState(null);
  const [remixForm, setRemixForm] = useState(defaultRemixForm);
  const [remixJob, setRemixJob] = useState(null);
  const [workspaceStats, setWorkspaceStats] = useState({
    connectedAccounts: 0,
    savedDrafts: 0,
  });
  const [loading, setLoading] = useState({
    overview: false,
    radar: false,
    canvas: false,
    remix: false,
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadBootstrapData = async () => {
      try {
        setLoading((prev) => ({ ...prev, overview: true }));
        const [overviewResponse, platformResponse, cartResponse] = await Promise.all([
          axios.get(`${API_URL}/api/overview`),
          axios.get(`${API_URL}/api/platforms`),
          axios.get(`${API_URL}/api/cart`),
        ]);
        setOverview(overviewResponse.data);
        setPlatforms(platformResponse.data.items || []);
        setCart(cartResponse.data.items || []);
        setWorkspaceStats({
          connectedAccounts: overviewResponse.data.connected_accounts || 0,
          savedDrafts: overviewResponse.data.draft_count || 0,
        });
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Failed to load platform data');
      } finally {
        setLoading((prev) => ({ ...prev, overview: false }));
      }
    };

    loadBootstrapData();
  }, []);

  const fetchRadar = async (event) => {
    event?.preventDefault();
    try {
      setLoading((prev) => ({ ...prev, radar: true }));
      setError(null);
      const response = await axios.get(`${API_URL}/api/radar`, {
        params: {
          region: radarQuery.region,
          platform_id: radarQuery.platform_id || undefined,
          keyword: radarQuery.keyword,
          limit: Number(radarQuery.limit) || 6,
        },
      });
      setRadarItems(response.data.items || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load radar items');
    } finally {
      setLoading((prev) => ({ ...prev, radar: false }));
    }
  };

  const addToCart = async (item) => {
    try {
      setError(null);
      const response = await axios.post(`${API_URL}/api/cart/items`, { item });
      setCart(response.data.items || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to add item to cart');
    }
  };

  const removeFromCart = async (itemId) => {
    try {
      setError(null);
      const response = await axios.delete(`${API_URL}/api/cart/${itemId}`);
      setCart(response.data.items || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to remove item');
    }
  };

  const createCanvasJob = async (event) => {
    event.preventDefault();
    try {
      setLoading((prev) => ({ ...prev, canvas: true }));
      setError(null);
      const response = await axios.post(`${API_URL}/api/canvas/similar`, canvasForm);
      setCanvasJob(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate canvas images');
    } finally {
      setLoading((prev) => ({ ...prev, canvas: false }));
    }
  };

  const createRemixJob = async (event) => {
    event.preventDefault();
    if (!cart.length) {
      setError('Add at least one item to the cart before remixing.');
      return;
    }

    try {
      setLoading((prev) => ({ ...prev, remix: true }));
      setError(null);
      const response = await axios.post(`${API_URL}/api/remix/jobs`, {
        item_ids: cart.map((item) => item.id),
        ...remixForm,
      });
      setRemixJob(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate remix video');
    } finally {
      setLoading((prev) => ({ ...prev, remix: false }));
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="app-header__inner">
          <div>
            <p className="eyebrow">Social Content Platform</p>
            <h1>Image and Video Generation Workspace</h1>
            <p className="header-copy">
              Build trend-backed content cards, generate similar image variants, and render remix videos from selected sources.
            </p>
          </div>
          <div className="header-metrics">
            <div className="metric-card">
              <span>Platforms</span>
              <strong>{overview ? overview.platform_count : '...'}</strong>
            </div>
            <div className="metric-card">
              <span>Accounts</span>
              <strong>{workspaceStats.connectedAccounts}</strong>
            </div>
            <div className="metric-card">
              <span>Drafts</span>
              <strong>{workspaceStats.savedDrafts}</strong>
            </div>
            <div className="metric-card">
              <span>Cart</span>
              <strong>{cart.length}</strong>
            </div>
          </div>
        </div>
      </header>

      <main className="app-main dashboard">
        {error && <div className="error dashboard-error">{error}</div>}

        <section className="card section">
          <div className="section-head">
            <div>
              <p className="eyebrow">Content Radar</p>
              <h2>Find trending source items</h2>
            </div>
          </div>
          <form className="form-grid" onSubmit={fetchRadar}>
            <label className="field">
              <span>Region</span>
              <select
                value={radarQuery.region}
                onChange={(e) => setRadarQuery((prev) => ({ ...prev, region: e.target.value }))}
              >
                <option value="domestic">Domestic</option>
                <option value="overseas">Overseas</option>
              </select>
            </label>
            <label className="field">
              <span>Platform</span>
              <select
                value={radarQuery.platform_id}
                onChange={(e) => setRadarQuery((prev) => ({ ...prev, platform_id: e.target.value }))}
              >
                <option value="">All platforms</option>
                {platforms
                  .filter((platform) => platform.region === radarQuery.region)
                  .map((platform) => (
                    <option key={platform.id} value={platform.id}>
                      {platform.name}
                    </option>
                  ))}
              </select>
            </label>
            <label className="field field--wide">
              <span>Keyword</span>
              <input
                type="text"
                value={radarQuery.keyword}
                onChange={(e) => setRadarQuery((prev) => ({ ...prev, keyword: e.target.value }))}
                placeholder="trend, launch, product, etc."
              />
            </label>
            <label className="field">
              <span>Limit</span>
              <input
                type="number"
                min="1"
                max="20"
                value={radarQuery.limit}
                onChange={(e) => setRadarQuery((prev) => ({ ...prev, limit: e.target.value }))}
              />
            </label>
            <div className="field field--action">
              <span>&nbsp;</span>
              <button className="button primary" type="submit" disabled={loading.radar}>
                {loading.radar ? 'Loading...' : 'Search Radar'}
              </button>
            </div>
          </form>

          <div className="item-grid">
            {radarItems.map((item) => (
              <article key={item.id} className="item-card">
                <div className="item-card__head">
                  <h3>{item.title}</h3>
                  <span className={`content-pill content-pill--${item.content_type}`}>{item.content_type}</span>
                </div>
                <p>{item.summary}</p>
                <p className="muted">{item.platform_name} · {item.freshness}</p>
                <div className="item-card__actions">
                  <button className="button secondary" type="button" onClick={() => addToCart(item)}>
                    Add to Cart
                  </button>
                  <a className="link-button" href={item.source_url} target="_blank" rel="noreferrer">
                    Source
                  </a>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="card section">
          <div className="section-head">
            <div>
              <p className="eyebrow">Cart</p>
              <h2>Selected source items</h2>
            </div>
          </div>
          <div className="item-grid item-grid--compact">
            {cart.length ? (
              cart.map((item) => (
                <article key={item.id} className="item-card item-card--compact">
                  <div className="item-card__head">
                    <h3>{item.title}</h3>
                    <button className="icon-button" type="button" onClick={() => removeFromCart(item.id)}>
                      Remove
                    </button>
                  </div>
                  <p className="muted">{item.platform_name} · {item.content_type}</p>
                </article>
              ))
            ) : (
              <p className="empty-state">Cart is empty. Add items from the radar above.</p>
            )}
          </div>
        </section>

        <section className="card section">
          <div className="section-head">
            <div>
              <p className="eyebrow">Image Canvas</p>
              <h2>Generate similar images</h2>
            </div>
          </div>
          <form className="form-grid" onSubmit={createCanvasJob}>
            <label className="field field--wide">
              <span>Image name</span>
              <input
                type="text"
                value={canvasForm.image_name}
                onChange={(e) => setCanvasForm((prev) => ({ ...prev, image_name: e.target.value }))}
              />
            </label>
            <label className="field field--wide">
              <span>Prompt hint</span>
              <input
                type="text"
                value={canvasForm.prompt_hint}
                onChange={(e) => setCanvasForm((prev) => ({ ...prev, prompt_hint: e.target.value }))}
              />
            </label>
            <label className="field">
              <span>Style</span>
              <input
                type="text"
                value={canvasForm.style}
                onChange={(e) => setCanvasForm((prev) => ({ ...prev, style: e.target.value }))}
              />
            </label>
            <label className="field">
              <span>Variants</span>
              <input
                type="number"
                min="1"
                max="12"
                value={canvasForm.count}
                onChange={(e) => setCanvasForm((prev) => ({ ...prev, count: Number(e.target.value) }))}
              />
            </label>
            <div className="field field--action">
              <span>&nbsp;</span>
              <button className="button primary" type="submit" disabled={loading.canvas}>
                {loading.canvas ? 'Generating...' : 'Generate Images'}
              </button>
            </div>
          </form>

          {canvasJob && (
            <div className="job-panel">
              <div className="job-panel__meta">
                <div>
                  <strong>{canvasJob.image_name}</strong>
                  <p className="muted">{canvasJob.prompt_hint}</p>
                </div>
                <a className="link-button" href={`${API_URL}${canvasJob.preview_image_url}`} target="_blank" rel="noreferrer">
                  Open Preview
                </a>
              </div>
              <div className="preview-stack">
                <img className="preview-image" src={`${API_URL}${canvasJob.preview_image_url}`} alt="Canvas preview" />
              </div>
              <div className="variant-links">
                {canvasJob.variants?.map((variant) => (
                  <a
                    key={variant.id}
                    className="variant-link"
                    href={`${API_URL}${variant.image_url}`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {variant.id}
                  </a>
                ))}
              </div>
            </div>
          )}
        </section>

        <section className="card section">
          <div className="section-head">
            <div>
              <p className="eyebrow">Remix Studio</p>
              <h2>Generate a preview video</h2>
            </div>
          </div>
          <form className="form-grid" onSubmit={createRemixJob}>
            <label className="field">
              <span>Mode</span>
              <select
                value={remixForm.mode}
                onChange={(e) => setRemixForm((prev) => ({ ...prev, mode: e.target.value }))}
              >
                <option value="merge">Merge</option>
                <option value="rewrite">Rewrite</option>
                <option value="one_by_one">One by one</option>
              </select>
            </label>
            <label className="field">
              <span>Tone</span>
              <input
                type="text"
                value={remixForm.tone}
                onChange={(e) => setRemixForm((prev) => ({ ...prev, tone: e.target.value }))}
              />
            </label>
            <label className="field field--toggle">
              <span>Preserve media</span>
              <input
                type="checkbox"
                checked={remixForm.preserve_media}
                onChange={(e) => setRemixForm((prev) => ({ ...prev, preserve_media: e.target.checked }))}
              />
            </label>
            <div className="field field--action">
              <span>&nbsp;</span>
              <button className="button primary" type="submit" disabled={loading.remix}>
                {loading.remix ? 'Generating...' : 'Generate Video'}
              </button>
            </div>
          </form>

          {remixJob && (
            <div className="job-panel">
              <div className="job-panel__meta">
                <div>
                  <strong>{remixJob.summary}</strong>
                  <p className="muted">{remixJob.mode} · {remixJob.tone}</p>
                </div>
                <a className="link-button" href={`${API_URL}${remixJob.preview_video_url}`} target="_blank" rel="noreferrer">
                  Open Preview
                </a>
              </div>
              <div className="preview-stack">
                <img className="preview-image" src={`${API_URL}${remixJob.storyboard_url}`} alt="Remix storyboard" />
                <video className="preview-video" controls src={`${API_URL}${remixJob.preview_video_url}`} />
              </div>
            </div>
          )}
        </section>

        <PublishingCenter
          apiUrl={API_URL}
          platforms={platforms}
          cart={cart}
          onStatsChange={setWorkspaceStats}
        />

        <CommentAssistant
          apiUrl={API_URL}
          cart={cart}
          remixJob={remixJob}
        />
      </main>
    </div>
  );
}

export default App;
