export interface ContainerNode {
  id: string;
  name: string;
  image: string;
  riskLevel: 'safe' | 'warning' | 'critical';
  cpu?: number;
  memory?: number;
  io?: number;
}
export interface ContainerEdge {
  id: string;
  source: string;
  target: string;
  type: 'network' | 'syscall' | 'file';
  weight?: number;
}
export interface SecurityEvent {
  id: string;
  timestamp: number;
  type: 'network' | 'syscall' | 'file' | 'process';
  containerId: string;
  containerName: string;
  severity: 'info' | 'warning' | 'critical';
  description: string;
  data?: any;
}
export interface Alert {
  id: string;
  timestamp: number;
  severity: 'warning' | 'critical';
  title: string;
  description: string;
  containerId?: string;
  containerName?: string;
}
export interface GraphData {
  nodes: ContainerNode[];
  edges: ContainerEdge[];
}
export interface Filters {
  showNetwork: boolean;
  showSyscall: boolean;
  showSuspicious: boolean;
  selectedContainer?: string;
}
