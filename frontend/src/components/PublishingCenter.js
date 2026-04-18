import React, { useEffect, useState } from 'react';
import axios from 'axios';

const defaultConnectForm = {
  platform_id: '',
  display_name: '',
  handle: '',
};

const defaultDraftForm = {
  platform_id: '',
  account_id: '',
  title: '',
  body: '',
  target: 'draft',
  notes: '',
};

function PublishingCenter({ apiUrl, platforms, cart, onStatsChange }) {
  const [ownerToken, setOwnerToken] = useState('owner-demo-token');
  const [ownerUnlocked, setOwnerUnlocked] = useState(false);
  const [ownerBusy, setOwnerBusy] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [drafts, setDrafts] = useState([]);
  const [connectForm, setConnectForm] = useState(defaultConnectForm);
  const [draftForm, setDraftForm] = useState(defaultDraftForm);
  const [savingAccount, setSavingAccount] = useState(false);
  const [savingDraft, setSavingDraft] = useState(false);
  const [localError, setLocalError] = useState(null);

  const syncStats = (nextAccounts, nextDrafts) => {
    onStatsChange?.({
      connectedAccounts: nextAccounts.length,
      savedDrafts: nextDrafts.length,
    });
  };

  const loadSecureCollections = async (token = ownerToken) => {
    const [accountsResponse, draftsResponse] = await Promise.all([
      axios.get(`${apiUrl}/api/accounts`, {
        headers: { 'X-Owner-Token': token },
      }),
      axios.get(`${apiUrl}/api/publishing/drafts`, {
        headers: { 'X-Owner-Token': token },
      }),
    ]);

    const nextAccounts = accountsResponse.data.items || [];
    const nextDrafts = draftsResponse.data.items || [];
    setAccounts(nextAccounts);
    setDrafts(nextDrafts);
    syncStats(nextAccounts, nextDrafts);
    return { nextAccounts, nextDrafts };
  };

  const handleUnlockWorkspace = async (event) => {
    event?.preventDefault();
    try {
      setOwnerBusy(true);
      setLocalError(null);
      setStatusMessage(null);

      const validation = await axios.post(`${apiUrl}/api/owner/validate`, {
        token: ownerToken,
      });

      if (!validation.data.valid) {
        setOwnerUnlocked(false);
        setStatusMessage({ variant: 'error', text: 'Owner token is invalid.' });
        return;
      }

      await loadSecureCollections(ownerToken);
      setOwnerUnlocked(true);
      setStatusMessage({ variant: 'success', text: 'Secure workspace unlocked.' });
    } catch (err) {
      setOwnerUnlocked(false);
      setLocalError(err.response?.data?.detail || err.message || 'Failed to unlock workspace');
    } finally {
      setOwnerBusy(false);
    }
  };

  useEffect(() => {
    if (platforms.length === 0) {
      return;
    }

    setConnectForm((prev) => ({
      ...prev,
      platform_id: prev.platform_id || platforms[0].id,
    }));
    setDraftForm((prev) => ({
      ...prev,
      platform_id: prev.platform_id || platforms[0].id,
    }));
  }, [platforms]);

  useEffect(() => {
    if (!ownerUnlocked || accounts.length === 0) {
      return;
    }

    setDraftForm((prev) => {
      const scoped = accounts.filter((account) => !prev.platform_id || account.platform_id === prev.platform_id);
      const nextAccount = scoped.find((account) => account.id === prev.account_id) || scoped[0] || accounts[0];

      if (!nextAccount || nextAccount.id === prev.account_id) {
        return prev;
      }

      return {
        ...prev,
        account_id: nextAccount.id,
      };
    });
  }, [accounts, ownerUnlocked]);

  useEffect(() => {
    void handleUnlockWorkspace();
    // The default token lets the local demo unlock automatically.
    // Users can replace it and click Unlock again for deployment.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleConnectAccount = async (event) => {
    event.preventDefault();
    try {
      setSavingAccount(true);
      setLocalError(null);

      const response = await axios.post(`${apiUrl}/api/accounts/connect`, connectForm, {
        headers: { 'X-Owner-Token': ownerToken },
      });

      const nextAccount = response.data.account;
      const nextAccounts = [nextAccount, ...accounts];
      setAccounts(nextAccounts);
      syncStats(nextAccounts, drafts);
      setStatusMessage({ variant: 'success', text: `Connected account ${nextAccount.display_name}.` });
      setConnectForm((prev) => ({
        ...prev,
        display_name: '',
        handle: '',
      }));
      setDraftForm((prev) => ({
        ...prev,
        account_id: nextAccount.id,
        platform_id: nextAccount.platform_id,
      }));
    } catch (err) {
      setLocalError(err.response?.data?.detail || err.message || 'Failed to connect account');
    } finally {
      setSavingAccount(false);
    }
  };

  const handleCreateDraft = async (event) => {
    event.preventDefault();
    const sourceIds = cart.map((item) => item.id);
    const media = Array.from(new Set(cart.flatMap((item) => item.media || [])));

    try {
      setSavingDraft(true);
      setLocalError(null);

      if (!draftForm.account_id) {
        throw new Error('Choose an account before creating a draft.');
      }

      const response = await axios.post(
        `${apiUrl}/api/publishing/drafts`,
        {
          ...draftForm,
          source_ids: sourceIds,
          media,
        },
        {
          headers: { 'X-Owner-Token': ownerToken },
        }
      );

      const nextDraft = response.data.draft;
      const nextDrafts = [nextDraft, ...drafts];
      setDrafts(nextDrafts);
      syncStats(accounts, nextDrafts);
      setStatusMessage({ variant: 'success', text: `Draft "${nextDraft.title}" saved.` });
      setDraftForm((prev) => ({
        ...prev,
        title: '',
        body: '',
        notes: '',
      }));
    } catch (err) {
      setLocalError(err.response?.data?.detail || err.message || 'Failed to save draft');
    } finally {
      setSavingDraft(false);
    }
  };

  const selectedPlatformAccounts = draftForm.platform_id
    ? accounts.filter((account) => account.platform_id === draftForm.platform_id)
    : accounts;

  const draftSourceSummary = cart.length
    ? cart.map((item) => `${item.platform_name}: ${item.title}`).join(' | ')
    : 'No source items selected yet.';

  return (
    <section className="card section">
      <div className="section-head">
        <div>
          <p className="eyebrow">Publishing Center</p>
          <h2>Bind accounts and save drafts</h2>
        </div>
      </div>

      <div className="lock-panel">
        <div>
          <p className="eyebrow">Owner Access</p>
          <h3>Unlock approved accounts and draft storage</h3>
          <div className="bullet-list">
            <div className="bullet-item">
              <span className="bullet-dot" />
              <span>Requires an owner token before reading accounts or drafts.</span>
            </div>
            <div className="bullet-item">
              <span className="bullet-dot" />
              <span>Use official or authorized integrations only.</span>
            </div>
            <div className="bullet-item">
              <span className="bullet-dot" />
              <span>Drafts can reuse cart sources and media references.</span>
            </div>
          </div>
        </div>
        <form className="lock-form" onSubmit={handleUnlockWorkspace}>
          <input
            className="text-input"
            type="password"
            value={ownerToken}
            onChange={(e) => setOwnerToken(e.target.value)}
            placeholder="Owner token"
          />
          <button className="button primary" type="submit" disabled={ownerBusy}>
            {ownerBusy ? 'Checking...' : ownerUnlocked ? 'Refresh Access' : 'Unlock Workspace'}
          </button>
        </form>
      </div>

      {statusMessage && <div className={`banner banner-${statusMessage.variant}`}>{statusMessage.text}</div>}
      {localError && <div className="banner banner-error">{localError}</div>}

      <div className="publish-grid" style={{ marginTop: '16px' }}>
        <div className="publish-card">
          <p className="panel-eyebrow">Account Binding</p>
          <h2>Connect an authorized account</h2>
          <form className="publish-card" onSubmit={handleConnectAccount}>
            <label>
              <span className="small-note">Platform</span>
              <select
                className="text-input"
                value={connectForm.platform_id}
                onChange={(e) => {
                  const nextPlatform = e.target.value;
                  setConnectForm((prev) => ({ ...prev, platform_id: nextPlatform }));
                  setDraftForm((prev) => ({ ...prev, platform_id: nextPlatform }));
                }}
              >
                {platforms.map((platform) => (
                  <option key={platform.id} value={platform.id}>
                    {platform.name} ({platform.region})
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span className="small-note">Display name</span>
              <input
                className="text-input"
                type="text"
                value={connectForm.display_name}
                onChange={(e) => setConnectForm((prev) => ({ ...prev, display_name: e.target.value }))}
                placeholder="Brand Content"
              />
            </label>
            <label>
              <span className="small-note">Handle</span>
              <input
                className="text-input"
                type="text"
                value={connectForm.handle}
                onChange={(e) => setConnectForm((prev) => ({ ...prev, handle: e.target.value }))}
                placeholder="@brand_lab"
              />
            </label>
            <button className="button primary" type="submit" disabled={savingAccount || !ownerUnlocked}>
              {savingAccount ? 'Connecting...' : 'Connect Account'}
            </button>
          </form>
        </div>

        <div className="publish-card">
          <p className="panel-eyebrow">Draft Builder</p>
          <h2>Create a draft from cart sources</h2>
          <form className="publish-card" onSubmit={handleCreateDraft}>
            <div className="grid-two">
              <label>
                <span className="small-note">Platform</span>
                <select
                  className="text-input"
                  value={draftForm.platform_id}
                  onChange={(e) => setDraftForm((prev) => ({ ...prev, platform_id: e.target.value, account_id: '' }))}
                >
                  {platforms.map((platform) => (
                    <option key={platform.id} value={platform.id}>
                      {platform.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span className="small-note">Account</span>
                <select
                  className="text-input"
                  value={draftForm.account_id}
                  onChange={(e) => setDraftForm((prev) => ({ ...prev, account_id: e.target.value }))}
                >
                  <option value="">Choose an account</option>
                  {selectedPlatformAccounts.map((account) => (
                    <option key={account.id} value={account.id}>
                      {account.display_name} ({account.handle})
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <label>
              <span className="small-note">Title</span>
              <input
                className="text-input"
                type="text"
                value={draftForm.title}
                onChange={(e) => setDraftForm((prev) => ({ ...prev, title: e.target.value }))}
                placeholder="Launch-ready content draft"
              />
            </label>

            <label>
              <span className="small-note">Body</span>
              <textarea
                className="text-area"
                value={draftForm.body}
                onChange={(e) => setDraftForm((prev) => ({ ...prev, body: e.target.value }))}
                placeholder="Write the draft body here"
              />
            </label>

            <div className="grid-two">
              <label>
                <span className="small-note">Target</span>
                <select
                  className="text-input"
                  value={draftForm.target}
                  onChange={(e) => setDraftForm((prev) => ({ ...prev, target: e.target.value }))}
                >
                  <option value="draft">Draft</option>
                  <option value="queue">Scheduled Queue</option>
                </select>
              </label>
              <label>
                <span className="small-note">Notes</span>
                <input
                  className="text-input"
                  type="text"
                  value={draftForm.notes}
                  onChange={(e) => setDraftForm((prev) => ({ ...prev, notes: e.target.value }))}
                  placeholder="Reviewer notes or publish checklist"
                />
              </label>
            </div>

            <div className="small-note">
              <strong>Sources:</strong> {draftSourceSummary}
            </div>
            <div className="small-note">
              <strong>Media references:</strong> {cart.reduce((count, item) => count + (item.media?.length || 0), 0)}
            </div>

            <button className="button primary" type="submit" disabled={savingDraft || !ownerUnlocked}>
              {savingDraft ? 'Saving...' : 'Save Draft'}
            </button>
          </form>
        </div>

        <div className="publish-card full-span">
          <p className="panel-eyebrow">Workspace State</p>
          <h2>Authorized accounts and saved drafts</h2>
          <div className="grid-two">
            <div>
              <h3>Accounts</h3>
              <div className="account-grid">
                {accounts.length ? (
                  accounts.map((account) => (
                    <button
                      type="button"
                      key={account.id}
                      className={`account-card ${account.id === draftForm.account_id ? 'selected' : ''}`}
                      onClick={() => setDraftForm((prev) => ({ ...prev, account_id: account.id, platform_id: account.platform_id }))}
                    >
                      <strong>{account.display_name}</strong>
                      <span>{account.handle}</span>
                      <small>{account.platform_id}</small>
                      <small>Drafts: {account.draft_count}</small>
                    </button>
                  ))
                ) : (
                  <p className="empty-state">
                    Unlock the workspace to load authorized accounts.
                  </p>
                )}
              </div>
            </div>

            <div>
              <h3>Saved Drafts</h3>
              <div className="draft-box-list">
                {drafts.length ? (
                  drafts.map((draft) => (
                    <article key={draft.id} className="saved-draft">
                      <div className="stack-head">
                        <strong>{draft.title}</strong>
                        <span className="tag accent">{draft.target}</span>
                      </div>
                      <p>{draft.body}</p>
                      <div className="grid-two">
                        <span className="tag neutral">{draft.platform_name}</span>
                        <span className="tag cool">{draft.account_name}</span>
                      </div>
                      <p className="small-note">
                        Sources: {draft.source_ids?.length || 0} | Media refs: {draft.media?.length || 0}
                      </p>
                      {draft.notes && <p className="small-note">Notes: {draft.notes}</p>}
                    </article>
                  ))
                ) : (
                  <p className="empty-state">
                    No drafts saved yet. Create one from the form above.
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default PublishingCenter;
