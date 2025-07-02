'use client'

import React, { useEffect, useRef } from 'react'

interface Props { markdown: string }

/**
 * Renders an interactive, zoomable mind-map from a markdown bullet-list using Markmap (D3-based).
 * Loading is done dynamically to avoid shipping heavy libraries to the server bundle.
 */
export default function MarkdownMindMap({ markdown }: Props) {
  const svgRef = useRef<SVGSVGElement | null>(null)
  const mmRef = useRef<any>(null)

  useEffect(() => {
    if (!markdown) return

    let cancelled = false

    async function render() {
      // Dynamically import heavy libraries only on the client.
      const [{ Markmap }, { Transformer }] = await Promise.all([
        import('markmap-view'),
        import('markmap-lib')
      ])

      if (cancelled || !svgRef.current) return

      const transformer = new Transformer()
      // Strip optional markdown fences so Markmap gets clean input
      const clean = markdown.replace(/```(?:markdown)?|```/g, '').trim()
      const { root } = transformer.transform(clean)

      if (mmRef.current) {
        // Update existing instance
        mmRef.current.setData(root)
        mmRef.current.fit()
      } else {
        mmRef.current = Markmap.create(svgRef.current, undefined, root)
      }
    }

    render()

    return () => {
      cancelled = true
    }
  }, [markdown])

  // svg must have an explicit height; width is 100% by default
  return <svg ref={svgRef} style={{ width: '100%', height: '600px' }} />
} 