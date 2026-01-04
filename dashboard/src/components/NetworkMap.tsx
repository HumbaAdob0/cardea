import { ReactFlow, Background, Controls } from '@xyflow/react';
import type { Edge, Node } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes: Node[] = [
  { 
    id: 'sentry', 
    type: 'input', 
    data: { label: 'Sentry Node (ThinkPad X230)' }, 
    position: { x: 50, y: 100 },
    className: 'bg-slate-900 text-cyan-400 border-cyan-800 rounded-md p-2 text-xs font-mono shadow-lg'
  },
  { 
    id: 'oracle', 
    type: 'output', 
    data: { label: 'Cardea Oracle (Azure Cloud)' }, 
    position: { x: 400, y: 100 },
    className: 'bg-slate-900 text-purple-400 border-purple-800 rounded-md p-2 text-xs font-mono shadow-lg'
  },
];

const initialEdges: Edge[] = [
  { 
    id: 'e-s-o', 
    source: 'sentry', 
    target: 'oracle', 
    animated: true, 
    label: 'Escalating Evidence',
    style: { stroke: '#06b6d4' }
  },
];

export const NetworkMap = () => {
  return (
    <div className="h-64 w-full bg-slate-950 rounded-xl border border-slate-900 overflow-hidden">
      <ReactFlow nodes={initialNodes} edges={initialEdges} fitView>
        <Background color="#1e293b" gap={20} />
        <Controls />
      </ReactFlow>
    </div>
  );
};