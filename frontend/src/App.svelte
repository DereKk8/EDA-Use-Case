<script>
  let productos = []
  let carrito = []
  let cliente = ''
  let mensajePedido = ''
  let consultaId = ''
  let resultado = null

  async function cargarProductos() {
    const r = await fetch('/productos')
    productos = await r.json()
  }

  function agregar(p) {
    if (!carrito.find(x => x.id === p.id)) carrito = [...carrito, { ...p }]
  }

  function quitar(id) {
    carrito = carrito.filter(x => x.id !== id)
  }

  const total = () => carrito.reduce((s, p) => s + p.precio, 0).toLocaleString('es-CO')

  async function realizarPedido() {
    if (!cliente.trim() || carrito.length === 0) {
      mensajePedido = 'Ingresa tu nombre y agrega al menos un producto.'
      return
    }
    const r = await fetch('/pedidos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cliente, productos: carrito })
    })
    const data = await r.json()
    mensajePedido = `Pedido creado. ID: ${data.pedido_id}`
    consultaId = data.pedido_id
    carrito = []
    cliente = ''
  }

  async function consultar() {
    if (!consultaId.trim()) return
    const r = await fetch(`/pedidos/${consultaId}`)
    resultado = r.ok ? await r.json() : null
  }

  cargarProductos()
</script>

<h1>Sistema de Pedidos EDA</h1>

<section>
  <h2>Catálogo</h2>
  {#each productos as p}
    <div>
      <strong>{p.nombre}</strong> — ${p.precio.toLocaleString('es-CO')}
      <button on:click={() => agregar(p)}>+ Agregar</button>
    </div>
  {/each}
</section>

<section>
  <h2>Tu pedido</h2>
  <input bind:value={cliente} placeholder="Tu nombre" />
  {#each carrito as p}
    <div>{p.nombre} — ${p.precio.toLocaleString('es-CO')}
      <button on:click={() => quitar(p.id)}>Quitar</button>
    </div>
  {/each}
  <p>Total: <strong>${total()}</strong></p>
  <button on:click={realizarPedido}>Realizar Pedido</button>
  {#if mensajePedido}<p class="ok">{mensajePedido}</p>{/if}
</section>

<section>
  <h2>Consultar estado</h2>
  <input bind:value={consultaId} placeholder="Pega el pedido_id aquí" />
  <button on:click={consultar}>Consultar</button>

  {#if resultado}
    <p>Cliente: {resultado.cliente} | Total: ${resultado.total?.toLocaleString('es-CO')}</p>
    {#if resultado.notificacion}
      <p class="ok">✓ {resultado.notificacion.mensaje}</p>
    {:else}
      <p class="wait">Procesando... (el worker aún no escribió la notificación)</p>
    {/if}
  {:else if consultaId}
    <p class="err">Pedido no encontrado.</p>
  {/if}
</section>
