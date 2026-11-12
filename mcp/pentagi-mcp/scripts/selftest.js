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
ok('pentagi_status responde', !status.isError, textoStatus.slice(0, 120).replace(/\n/g, ' '))

const flows = await cliente.callTool({ name: 'pentagi_list_flows', arguments: {} })
ok('pentagi_list_flows responde', !flows.isError, (flows.content?.[0]?.text ?? '').slice(0, 80).replace(/\n/g, ' '))

await cliente.close()
console.log(`\nfalhas: ${falhas}`)
process.exit(falhas === 0 ? 0 : 1)
