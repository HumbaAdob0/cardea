import { useEffect, useState } from 'react';
import { ReactFlow, Background, BackgroundVariant, Handle, Position, useNodesState, useEdgesState } from '@xyflow/react';
import type { Edge, Node, NodeProps } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Shield, Smartphone, Laptop, Cpu, Globe } from 'lucide-react';

// Define the interface for our node data to satisfy TypeScript
interface DeviceNodeData {
  label: string;
  type: 'sentry' | 'cloud' | 'asset';
  deviceType?: 'pc' | 'mobile' | 'iot';
  ip?: string;
  status: 'online' | 'offline' | 'alert';
  [key: string]: unknown;
}

const DeviceNode = ({ data }: NodeProps) => {
  const nodeData = data as unknown as DeviceNodeData;
  const isSentry = nodeData.type === 'sentry';
  const isCloud = nodeData.type === 'cloud';
  const isAlert = nodeData.status === 'alert';
  const isOffline = nodeData.status === 'offline';

  return (
    <div className={`px-4 py-3 rounded-lg border-2 font-mono flex items-center gap-3 transition-all duration-500
      ${isSentry ? 'bg-slate-950 border-cyan-500 text-cyan-500 shadow-[0_0_20px_rgba(6,182,212,0.3)]' : 
        isCloud ? 'bg-slate-950 border-purple-500 text-purple-500 shadow-[0_0_20px_rgba(168,85,247,0.3)]' :
        isAlert ? 'bg-red-950/20 border-red-500 text-red-500 shadow-[0_0_15px_rgba(239,68,68,0.4)] animate-pulse' :
        isOffline ? 'bg-slate-900 border-slate-800 text-slate-600 grayscale' :
        'bg-slate-900/80 border-slate-700 text-slate-400'}`}>
      
      <div className="shrink-0">
        {isSentry && <Shield size={16} className={isOffline ? 'opacity-20' : ''} />}
        {isCloud && <Globe size={16} />}
        {nodeData.deviceType === 'mobile' && <Smartphone size={16} />}
        {nodeData.deviceType === 'pc' && <Laptop size={16} />}
        {nodeData.deviceType === 'iot' && <Cpu size={16} />}
      </div>

      <div className="flex flex-col">
        <span className="text-[10px] font-bold uppercase tracking-tighter leading-none">{nodeData.label}</span>
        {nodeData.ip && <span className="text-[8px] opacity-60 mt-1">{nodeData.ip}</span>}
      </div>

      <Handle type="target" position={Position.Top} className="opacity-0" />
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
    </div>
  );
};

const nodeTypes = { device: DeviceNode };

export const NetworkMap = () => {
  // Explicitly type the state hooks to avoid 'never[]' assignment errors
  const [nodes, setNodes] = useNodesState<Node>([]);
  const [edges, setEdges] = useEdgesState<Edge>([]);
  const [stats, setStats] = useState({ deviceCount: 0, sentryOnline: false });

  const fetchData = async () => {
    try {
      // Endpoint must exist on your bridge_service.py
      const response = await fetch('http://localhost:8001/api/discovery');
      const data = await response.json();
      
      const newNodes: Node[] = data.devices.map((dev: any, index: number) => ({
        id: dev.id,
        type: 'device',
        data: { 
          label: dev.name, 
          type: dev.role, 
          deviceType: dev.category, 
          ip: dev.ip, 
          status: dev.status 
        },
        position: dev.role === 'sentry' ? { x: 250, y: 150 } : 
                  dev.role === 'cloud' ? { x: 250, y: -50 } : 
                  { x: 50 + (index * 150), y: 300 },
      }));

      const newEdges: Edge[] = data.links.map((link: any) => ({
        id: `e-${link.source}-${link.target}`,
        source: link.source,
        target: link.target,
        animated: link.active,
        style: { 
            stroke: link.status === 'alert' ? '#ef4444' : '#334155', 
            strokeWidth: link.active ? 2 : 1 
        }
      }));

      setNodes(newNodes);
      setEdges(newEdges);
      setStats({ 
          deviceCount: data.devices.filter((d: any) => d.role === 'asset').length,
          sentryOnline: data.devices.find((d: any) => d.role === 'sentry')?.status === 'online'
      });

    } catch (error) {
      console.error("Discovery Sync Error:", error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-full w-full min-h-[450px] bg-[#020617] rounded-xl border border-slate-900 overflow-hidden relative shadow-inner">
      <ReactFlow 
        nodes={nodes} 
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        colorMode="dark"
        nodesDraggable={true}
      >
        <Background color="#0f172a" variant={BackgroundVariant.Dots} gap={20} size={1} />
      </ReactFlow>
      
      <div className="absolute top-4 left-4 flex flex-col gap-1 text-[8px] font-bold uppercase tracking-widest text-slate-600">
        <span>Active Monitor: KitNET v2</span>
        <span>Assets Discovered: {stats.deviceCount}</span>
      </div>

      <div className="absolute bottom-4 left-4 flex gap-4 text-[9px] font-bold uppercase tracking-tighter text-slate-400 bg-slate-950/90 px-3 py-2 rounded-lg border border-slate-800 backdrop-blur-sm">
        <span className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${stats.sentryOnline ? 'bg-cyan-500 shadow-[0_0_8px_#06b6d4]' : 'bg-slate-700'}`} /> 
            SENTRY: {stats.sentryOnline ? 'ONLINE' : 'OFFLINE'}
        </span>
      </div>
    </div>
  );
};