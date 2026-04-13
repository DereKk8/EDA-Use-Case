<script>
  import { onMount, onDestroy } from 'svelte'
  import EdaFlow from './lib/EdaFlow.svelte'
  import LogFeed from './lib/LogFeed.svelte'

  // ── State ────────────────────────────────────────────────
  let productos = []
  let carrito = []
  let cliente = ''
  let mensajePedido = ''
  let mensajeTipo = '' // 'ok' | 'err'
  let cargando = false
  let edaStep = 0
  let pollingInterval = null
  let step2Timeout = null
  let logLines = []
  let logId = 0
  let notificaciones = []
  let cargandoNotifs = false
  let errorNotifs = ''

  // Adjust timing (ms) to speed up the demo — lower = faster
  const STEP2_DELAY = 1500
  const POLL_INTERVAL = 2000

  const foodEmoji = {
    'prod-1': '🍔',
    'prod-2': '🍕',
    'prod-3': '🥤',
    'prod-4': '🥗',
  }

  // ── Lifecycle ────────────────────────────────────────────
  onMount(async () => {
    try {
      const r = await fetch('/productos')
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      productos = await r.json()
    } catch (e) {
      console.error('No se pudo cargar el catálogo:', e)
      mensajePedido = 'No se pudo conectar con el servidor. ¿Está el backend en ejecución?'
      mensajeTipo = 'err'
    }
    await cargarNotificaciones()
  })

  async function cargarNotificaciones() {
    cargandoNotifs = true
    errorNotifs = ''
    try {
      const r = await fetch('/notificaciones')
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      notificaciones = await r.json()
    } catch (e) {
      console.error('No se pudieron cargar las notificaciones:', e)
      errorNotifs = 'No se pudo consultar Redis.'
      notificaciones = []
    } finally {
      cargandoNotifs = false
    }
  }

  onDestroy(() => {
    clearInterval(pollingInterval)
    clearTimeout(step2Timeout)
  })

  // ── Cart helpers ─────────────────────────────────────────
  function agregar(p) {
    if (!carrito.find(x => x.id === p.id)) carrito = [...carrito, { ...p }]
  }

  function quitar(id) {
    carrito = carrito.filter(x => x.id !== id)
  }

  $: total = carrito.reduce((s, p) => s + p.precio, 0)
  $: enCarrito = (id) => !!carrito.find(x => x.id === id)

  // ── Order flow ───────────────────────────────────────────
  async function realizarPedido() {
    if (!cliente.trim() || carrito.length === 0) {
      mensajePedido = 'Ingresa tu nombre y agrega al menos un producto.'
      mensajeTipo = 'err'
      return
    }
    cargando = true
    clearInterval(pollingInterval)
    clearTimeout(step2Timeout)
    edaStep = 0
    mensajePedido = ''

    try {
      const r = await fetch('/pedidos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cliente, productos: carrito }),
      })
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      const data = await r.json()

      mensajePedido = `¡Pedido enviado! ID: ${data.pedido_id.slice(0, 8)}…`
      mensajeTipo = 'ok'

      const nombrePedido = cliente
      const totalPedido = total
      carrito = []
      cliente = ''

      // Kick off EDA flow visualisation + log feed (cosmetic only)
      logLines = []
      scheduleLogs(data.pedido_id, nombrePedido, totalPedido)
      edaStep = 1
      step2Timeout = setTimeout(() => {
        // Avoid overriding a later step if processing already finished.
        if (edaStep === 1) edaStep = 2
      }, STEP2_DELAY)
      startPolling(data.pedido_id)
    } catch (e) {
      mensajePedido = 'Error al crear el pedido. Intenta de nuevo.'
      mensajeTipo = 'err'
    }

    cargando = false
  }

  function startPolling(id) {
    clearInterval(pollingInterval)
    pollingInterval = setInterval(async () => {
      try {
        const r = await fetch(`/pedidos/${id}`)
        if (r.ok) {
          const data = await r.json()
          if (data.notificacion) {
            edaStep = 3
            clearInterval(pollingInterval)
            clearTimeout(step2Timeout)
            cargarNotificaciones()
            setTimeout(() => {
              if (edaStep === 3) edaStep = 4
            }, 700)
          }
        }
      } catch (_) { /* silent — backend may be momentarily unavailable */ }
    }, POLL_INTERVAL)
  }

  // ── Log feed (purely cosmetic — no backend calls) ────────
  function addLog(service, level, msg) {
    const now = new Date()
    const time = now.toTimeString().slice(0, 8)
    logLines = [...logLines, { id: logId++, time, service, level, msg }]
  }

  /**
   * Schedules a sequence of realistic log lines after an order is placed.
   * All delays are cosmetic-only; they do not affect any fetch or polling call.
   */
  function scheduleLogs(pedidoId, nombre, orderTotal) {
    const shortId = pedidoId.slice(0, 8)
    const fmt = (n) => n.toLocaleString('es-CO')
    const offset = Math.floor(Math.random() * 90) + 10  // random Kafka offset

    const entries = [
      // ── Stage 1 — order submitted ──────────────────────────
      { t:    0, svc: 'API',      lvl: 'INFO',  msg: `POST /pedidos → 201 Created  [id: ${shortId}…]` },
      { t:  180, svc: 'Producer', lvl: 'INFO',  msg: `Serialising OrderCreated event for order ${shortId}…` },
      { t:  400, svc: 'Producer', lvl: 'INFO',  msg: `Publishing to Kafka topic 'orders' (key: ${shortId})` },
      { t:  620, svc: 'Kafka',    lvl: 'INFO',  msg: `Message received on topic 'orders', partition 0` },
      { t:  820, svc: 'Kafka',    lvl: 'DEBUG', msg: `Assigned offset ${offset}  [group: kitchen-workers]` },
      // ── Stage 2 — broker delivers to worker ────────────────
      { t: 1300, svc: 'Kafka',    lvl: 'INFO',  msg: `Delivering msg offset ${offset} to consumer kitchen-workers-0` },
      { t: 1550, svc: 'Worker',   lvl: 'INFO',  msg: `Fetched message from 'orders'  [offset: ${offset}]` },
      { t: 1800, svc: 'Worker',   lvl: 'INFO',  msg: `Processing order for '${nombre}'  — $${fmt(orderTotal)}` },
      { t: 2100, svc: 'Worker',   lvl: 'DEBUG', msg: `Validating ${orderTotal > 0 ? 'products list' : 'empty cart'}…` },
      // ── Stage 3 — worker completes ─────────────────────────
      { t: 2500, svc: 'Worker',   lvl: 'INFO',  msg: `Order validated ✓  — writing notification to Redis` },
      { t: 2750, svc: 'Redis',    lvl: 'INFO',  msg: `SET notification:${shortId}  [EX 3600]  → OK` },
      { t: 2980, svc: 'Kafka',    lvl: 'DEBUG', msg: `Committing offset ${offset + 1} for group kitchen-workers` },
      { t: 3150, svc: 'Worker',   lvl: 'INFO',  msg: `✓ Order ${shortId}… marked as ready` },
    ]

    for (const e of entries) {
      setTimeout(() => addLog(e.svc, e.lvl, e.msg), e.t)
    }
  }
