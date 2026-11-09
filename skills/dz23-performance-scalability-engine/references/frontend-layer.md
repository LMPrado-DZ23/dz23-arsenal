# Camada 1 — Frontend & Interface (UX e renderização)

Cada item: **problema que evita** · **como implementar** · **diretriz**.

## 1.1 Skeleton Loaders
**Evita** layout shift (CLS) e a percepção de travamento; evita "tela branca" que o usuário interpreta como bug.
**Implementar** skeleton com as mesmas dimensões do conteúdo real, renderizado no primeiro paint (não depois do fetch). Reserve altura fixa (`min-height`, `aspect-ratio`) para o container. Use `aria-busy="true"` e `prefers-reduced-motion` para não animar infinitamente.
```tsx
// Card com dimensão reservada: nada pula quando o dado chega
<section aria-busy={isLoading} className="min-h-[220px]">
  {isLoading ? <SkeletonCard /> : <Card data={data} />}
</section>
```
**Diretriz** skeleton **substitui** o espaço final (mesma caixa). Se ele muda de tamanho, virou CLS. Spinner central sem dimensão reservada é o antipadrão.

## 1.2 Otimização de mídia
**Evita** payload de imagem 5–10× maior que o necessário e LCP alto; evita baixar o que está fora da tela.
**Implementar** WebP/AVIF com fallback por `<picture>`; `srcset` + `sizes` reais; `loading="lazy"` e `decoding="async"` fora da viewport; `fetchpriority="high"` **só** na imagem de LCP; dimensões explícitas (`width`/`height`) para reservar espaço.
```html
<picture>
  <source srcset="/img/hero.avif 1600w, /img/hero-800.avif 800w" type="image/avif" sizes="100vw">
  <source srcset="/img/hero.webp 1600w, /img/hero-800.webp 800w" type="image/webp" sizes="100vw">
  <img src="/img/hero-800.jpg" width="1600" height="900" alt="…"
       fetchpriority="high" decoding="async">
</picture>
<!-- abaixo da dobra -->
<img src="/img/x.webp" width="640" height="360" loading="lazy" decoding="async" alt="…">
```
**Diretriz** nunca `loading="lazy"` na imagem de LCP (atrasa o maior elemento). `sizes` errado faz o navegador baixar o maior arquivo — é o erro silencioso mais comum.

## 1.3 Code splitting & bundling
**Evita** bundle monolítico que atrasa TTI/INP; evita script de terceiro bloqueando a thread principal.
**Implementar** split por rota (o framework já faz em Next/Remix/Astro); componente pesado (editor, chart, mapa, modal raro) via `dynamic()`/`lazy()` com `Suspense`; terceiros com `defer`/`async` ou carregados após interação; analyse com `source-map-explorer`/`rollup-plugin-visualizer`.
```tsx
const Chart = dynamic(() => import('@/components/Chart'), { ssr: false, loading: () => <SkeletonChart /> });
// terceiro só quando necessário
export function loadGTM() { if (!window.__gtm) { const s = document.createElement('script'); s.src = '/gtm.js'; s.async = true; document.head.appendChild(s); window.__gtm = 1; } }
```
**Diretriz** budget por rota (ex.: ≤ 170 KB gzip de JS inicial). Se o terceiro entra no `<head>` síncrono, ele é parte do seu LCP — trate como código seu.

## 1.4 Virtualização de listas
**Evita** DOM com milhares de nós (scroll travado, memória alta, INP péssimo) em tabelas e feeds longos.
**Implementar** `@tanstack/react-virtual` com `estimateSize`, `overscan` 5–10, `measureElement` nas linhas de altura variável e container com altura fixa e `overflow: auto`.
```tsx
const rowVirtualizer = useVirtualizer({
  count: rows.length, getScrollElement: () => parentRef.current,
  estimateSize: () => 44, overscan: 8,
});
```
**Diretriz** virtualize a partir de ~100–200 linhas. Virtualização sem teste de scroll (teclado, `Ctrl+F`, impressão) quebra acessibilidade — prove com E2E.

## 1.5 Otimização de input
**Evita** requisição por tecla (rajada de chamadas, servidor saturado, resultado fora de ordem) e re-render por evento.
**Implementar** `debounce` 250–400 ms na busca; `throttle` em scroll/resize; `AbortController` cancelando a requisição anterior; estado de input controlado local, consulta em estado separado.
```ts
const search = useDebouncedCallback((q: string) => {
  ctrlRef.current?.abort();
  ctrlRef.current = new AbortController();
  fetch(`/api/search?q=${encodeURIComponent(q)}`, { signal: ctrlRef.current.signal });
}, 300);
```
**Diretriz** debounce **+ cancelamento**: só um dos dois deixa requisição órfã competindo. Autocomplete sem cancelamento mostra resultado antigo por cima do novo.

## 1.6 Fontes & estáticos
**Evita** FOIT/CLS de fonte, requisição a terceiro (Google Fonts) no caminho crítico e revalidação desnecessária de asset imutável.
**Implementar** self-host (`woff2`), no máximo 2–3 pesos e 1 eixo variável; `font-display: swap` + `size-adjust`/`ascent-override` para casar métrica da fallback; `preload` só da fonte acima da dobra; estáticos com hash no nome + `Cache-Control: public, max-age=31536000, immutable`.
```css
@font-face { font-family: Inter; src: url(/fonts/inter-var.woff2) format('woff2-variations');
  font-weight: 100 900; font-display: swap; }
```
**Diretriz** variável substitui 4 pesos estáticos. `immutable` exige nome com hash — sem hash, o arquivo fica preso no cache por um ano.

## 1.7 Resiliência mobile
**Evita** travamento em 3G/latência alta, timeout de 30 s percebido como "quebrou", e retry em tempestade.
**Implementar** teste com throttling real (DevTools "Slow 4G" + 300 ms RTT); timeouts curtos com retry exponencial e jitter; estado offline explícito; `prefetch` no idle para rotas prováveis; payload reduzido em conexão fraca (`navigator.connection.effectiveType`/`saveData`).
```ts
const ctrl = new AbortController();
const t = setTimeout(() => ctrl.abort(), 8000);
await fetch(url, { signal: ctrl.signal }).finally(() => clearTimeout(t));
```
**Diretriz** meça no device real ou emulando CPU 4× + rede 3G. "Funciona no meu desktop" não é evidência de performance mobile.

## Ordem de ataque nesta camada
1. Bundle inicial (maior impacto em TTI/INP) → 2. imagem de LCP → 3. listas longas → 4. inputs → 5. fontes → 6. skeleton (cosmético, mas barato) → 7. resiliência (teste, não código novo).

## Verificação
`Lighthouse`/`PageSpeed` para sintético; `web-vitals` para RUM (`onLCP`, `onINP`, `onCLS`); `PerformanceObserver` no waterfall. Sem RUM, o número é do seu laptop, não do usuário.
