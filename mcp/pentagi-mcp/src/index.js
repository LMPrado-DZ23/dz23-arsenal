#!/usr/bin/env node
/**
 * pentagi-mcp — expõe o PentAGI (plataforma de pentest autônomo self-hosted) como servidor MCP
 * stdio, para qualquer harness que fale MCP: DSH, Claude Code, Codex, Gemini CLI, Qwen Code,
 * OpenCode, Cursor.
 *
 * Fala GraphQL em https://<host>:8443/api/v1/graphql com Bearer token (API token do PentAGI).
 * Configuração por variável de ambiente:
 *   PENTAGI_URL    base do PentAGI (default https://127.0.0.1:8443)
 *   PENTAGI_TOKEN  API token (JWT). Se ausente, tenta PENTAGI_TOKEN_FILE.
 *   PENTAGI_TOKEN_FILE  caminho de um arquivo com o token
 *   PENTAGI_INSECURE=1  aceita certificado self-signed (default: 1 para localhost)
 *
 * Regra: nada de escrita sem intenção explícita. `pentagi_delete_flow` exige confirm=true.
 * Toda ferramenta devolve o erro do servidor em texto, não inventa resultado.
 */
import { readFileSync } from 'node:fs'
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { z } from 'zod'

const BASE = (process.env.PENTAGI_URL || 'https://127.0.0.1:8443').replace(/\/+$/, '')
const TOKEN = (() => {
  if (process.env.PENTAGI_TOKEN?.trim()) return process.env.PENTAGI_TOKEN.trim()
  const file = process.env.PENTAGI_TOKEN_FILE
  if (file) {
    try {
      return readFileSync(file, 'utf8').trim()
    } catch {
      return ''
    }
  }
  return ''
})()

// --- TLS: o PentAGI local sobe com certificado self-signed em https://127.0.0.1:8443 --------
// Node/undici recusam certificado self-signed. Resolvemos com um Agent do undici limitado a este
// processo, e so quando PENTAGI_INSECURE nao for "0". Sem rede envolvida, sem flag global de shell.
const INSEGURO = process.env.PENTAGI_INSECURE !== '0'
if (INSEGURO) {
  try {
    const { Agent, setGlobalDispatcher } = await import('undici')
    setGlobalDispatcher(new Agent({ connect: { rejectUnauthorized: false } }))
  } catch {
    // undici indisponivel: cai no ajuste de ambiente do Node (mesmo efeito, escopo deste processo)
    process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'
  }
}

const GQL_URL = `${BASE}/api/v1/graphql`

