export interface Alert {
    id: number;
    source: string;
    alert_type: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    title: string;
    description: string;
    timestamp: string;
    threat_score?: number;
    raw_data?: Record<string, any>;
  }
  
  export interface AnalyticsResponse {
    total_alerts: number;
    risk_score: number;
    alerts: Alert[];
    // Extended fields from Oracle backend
    time_range?: string;
    alerts_by_severity?: Record<string, number>;
    alerts_by_type?: Record<string, number>;
    top_threats?: ThreatInfo[];
    trend_data?: Record<string, any>[];
    generated_at?: string;
  }

  export interface ThreatInfo {
    threat_id: string;
    threat_type: string;
    severity: string;
    confidence_score: number;
    first_seen: string;
    last_seen: string;
    indicators: string[];
    affected_assets: string[];
  }

  export interface FlowData {
    nodes: Array<{
      id: string;
      type: string;
      data: { label: string; status?: string };
      position: { x: number; y: number };
    }>;
    edges: Array<{
      id: string;
      source: string;
      target: string;
      animated?: boolean;
    }>;
  }