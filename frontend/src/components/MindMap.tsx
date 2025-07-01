import React from 'react'
import ReactFlow, { Background, Controls, MiniMap, Node, Edge } from 'reactflow'
import 'reactflow/dist/style.css'

interface Props { markdown: string }

export default function MindMap({ markdown }: Props) {
  const clean = markdown.replace(/```markdown|```/g, '').trim()
  const lines = clean.split(/\r?\n/).filter(l => l.trim())
  const nodes: Node[] = []
  const edges: Edge[] = []
  const stack: { id: string; index: number }[] = []

  // Group nodes by level to compute radial positions
  const levelCounts: Record<number, number> = {}

  lines.forEach((raw) => {
    const match = raw.match(/^(\s*)[\-*]?\s*(.+)$/)
    if (!match) return
    const indent = match[1].length
    const level = Math.floor(indent / 2)
    levelCounts[level] = (levelCounts[level] || 0) + 1
  })

  let levelCurrentIndex: Record<number, number> = {}

  const center = { x: 0, y: 0 }
  const radiusStep = 200

  lines.forEach((raw, i) => {
    const match = raw.match(/^(\s*)[\-*]?\s*(.+)$/)
    if (!match) return
    const indent = match[1].length
    const level = Math.floor(indent / 2)
    const id = `n${i}`

    // Current index within this level
    const idx = levelCurrentIndex[level] || 0
    levelCurrentIndex[level] = idx + 1

    // Calculate angular spacing
    const total = levelCounts[level] || 1
    const angle = (idx / total) * Math.PI * 2
    const r = level * radiusStep
    const x = center.x + r * Math.cos(angle)
    const y = center.y + r * Math.sin(angle)

    nodes.push({ id, data: { label: match[2] }, position: { x, y } })

    // Record stack to create edges (parent-child)
    stack[level] = { id, index: i }
    if (level > 0 && stack[level - 1]) {
      edges.push({
        id: `e${i}`,
        source: stack[level - 1].id,
        target: id,
        animated: false,
        style: { stroke: '#888', strokeWidth: 2 },
        type: 'smoothstep'
      })
    }
  })

  return (
    <div style={{ height: 600 }}>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <MiniMap />
        <Controls />
        <Background gap={16} />
      </ReactFlow>
    </div>
  )
} 