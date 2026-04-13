<script>
  /** 0 = idle, 1 = OrderCreated, 2 = BrokerQueued, 3 = OrderReady, 4 = Completed */
  export let step = 0

  const stages = [
    {
      id: 1,
      event: 'OrderCreated',
      label: 'Pedido Enviado',
      icon: '📤',
      desc: 'El Productor publica el evento OrderCreated al broker de mensajes (Kafka).',
    },
    {
      id: 2,
      event: 'OrderQueued',
      label: 'Broker Procesando',
      icon: '📨',
      desc: 'Kafka recibe el evento, lo encola en el topic y lo entrega al Worker consumidor.',
    },
    {
      id: 3,
      event: 'OrderReady',
      label: 'Pedido Listo',
      icon: '✅',
      desc: 'El Worker consume el evento, procesa el pedido y escribe la notificación en Redis.',
    },
  ]
</script>

<div class="eda-panel">
  <div class="eda-header">
    <h2>Flujo de Eventos</h2>
    <span class="tech-badge">Kafka · Redis</span>
  </div>

  <div class="pipeline">
    {#each stages as s, i}
      <div class="stage" class:done={step > s.id} class:active={step === s.id} class:idle={step < s.id}>
        <div class="dot-col">
          <div class="dot">
            {#if step > s.id}
              <span class="check">✓</span>
            {:else if step === s.id}
              <span class="pulse-ring"></span>
              <span class="dot-inner"></span>
            {:else}
              <span class="dot-num">{s.id}</span>
            {/if}
          </div>
          {#if i < stages.length - 1}
            <div class="connector" class:filled={step > s.id}></div>
          {/if}
        </div>

        <div class="stage-body">
          <code class="event-tag">{s.event}</code>
          <span class="stage-label">{s.label}</span>
          {#if step === s.id}
            <p class="stage-desc">{s.desc}</p>
          {/if}
        </div>
      </div>
    {/each}
  </div>

  <div class="explanation">
    {#if step === 0}
      <p>Coloca un pedido para ver el flujo de eventos en tiempo real.</p>
    {:else if step < 3}
      <p>Procesando… el Worker está consumiendo el evento de Kafka.</p>
    {:else if step === 3}
      <p>Evento consumido. Confirmando finalización del flujo…</p>
    {:else}
      <p>¡Pedido completado! El Worker procesó el evento y notificó al cliente.</p>
    {/if}
  </div>

  <p class="caption">
    El <strong>Productor</strong> publica eventos al <strong>Broker (Kafka)</strong>.
    El Broker los encola y el <strong>Worker</strong> los consume para confirmar el pedido.
  </p>
</div>

<style>
  .eda-panel {
    background: var(--surface);
    border-radius: var(--radius);
    padding: 1.25rem;
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border);
  }

  .eda-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.25rem;
  }

  .eda-header h2 {
    margin: 0;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text);
  }

  .tech-badge {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    background: #e0f2fe;
    color: #0369a1;
    padding: 0.2rem 0.5rem;
    border-radius: 999px;
  }

  /* ── Pipeline ───────────────────────────── */
  .pipeline {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-bottom: 1rem;
  }

  .stage {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
  }

  .dot-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex-shrink: 0;
  }

  .dot {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    transition: background 0.3s, border-color 0.3s;
    border: 2px solid var(--border);
    background: var(--bg);
    flex-shrink: 0;
  }

  .stage.done .dot {
    background: var(--accent);
    border-color: var(--accent);
  }

  .stage.active .dot {
    background: var(--primary);
    border-color: var(--primary);
  }

  .check {
    color: #fff;
    font-size: 0.85rem;
    font-weight: 700;
  }

  .dot-num {
    color: var(--muted);
    font-size: 0.75rem;
    font-weight: 600;
  }

  .dot-inner {
    width: 0.5rem;
    height: 0.5rem;
    border-radius: 50%;
    background: #fff;
  }

  /* Pulse ring animation for current step */
  .pulse-ring {
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    border: 2px solid var(--primary);
    animation: pulse-ring 1.4s ease-out infinite;
  }

  @keyframes pulse-ring {
    0%   { opacity: 0.8; transform: scale(1); }
    100% { opacity: 0;   transform: scale(1.5); }
  }

  .connector {
    width: 2px;
    height: 2rem;
    background: var(--border);
    transition: background 0.4s;
    margin: 0.15rem 0;
  }

  .connector.filled {
    background: var(--accent);
  }

  /* ── Stage body ────────────────────────── */
  .stage-body {
    padding: 0.25rem 0 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }

  .event-tag {
    font-size: 0.7rem;
    font-weight: 600;
    font-family: 'SF Mono', 'Fira Code', monospace;
    color: var(--primary);
    background: var(--primary-light);
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    width: fit-content;
  }

  .stage.idle .event-tag {
    color: var(--muted);
    background: var(--bg);
  }

  .stage.done .event-tag {
    color: var(--accent);
    background: #ecfdf5;
  }

  .stage-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text);
  }

  .stage.idle .stage-label {
    color: var(--muted);
  }

  .stage-desc {
    font-size: 0.72rem;
    color: var(--muted);
    margin: 0.25rem 0 0;
    line-height: 1.4;
    animation: fade-in 0.3s ease;
  }

  @keyframes fade-in {
    from { opacity: 0; transform: translateY(-4px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  /* ── Footer texts ──────────────────────── */
  .explanation {
    font-size: 0.78rem;
    color: var(--muted);
    background: var(--bg);
    border-radius: var(--radius-sm);
    padding: 0.6rem 0.75rem;
    margin-bottom: 0.75rem;
    min-height: 2.5rem;
    line-height: 1.5;
  }

  .explanation p {
    margin: 0;
  }

  .caption {
    font-size: 0.7rem;
    color: var(--muted);
    line-height: 1.5;
    margin: 0;
    border-top: 1px solid var(--border);
    padding-top: 0.75rem;
  }

  .caption strong {
    color: var(--text);
  }
</style>