async function gql(query, variables = {}) {
  if (!TOKEN) {
    throw new Error(
      'PENTAGI_TOKEN ausente: crie um token em Settings → API Tokens do PentAGI e exporte PENTAGI_TOKEN ou PENTAGI_TOKEN_FILE',
    )
  }
  const res = await fetch(GQL_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${TOKEN}` },
    body: JSON.stringify({ query, variables }),
  })
  const texto = await res.text()
  if (!res.ok) throw new Error(`HTTP ${res.status} em ${GQL_URL}: ${texto.slice(0, 300)}`)
  let json
  try {
    json = JSON.parse(texto)
  } catch {
    throw new Error(`resposta não-JSON de ${GQL_URL}: ${texto.slice(0, 200)}`)
  }
  if (json.errors?.length) throw new Error(json.errors.map((e) => e.message).join('; '))
  return json.data
}

function texto(obj) {
  return { content: [{ type: 'text', text: JSON.stringify(obj, null, 2) }] }
}

function falha(erro) {
  return { isError: true, content: [{ type: 'text', text: `erro: ${erro.message || erro}` }] }
}

const server = new McpServer({ name: 'pentagi', version: '1.0.0' })

server.tool(
  'pentagi_status',
  'Saúde do PentAGI: versão, providers configurados e quantidade de flows. Use antes de qualquer outra ferramenta.',
  {},
  async () => {
    try {
      const [settings, providers, flows] = await Promise.all([
        gql('{ settings { version debug isDevelopMode } }'),
        gql('{ providers { name type } }').catch(() => ({ providers: [] })),
        gql('{ flows { id status } }').catch(() => ({ flows: [] })),
      ])
      return texto({
        base: BASE,
        autenticado: true,
        versao: settings.settings?.version,
        providers: providers.providers ?? [],
        flows: (flows.flows ?? []).length,
        atencao:
          (providers.providers ?? []).length === 0
            ? 'nenhum provider LLM configurado: create_flow vai falhar até configurar um (Settings → Providers)'
            : undefined,
      })
    } catch (e) {
      return falha(e)
    }
  },
)

server.tool(
  'pentagi_list_flows',
  'Lista os flows (avaliações) existentes: id, título, status, provider e datas.',
  {},
  async () => {
    try {
      const d = await gql('{ flows { id title status provider { name } createdAt updatedAt } }')
      return texto(d.flows ?? [])
    } catch (e) {
      return falha(e)
    }
  },
)

server.tool(
  'pentagi_get_flow',
  'Detalhe de um flow: status, provider e as tasks com subtasks. Use para acompanhar o progresso.',
  { flowId: z.string().describe('id numérico do flow (string)') },
  async ({ flowId }) => {
    try {
      const d = await gql(
        `query($id: ID) { flow(flowId: $id) { id title status provider { name } createdAt updatedAt
           tasks { id title status } } }`,
        { id: flowId },
      )
      if (!d.flow) return texto({ flowId, encontrado: false })
      return texto(d.flow)
    } catch (e) {
      return falha(e)
    }
  },
)

server.tool(
  'pentagi_create_flow',
  'Cria um flow de pentest: descreva o alvo e o objetivo em linguagem natural. Exige provider LLM configurado. Só rode contra alvo autorizado.',
  {
    input: z.string().min(10).describe('alvo e objetivo, ex.: "mapear portas e banner de 10.0.0.5 (autorizado)"'),
    provider: z.string().optional().describe('nome do provider (ex.: openai, anthropic, ollama, deepseek)'),
  },
  async ({ input, provider }) => {
    try {
      const d = await gql(
        `mutation($input: String, $provider: String) { createFlow(input: $input, modelProvider: $provider) {
           id title status provider createdAt } }`,
        { input, provider },
      )
      return texto(d.createFlow)
    } catch (e) {
      return falha(e)
    }
  },
)

server.tool(
  'pentagi_stop_flow',
  'Para um flow em execução (mantém o histórico).',
  { flowId: z.string() },
  async ({ flowId }) => {
    try {
      return texto(await gql('mutation($id: ID) { stopFlow(flowId: $id) { message } }', { id: flowId }))
    } catch (e) {
      return falha(e)
    }
  },
)

server.tool(
  'pentagi_finish_flow',
  'Encerra um flow como concluído e gera o resultado final.',
  { flowId: z.string() },
  async ({ flowId }) => {
    try {
      return texto(await gql('mutation($id: ID) { finishFlow(flowId: $id) { message } }', { id: flowId }))
    } catch (e) {
      return falha(e)
    }
  },
)

server.tool(
  'pentagi_put_input',
  'Envia uma instrução nova para um flow que está aguardando input (ex.: autorizar próximo passo).',
  { flowId: z.string(), input: z.string().min(1), provider: z.string().optional() },
  async ({ flowId, input, provider }) => {
    try {
      const d = await gql(
        'mutation($id: ID, $input: String, $p: String) { putUserInput(flowId: $id, input: $input, modelProvider: $p) { message } }',
        { id: flowId, input, p: provider },
      )
      return texto(d.putUserInput)
    } catch (e) {
      return falha(e)
    }
  },
)

server.tool(
  'pentagi_delete_flow',
  'DESTRUTIVO: apaga o flow e o histórico dele no PentAGI. Exige confirm=true.',
  { flowId: z.string(), confirm: z.literal(true).describe('true para confirmar a exclusão') },
  async ({ flowId }) => {
    try {
      return texto(await gql('mutation($id: ID) { deleteFlow(flowId: $id) { message } }', { id: flowId }))
    } catch (e) {
      return falha(e)
    }
  },
)

const transporte = new StdioServerTransport()
await server.connect(transporte)
