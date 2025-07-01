'use client'

import React, { useEffect, useRef } from 'react'

interface Props { chart: string }

export default function MermaidChart({ chart }: Props) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let isMounted = true

    async function renderMermaid() {
      const m = await import('mermaid')
      if (!isMounted) return

      const mermaid = m.default
      // Ensure mermaid is only initialized once per page load
      if (!(mermaid as any)._initialized) {
        mermaid.initialize({ startOnLoad: false, theme: 'dark' })
        ;(mermaid as any)._initialized = true
      }

      // Generate a unique id for each diagram so that multiple charts can coexist
      const id = `mermaid-${Date.now()}-${Math.random().toString(36).slice(2)}`

      try {
        const { svg, bindFunctions } = await (mermaid.render as any)(id, chart) as any
        if (ref.current) {
          ref.current.innerHTML = svg
          // In mermaid@10, bindFunctions is required for interactivity (e.g. mindmap collapse)
          bindFunctions?.(ref.current)
        }
      } catch (err) {
        // Fail gracefully so the whole app doesn't crash
        // eslint-disable-next-line no-console
        console.error('Mermaid render error:', err)
      }
    }

    renderMermaid()

    return () => {
      isMounted = false
    }
  }, [chart])

  return <div ref={ref} />
} 