</script>

<!-- ═══════════════════════════════════════════════════════ -->
<!--  Layout                                                 -->
<!-- ═══════════════════════════════════════════════════════ -->

<div class="app">

  <!-- Header -->
  <header>
    <div class="header-inner">
      <div class="brand">
        <span class="brand-icon">🍽️</span>
        <h1>EDA Bistro</h1>
      </div>
      <span class="eda-badge">Event-Driven Demo</span>
    </div>
  </header>

  <!-- Main content -->
  <main>

    <!-- Catalog ─────────────────────────────── -->
    <section class="catalog-section">
      <h2 class="section-title">Menú del día</h2>

      {#if productos.length === 0 && !mensajePedido}
        <div class="skeleton-grid">
          {#each Array(4) as _}
            <div class="skeleton-card"></div>
          {/each}
        </div>
      {:else}
        <div class="catalog-grid">
          {#each productos as p (p.id)}
            {@const added = enCarrito(p.id)}
            <div class="card" class:added>
              <div class="card-emoji">{foodEmoji[p.id] ?? '🍽️'}</div>
              <div class="card-info">
                <h3>{p.nombre}</h3>
                <p class="price">${p.precio.toLocaleString('es-CO')}</p>
              </div>
              <button
                class="btn-add"
                class:btn-added={added}
                on:click={() => agregar(p)}
                disabled={added}
              >
                {added ? '✓ En tu pedido' : '+ Agregar'}
              </button>
            </div>
          {/each}
        </div>
      {/if}
    </section>

    <!-- Sidebar ─────────────────────────────── -->
    <aside class="sidebar">

      <!-- Cart panel -->
      <div class="panel cart-panel">
        <h2 class="section-title">Tu pedido</h2>

        <input
          class="name-input"
          bind:value={cliente}
          placeholder="¿A nombre de quién?"
          autocomplete="off"
        />

        {#if carrito.length > 0}
          <ul class="cart-list">
            {#each carrito as p (p.id)}
              <li class="cart-item">
                <span class="item-emoji">{foodEmoji[p.id] ?? '🍽️'}</span>
                <span class="item-name">{p.nombre}</span>
                <span class="item-price">${p.precio.toLocaleString('es-CO')}</span>
                <button class="btn-remove" on:click={() => quitar(p.id)} title="Quitar">×</button>
              </li>
            {/each}
          </ul>
          <div class="total-row">
            <span>Total</span>
            <strong>${total.toLocaleString('es-CO')}</strong>
          </div>
        {:else}
          <p class="empty-cart">Agrega algo del menú 👆</p>
        {/if}

        <button class="btn-order" on:click={realizarPedido} disabled={cargando}>
          {cargando ? 'Enviando…' : 'Realizar Pedido 🚀'}
        </button>

        {#if mensajePedido}
          <p class="msg {mensajeTipo}">{mensajePedido}</p>
        {/if}
      </div>

      <!-- Notificaciones Redis -->
      <div class="panel notif-panel">
        <div class="notif-header">
          <h2 class="section-title notif-title">Notificaciones (Redis)</h2>
          <button
            type="button"
            class="btn-refresh"
            on:click={cargarNotificaciones}
            disabled={cargandoNotifs}
            title="Actualizar lista"
          >
            {cargandoNotifs ? '…' : '\u21BB'}
          </button>
        </div>
        {#if errorNotifs}
          <p class="notif-err">{errorNotifs}</p>
        {:else if notificaciones.length === 0}
          <p class="notif-empty">
            {cargandoNotifs ? 'Cargando…' : 'No hay notificaciones guardadas (o ya expiraron).'}
          </p>
        {:else}
          <ul class="notif-list">
            {#each notificaciones as n (n.pedido_id)}
              <li class="notif-item">
                <span class="notif-id" title={n.pedido_id}>{n.pedido_id.slice(0, 8)}…</span>
                <span class="notif-msg">{n.mensaje}</span>
                <span class="notif-meta">
                  <span class="notif-estado">{n.estado ?? '—'}</span>
                  {#if n.created_at}
                    <time class="notif-time" datetime={n.created_at}>
                      {new Date(n.created_at).toLocaleString('es-CO', {
                        dateStyle: 'short',
                        timeStyle: 'medium',
                      })}
                    </time>
                  {/if}
                </span>
              </li>
            {/each}
          </ul>
        {/if}
      </div>

      <!-- EDA Flow panel -->
      <EdaFlow step={edaStep} />

    </aside>
  </main>

  <!-- Service log feed — full width below the main grid -->
  <div class="log-wrapper">
    <LogFeed logs={logLines} />
  </div>

</div>

<!-- ═══════════════════════════════════════════════════════ -->
<!--  Styles                                                 -->
<!-- ═══════════════════════════════════════════════════════ -->

<style>
  /* ── Design tokens ─────────────────────────────────────── */
  :global(:root) {
    --bg:           #FFF8F0;
    --surface:      #FFFFFF;
    --primary:      #F4622A;
    --primary-light:#FFF0E8;
    --accent:       #52B788;
    --text:         #1C1C1E;
    --muted:        #6B7280;
    --border:       #E5E7EB;
    --shadow-sm:    0 1px 3px rgba(0,0,0,0.07);
    --shadow-md:    0 4px 16px rgba(0,0,0,0.09);
    --shadow-lg:    0 8px 32px rgba(0,0,0,0.12);
    --radius:       14px;
    --radius-sm:    8px;
  }

  :global(*, *::before, *::after) { box-sizing: border-box; margin: 0; padding: 0; }

  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    font-size: 15px;
    line-height: 1.5;
  }

  :global(h1, h2, h3) { line-height: 1.2; }

  /* ── App shell ─────────────────────────────────────────── */
  .app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* ── Header ────────────────────────────────────────────── */
  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .header-inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0.9rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }

  .brand-icon { font-size: 1.5rem; }

  h1 {
    font-size: 1.3rem;
    font-weight: 800;
    color: var(--primary);
    letter-spacing: -0.02em;
  }

  .eda-badge {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    background: var(--primary-light);
    color: var(--primary);
    padding: 0.3rem 0.7rem;
    border-radius: 999px;
    border: 1px solid #fad3be;
  }

  /* ── Main layout ───────────────────────────────────────── */
  main {
    flex: 1;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
    padding: 2rem 1.5rem;
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 2rem;
    align-items: start;
  }

  @media (max-width: 860px) {
    main {
      grid-template-columns: 1fr;
      padding: 1.25rem 1rem;
    }
  }

  .section-title {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: var(--text);
  }

  /* ── Catalog ───────────────────────────────────────────── */
  .catalog-section { min-width: 0; }

  .catalog-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1rem;
  }

  /* Skeleton loading */
  .skeleton-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1rem;
  }

  .skeleton-card {
    height: 220px;
    border-radius: var(--radius);
    background: linear-gradient(90deg, #f0e8e0 25%, #fdf6f0 50%, #f0e8e0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.4s infinite;
  }

  @keyframes shimmer {
    0%   { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  /* Product card */
  .card {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1rem 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.6rem;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    cursor: default;
  }

  .card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
  }

  .card.added {
    border-color: var(--accent);
    background: #f0faf4;
  }

  .card-emoji {
    font-size: 2.8rem;
    line-height: 1;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.12));
    transition: transform 0.2s;
  }

  .card:hover .card-emoji {
    transform: scale(1.08);
  }

  .card-info h3 {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.2rem;
  }

  .price {
    font-size: 1rem;
    font-weight: 700;
    color: var(--primary);
  }

  .btn-add {
    margin-top: auto;
    width: 100%;
    padding: 0.5rem;
    border: none;
    border-radius: var(--radius-sm);
    background: var(--primary);
    color: #fff;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s, transform 0.1s;
  }

  .btn-add:hover:not(:disabled) {
    background: #d9521f;
    transform: scale(1.02);
  }

  .btn-add.btn-added,
  .btn-add:disabled {
    background: var(--accent);
    cursor: default;
    transform: none;
  }

  /* ── Sidebar ───────────────────────────────────────────── */
  .sidebar {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    position: sticky;
    top: 4.5rem;
  }

  .panel {
    background: var(--surface);
    border-radius: var(--radius);
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border);
    padding: 1.25rem;
  }

  /* ── Cart panel ────────────────────────────────────────── */
  .name-input {
    width: 100%;
    padding: 0.6rem 0.8rem;
    border: 1.5px solid var(--border);
    border-radius: var(--radius-sm);
    font-size: 0.9rem;
    font-family: inherit;
    background: var(--bg);
    color: var(--text);
    outline: none;
    transition: border-color 0.15s;
    margin-bottom: 0.75rem;
  }

  .name-input:focus {
    border-color: var(--primary);
  }

  .cart-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-bottom: 0.75rem;
  }

  .cart-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.4rem 0.5rem;
    background: var(--bg);
    border-radius: var(--radius-sm);
    font-size: 0.82rem;
  }

  .item-emoji { font-size: 1rem; }

  .item-name {
    flex: 1;
    color: var(--text);
    font-weight: 500;
  }

  .item-price {
    color: var(--primary);
    font-weight: 700;
    white-space: nowrap;
  }

  .btn-remove {
    background: none;
    border: none;
    color: var(--muted);
    font-size: 1.1rem;
    cursor: pointer;
    line-height: 1;
    padding: 0 0.2rem;
    transition: color 0.15s;
  }

  .btn-remove:hover { color: #e53e3e; }

  .total-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.9rem;
    font-weight: 600;
    padding: 0.5rem 0;
    border-top: 1px solid var(--border);
    margin-bottom: 0.75rem;
    color: var(--text);
  }

  .total-row strong {
    color: var(--primary);
    font-size: 1.1rem;
  }

  .empty-cart {
    font-size: 0.8rem;
    color: var(--muted);
    text-align: center;
    padding: 0.75rem 0;
  }

  .btn-order {
    width: 100%;
    padding: 0.7rem 1rem;
    border: none;
    border-radius: var(--radius-sm);
    background: var(--primary);
    color: #fff;
    font-size: 0.9rem;
    font-weight: 700;
    cursor: pointer;
    transition: background 0.15s, transform 0.1s, box-shadow 0.15s;
    box-shadow: 0 2px 8px rgba(244, 98, 42, 0.3);
  }

  .btn-order:hover:not(:disabled) {
    background: #d9521f;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(244, 98, 42, 0.4);
  }

  .btn-order:disabled {
    background: var(--muted);
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
  }

  .msg {
    margin-top: 0.6rem;
    padding: 0.5rem 0.7rem;
    border-radius: var(--radius-sm);
    font-size: 0.78rem;
    font-weight: 500;
    line-height: 1.4;
  }

  .msg.ok  { background: #ecfdf5; color: #065f46; }
  .msg.err { background: #fef2f2; color: #991b1b; }

  /* ── Notificaciones panel ──────────────────────────────── */
  .notif-panel .section-title { margin-bottom: 0; }

  .notif-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .notif-title {
    font-size: 0.95rem;
    flex: 1;
  }

  .btn-refresh {
    flex-shrink: 0;
    width: 2rem;
    height: 2rem;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: var(--bg);
    color: var(--primary);
    font-size: 1rem;
    line-height: 1;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s;
  }

  .btn-refresh:hover:not(:disabled) {
    background: var(--primary-light);
    border-color: #fad3be;
  }

  .btn-refresh:disabled {
    opacity: 0.5;
    cursor: default;
  }

  .notif-err {
    font-size: 0.78rem;
    color: #991b1b;
    background: #fef2f2;
    padding: 0.5rem 0.6rem;
    border-radius: var(--radius-sm);
  }

  .notif-empty {
    font-size: 0.78rem;
    color: var(--muted);
    text-align: center;
    padding: 0.5rem 0;
  }

  .notif-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-height: 220px;
    overflow-y: auto;
  }

  .notif-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    padding: 0.55rem 0.65rem;
    background: var(--bg);
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    font-size: 0.78rem;
  }

  .notif-id {
    font-family: ui-monospace, monospace;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--primary);
  }

  .notif-msg {
    color: var(--text);
    line-height: 1.35;
  }

  .notif-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.35rem 0.75rem;
    font-size: 0.7rem;
    color: var(--muted);
  }

  .notif-estado {
    text-transform: capitalize;
    font-weight: 600;
    color: var(--accent);
  }

  .notif-time { font-variant-numeric: tabular-nums; }

  /* ── Log wrapper ───────────────────────────────────────── */
  .log-wrapper {
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
    padding: 0 1.5rem 2.5rem;
  }

  @media (max-width: 860px) {
    .log-wrapper { padding: 0 1rem 2rem; }
  }
</style>
