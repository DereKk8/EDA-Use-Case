<script>
  import { afterUpdate } from 'svelte'

  /** Array of { id, time, service, level, msg } objects */
  export let logs = []

  let feedEl

  // Keep the feed scrolled to the latest entry
  afterUpdate(() => {
    if (feedEl) feedEl.scrollTop = feedEl.scrollHeight
  })

  const SERVICE_COLORS = {
    api:      { bg: '#f3f4f6', text: '#374151' },
    producer: { bg: '#fff7ed', text: '#c2410c' },
    kafka:    { bg: '#eff6ff', text: '#1d4ed8' },
    worker:   { bg: '#f5f3ff', text: '#6d28d9' },
    redis:    { bg: '#fff1f2', text: '#be123c' },
  }

  const LEVEL_COLORS = {
    info:  { text: '#374151' },
    debug: { text: '#9ca3af' },
    warn:  { text: '#b45309' },
    error: { text: '#dc2626' },
  }

  function serviceStyle(service) {
    const c = SERVICE_COLORS[service.toLowerCase()] ?? SERVICE_COLORS.api
    return `background:${c.bg};color:${c.text}`
  }

  function levelStyle(level) {
    const c = LEVEL_COLORS[level.toLowerCase()] ?? LEVEL_COLORS.info
    return `color:${c.text}`
  }
</script>

<div class="log-panel panel">
  <div class="log-header">
    <h2>Logs de Servicios</h2>
    <div class="header-right">
      {#if logs.length > 0}
        <span class="live-badge">
          <span class="live-dot"></span>
          LIVE
        </span>
      {/if}
      <span class="log-count">{logs.length} líneas</span>
    </div>
  </div>

  <div class="feed" bind:this={feedEl}>
    {#if logs.length === 0}
      <p class="empty">Realiza un pedido para ver los logs en tiempo real…</p>
    {:else}
      {#each logs as line (line.id)}
        <div class="log-line">
          <span class="ts">{line.time}</span>
          <span class="svc" style={serviceStyle(line.service)}>{line.service}</span>
          <span class="lvl" style={levelStyle(line.level)}>{line.level}</span>
          <span class="msg">{line.msg}</span>
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  .log-panel {
    /* inherits .panel from App.svelte :global — redefine locally for portability */
    background: #0f172a;
    border-radius: var(--radius);
    box-shadow: var(--shadow-md);
    border: 1px solid #1e293b;
    overflow: hidden;
  }

  .log-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1.1rem 0.75rem;
    border-bottom: 1px solid #1e293b;
  }

  .log-header h2 {
    margin: 0;
    font-size: 0.85rem;
    font-weight: 700;
    color: #e2e8f0;
    letter-spacing: 0.01em;
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }

  .live-badge {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: #4ade80;
    background: #052e16;
    border: 1px solid #166534;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
  }

  .live-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #4ade80;
    animation: blink 1s ease-in-out infinite;
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
  }

  .log-count {
    font-size: 0.65rem;
    color: #64748b;
    font-variant-numeric: tabular-nums;
  }

  /* ── Feed area ──────────────────────────────── */
  .feed {
    padding: 0.5rem 0.75rem 0.75rem;
    max-height: 240px;
    overflow-y: auto;
    scroll-behavior: smooth;
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
    font-size: 0.72rem;
    line-height: 1.7;
  }

  .feed::-webkit-scrollbar { width: 4px; }
  .feed::-webkit-scrollbar-track { background: transparent; }
  .feed::-webkit-scrollbar-thumb { background: #334155; border-radius: 2px; }

  .empty {
    color: #475569;
    font-size: 0.75rem;
    font-family: inherit;
    padding: 0.5rem 0;
    margin: 0;
    font-style: italic;
  }

  /* ── Log line ───────────────────────────────── */
  .log-line {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    padding: 0.05rem 0;
    animation: slide-in 0.2s ease;
  }

  @keyframes slide-in {
    from { opacity: 0; transform: translateX(-6px); }
    to   { opacity: 1; transform: translateX(0); }
  }

  .ts {
    color: #475569;
    white-space: nowrap;
    flex-shrink: 0;
    font-size: 0.67rem;
    letter-spacing: 0.02em;
  }

  .svc {
    font-size: 0.65rem;
    font-weight: 700;
    padding: 0.05rem 0.35rem;
    border-radius: 3px;
    white-space: nowrap;
    flex-shrink: 0;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .lvl {
    font-size: 0.65rem;
    font-weight: 600;
    white-space: nowrap;
    flex-shrink: 0;
    width: 3.2rem;
    text-align: right;
  }

  .msg {
    color: #cbd5e1;
    word-break: break-word;
    flex: 1;
  }
</style>
