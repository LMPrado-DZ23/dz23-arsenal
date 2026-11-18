#!/usr/bin/env node
/**
 * selftest — abre o servidor por stdio como um cliente MCP faria e exercita as ferramentas
 * de leitura. Falha se o handshake, o list ou o status não funcionarem.
 *
 * Uso: node scripts/selftest.js
 */
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const aqui = dirname(fileURLToPath(import.meta.url))
const servidor = join(aqui, '..', 'src', 'index.js')

const transporte = new StdioClientTransport({
  command: process.execPath,
  args: [servidor],
  env: { ...process.env },
})
const cliente = new Client({ name: 'selftest', version: '1.0.0' })

let falhas = 0
function ok(nome, cond, extra = '') {
  console.log(`${cond ? 'ok  ' : 'FALHA'} ${nome}${extra ? ' — ' + extra : ''}`)
  if (!cond) falhas++
}

await cliente.connect(transporte)
console.log('handshake: conectado')

const lista = await cliente.listTools()
ok('tools/list', lista.tools.length >= 6, `${lista.tools.length} ferramentas`)
const nomes = lista.tools.map((t) => t.name)
for (const obrig of ['pentagi_status', 'pentagi_list_flows', 'pentagi_create_flow']) {
  ok(`ferramenta ${obrig}`, nomes.includes(obrig))
}

const status = await cliente.callTool({ name: 'pentagi_status', arguments: {} })
const textoStatus = status.content?.[0]?.text ?? ''

// O PentAGI é um serviço local self-hosted: na ausência dele, a resposta correta NÃO é sucesso,
// e o teste não pode exigir sucesso para dizer que o servidor está bem. A versão anterior marcava
// FALHA em qualquer máquina sem o serviço de pé -- um sinal falso que fazia o selftest ser
// ignorado justamente onde mais se precisava dele. Agora distinguimos os dois estados: com
// serviço acessível exigimos dados; sem ele exigimos que a degradação seja acionável (endpoint +
// causa), que é o contrato real desta ferramenta.
let servicoAlcancavel = true
try {
  const { request } = await import('undici')
  const probe = await request({
    url: (process.env.PENTAGI_URL || 'https://127.0.0.1:8443').replace(/\/+$/, '') + '/api/v1/graphql',
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query: '{ __typename }' }),
    tls: { rejectUnauthorized: false },
    headersTimeout: 5000,
    bodyTimeout: 5000,
  }).catch(() => null)
  servicoAlcancavel = Boolean(probe)
} catch {
  servicoAlcancavel = false
}

if (servicoAlcancavel) {
  ok('pentagi_status responde', !status.isError, textoStatus.slice(0, 120).replace(/\n/g, ' '))
  const flows = await cliente.callTool({ name: 'pentagi_list_flows', arguments: {} })
  ok('pentagi_list_flows responde', !flows.isError, (flows.content?.[0]?.text ?? '').slice(0, 80).replace(/\n/g, ' '))
} else {
  console.log('AVISO: servico PentAGI inacessivel -- cobrando degradacao acionavel, nao sucesso')
  const temToken = Boolean(process.env.PENTAGI_TOKEN?.trim() || process.env.PENTAGI_TOKEN_FILE)
  if (!temToken) {
    // sem credencial, a mensagem precisa dizer exatamente o que criar e onde
    ok('sem token: mensagem orienta', /PENTAGI_TOKEN/.test(textoStatus) && /Settings|API Tokens/.test(textoStatus),
      textoStatus.slice(0, 90).replace(/\n/g, ' '))
  } else {
    // com credencial mas sem serviço: precisa citar a causa e o endpoint, nunca só "fetch failed"
    const citouEndpoint = /graphql|127\.0\.0\.1:8443|PENTAGI_URL/.test(textoStatus)
    const citouCausa = /ECONN|ENOTFOUND|fetch failed|nao respondeu/i.test(textoStatus)
    ok('rede fora: cita causa', citouCausa, textoStatus.slice(0, 90).replace(/\n/g, ' '))
    ok('rede fora: cita endpoint', citouEndpoint, '')
    ok('rede fora: isError definido', status.isError === true, '')
  }
  const flows = await cliente.callTool({ name: 'pentagi_list_flows', arguments: {} })
  ok('list_flows tambem degrada sem derrubar o servidor', flows.isError === true,
    (flows.content?.[0]?.text ?? '').slice(0, 60).replace(/\n/g, ' '))
  // o servidor precisa sobreviver ao erro de rede e continuar respondendo
  const listaDepois = await cliente.listTools()
  ok('servidor vivo apos erro de rede', listaDepois.tools.length >= 6, `${listaDepois.tools.length} ferramentas`)
}

await cliente.close()
console.log(`\nfalhas: ${falhas}`)
process.exit(falhas === 0 ? 0 : 1)
