'use client';

import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Database,
  GitMerge,
  Cpu,
  CheckCircle2,
  XCircle,
  Zap
} from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

interface Stats {
  total_organizations: number;
  active_connectors: number;
  total_records_ingested: number;
  resolved_entities_count: number;
  pending_approvals_count: number;
  executed_tasks_count: number;
}

interface AgentTask {
  id: string;
  resolved_entity_id: string;
  title: string;
  description: string;
  priority: string;
  status: string;
  proposed_tool_name: string;
  proposed_tool_args: any;
  ai_confidence_score: number;
  ai_reasoning: string;
  requires_human_approval: boolean;
  approved_by?: string;
  approval_notes?: string;
  created_at: string;
}

interface Entity {
  id: string;
  primary_name: string;
  domain: string;
  entity_type: string;
  attributes: any;
  match_confidence: number;
}

interface Connector {
  id: string;
  name: string;
  connector_type: string;
  status: string;
  records_count: number;
  last_synced_at: string;
}

interface AuditLog {
  id: string;
  actor: string;
  action: string;
  details: any;
  timestamp: string;
}

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<'agent-queue' | 'connectors' | 'entities' | 'audit'>('agent-queue');
  const [liveToast, setLiveToast] = useState<string | null>(null);

  const { isConnected, lastEvent } = useWebSocket('ws://localhost:8000/api/v1/ws/events');

  const [stats, setStats] = useState<Stats>({
    total_organizations: 0,
    active_connectors: 0,
    total_records_ingested: 0,
    resolved_entities_count: 0,
    pending_approvals_count: 0,
    executed_tasks_count: 0
  });

  const [tasks, setTasks] = useState<AgentTask[]>([]);
  const [entities, setEntities] = useState<Entity[]>([]);
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);

  // Fetch initial data from FastAPI backend endpoints
  const fetchDashboardData = async () => {
    try {
      const [statsRes, connRes, entRes, taskRes, auditRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/dashboard/stats'),
        fetch('http://localhost:8000/api/v1/connectors'),
        fetch('http://localhost:8000/api/v1/entities'),
        fetch('http://localhost:8000/api/v1/agent/tasks'),
        fetch('http://localhost:8000/api/v1/audit-logs')
      ]);

      if (statsRes.ok) setStats(await statsRes.json());
      if (connRes.ok) setConnectors(await connRes.json());
      if (entRes.ok) setEntities(await entRes.json());
      if (taskRes.ok) setTasks(await taskRes.json());
      if (auditRes.ok) setAuditLogs(await auditRes.json());
    } catch (err) {
      console.error('Error fetching backend data points:', err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Real-time Event Listener via WebSockets
  useEffect(() => {
    if (!lastEvent) return;

    if (lastEvent.type === 'RECORD_INGESTED') {
      const data = lastEvent.data;
      setStats(prev => ({
        ...prev,
        total_records_ingested: prev.total_records_ingested + 1
      }));
      setLiveToast(`⚡ Real-time Record Ingested: ${data.company_name} - ${data.subject}`);
    } else if (lastEvent.type === 'AGENT_TASK_CREATED') {
      const newTask = lastEvent.data;
      setTasks(prev => [newTask, ...prev]);
      setStats(prev => ({
        ...prev,
        pending_approvals_count: prev.pending_approvals_count + 1
      }));
      setLiveToast(`🤖 Real-time AI Agent Task Queued: ${newTask.title}`);
    } else if (lastEvent.type === 'AUDIT_LOG_ADDED') {
      setAuditLogs(prev => [lastEvent.data, ...prev]);
    }
  }, [lastEvent]);

  // Auto-dismiss toast notification
  useEffect(() => {
    if (liveToast) {
      const timer = setTimeout(() => setLiveToast(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [liveToast]);

  const handleReviewTask = async (taskId: string, approved: boolean) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/agent/tasks/${taskId}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          approved,
          reviewer: 'fde_lead@enterprise.com',
          notes: approved ? 'Approved via NexusOps Control Plane UI' : 'Rejected via Control Plane UI'
        })
      });

      if (res.ok) {
        const updatedTask = await res.json();
        setTasks(prevTasks => prevTasks.map(t => t.id === taskId ? updatedTask : t));
        fetchDashboardData(); // Refresh stats & audit logs from DB
        setLiveToast(`✅ Action ${approved ? 'EXECUTED' : 'REJECTED'} & logged to database audit trail.`);
      }
    } catch (err) {
      console.error('Error submitting review:', err);
    }
  };

  return (
    <div>
      {/* Realtime Connection Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <span style={{
            display: 'inline-block',
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: isConnected ? '#10b981' : '#f59e0b',
            boxShadow: isConnected ? '0 0 10px #10b981' : 'none'
          }} />
          <span style={{ fontSize: '0.85rem', fontWeight: '600', color: isConnected ? '#10b981' : '#f59e0b' }}>
            {isConnected ? 'LIVE BACKEND WEBSOCKET CONNECTED (PORT 8000)' : 'CONNECTING TO FASTAPI BACKEND...'}
          </span>
        </div>

        {liveToast && (
          <div style={{
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(6, 182, 212, 0.2))',
            border: '1px solid var(--border-glow)',
            padding: '0.4rem 1rem',
            borderRadius: '8px',
            fontSize: '0.85rem',
            fontWeight: '600',
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <Zap size={16} color="#06b6d4" />
            {liveToast}
          </div>
        )}
      </div>

      {/* Top Overview Metrics */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Active Data Connectors</div>
          <div className="stat-value" style={{ color: 'var(--primary-cyan)' }}>{stats.active_connectors}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Records Ingested</div>
          <div className="stat-value">{stats.total_records_ingested.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Resolved Entities</div>
          <div className="stat-value" style={{ color: 'var(--primary-indigo)' }}>{stats.resolved_entities_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pending AI Approvals</div>
          <div className="stat-value" style={{ color: stats.pending_approvals_count > 0 ? 'var(--accent-amber)' : 'var(--accent-emerald)' }}>
            {stats.pending_approvals_count}
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="tab-navigation">
        <button
          className={`tab-btn ${activeTab === 'agent-queue' ? 'active' : ''}`}
          onClick={() => setActiveTab('agent-queue')}
        >
          <Cpu size={18} />
          Human-in-the-Loop Queue ({tasks.filter(t => t.status === 'AWAITING_APPROVAL').length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'connectors' ? 'active' : ''}`}
          onClick={() => setActiveTab('connectors')}
        >
          <Database size={18} />
          Data Connectors ({connectors.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'entities' ? 'active' : ''}`}
          onClick={() => setActiveTab('entities')}
        >
          <GitMerge size={18} />
          Entity Knowledge Graph ({entities.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          <ShieldCheck size={18} />
          Audit Trail ({auditLogs.length})
        </button>
      </div>

      {/* TAB 1: Human-In-The-Loop AI Approval Queue */}
      {activeTab === 'agent-queue' && (
        <div className="card-panel">
          <div className="card-title-group">
            <div>
              <h2 className="panel-title">AI Agent Workflow Execution Queue</h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                High-risk AI recommendations queued from SQLite/Postgres DB for FDE verification & 1-click execution.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {tasks.map(task => (
              <div key={task.id} style={{
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '1.25rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                  <div>
                    <span className={`badge badge-${task.status}`}>{task.status.replace('_', ' ')}</span>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginTop: '0.5rem' }}>{task.title}</h3>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>AI Confidence Score</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: '700', color: 'var(--primary-cyan)' }}>
                      {(task.ai_confidence_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>

                <p style={{ fontSize: '0.9rem', color: '#d1d5db', marginBottom: '1rem', lineHeight: '1.5' }}>
                  {task.description}
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
                  <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
                      AI Reasoning & Risk Analysis
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#93c5fd' }}>{task.ai_reasoning}</div>
                  </div>
                  <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
                      Proposed Enterprise Tool Call
                    </div>
                    <div className="code-block">
                      {task.proposed_tool_name}({JSON.stringify(task.proposed_tool_args)})
                    </div>
                  </div>
                </div>

                {task.status === 'AWAITING_APPROVAL' ? (
                  <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
                    <button className="btn-danger" onClick={() => handleReviewTask(task.id, false)}>
                      Reject Action
                    </button>
                    <button className="btn-primary" onClick={() => handleReviewTask(task.id, true)}>
                      Approve & Execute Tool
                    </button>
                  </div>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: task.status === 'EXECUTED' ? 'var(--accent-emerald)' : 'var(--accent-crimson)', fontSize: '0.9rem', fontWeight: '600' }}>
                    {task.status === 'EXECUTED' ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
                    Task {task.status.toLowerCase()} by {task.approved_by || 'fde_lead@enterprise.com'}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 2: Data Connectors & Ingestion */}
      {activeTab === 'connectors' && (
        <div className="card-panel">
          <h2 className="panel-title" style={{ marginBottom: '1rem' }}>Multi-Tenant Data Connectors</h2>
          <table className="data-table">
            <thead>
              <tr>
                <th>Connector Name</th>
                <th>Type</th>
                <th>Status</th>
                <th>Records Ingested</th>
                <th>Last Synced</th>
              </tr>
            </thead>
            <tbody>
              {connectors.map(c => (
                <tr key={c.id}>
                  <td style={{ fontWeight: '600' }}>{c.name}</td>
                  <td><span className="code-block" style={{ fontSize: '0.75rem' }}>{c.connector_type}</span></td>
                  <td><span className="badge badge-ACTIVE">{c.status}</span></td>
                  <td>{c.records_count.toLocaleString()}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{c.last_synced_at ? new Date(c.last_synced_at).toLocaleTimeString() : 'Just now'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* TAB 3: Entity Knowledge Graph */}
      {activeTab === 'entities' && (
        <div className="card-panel">
          <h2 className="panel-title" style={{ marginBottom: '1rem' }}>Unified Customer Knowledge Graph</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {entities.map(e => (
              <div key={e.id} style={{
                background: 'rgba(0, 0, 0, 0.4)',
                border: '1px solid var(--border-glow)',
                borderRadius: '12px',
                padding: '1.25rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: '700' }}>{e.primary_name}</h3>
                  <span className="badge badge-ACTIVE">{e.entity_type}</span>
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--primary-cyan)', marginBottom: '1rem' }}>Domain: {e.domain}</div>
                <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem', borderRadius: '8px', fontSize: '0.85rem' }}>
                  <div><strong>ARR:</strong> {e.attributes?.annual_contract_value || '$500,000'}</div>
                  <div><strong>Contract Tier:</strong> {e.attributes?.tier || 'Enterprise'}</div>
                  <div><strong>Health:</strong> {e.attributes?.health_score || 'HEALTHY'}</div>
                  <div style={{ marginTop: '0.4rem', color: 'var(--primary-indigo)' }}>
                    <strong>Fuzzy Match Score:</strong> {(e.match_confidence * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 4: Audit Trail */}
      {activeTab === 'audit' && (
        <div className="card-panel">
          <h2 className="panel-title" style={{ marginBottom: '1rem' }}>Immutable Audit Log & Governance Records</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {auditLogs.map(log => (
              <div key={log.id} style={{
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid var(--border-color)',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                display: 'flex',
                justify: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--primary-cyan)', fontWeight: '600', marginRight: '0.75rem' }}>
                    [{log.actor}]
                  </span>
                  <span style={{ fontSize: '0.9rem', fontWeight: '600' }}>{log.action}</span>
                  <div className="code-block" style={{ marginTop: '0.4rem', fontSize: '0.75rem' }}>
                    {JSON.stringify(log.details)}
                  </div>
                </div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : 'Just now'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
