import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

export default function AuditLogModal({ ticket, isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('ticketAudit'); // 'ticketAudit' | 'emailLog'
  const [logs, setLogs] = useState([]);
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen, ticket]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (ticket?.id) {
        const ticketLogs = await apiService.getTicketAuditLogs(ticket.id);
        setLogs(ticketLogs);
      }
      const sentEmails = await apiService.getSentNotifications();
      setEmails(sentEmails);
    } catch (err) {
      console.error('Error cargando logs/notificaciones:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-850">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <span>Trazabilidad de Eventos &bull; {ticket ? `Ticket #${ticket.id}` : 'General'}</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                Observer Pattern
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Eventos despachados por el TicketSubject hacia AuditLogObserver y EmailNotifierObserver.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex border-b border-slate-800 bg-slate-950/40 px-5 pt-2 gap-4">
          <button
            onClick={() => setActiveTab('ticketAudit')}
            className={`pb-2 text-xs font-semibold border-b-2 transition ${
              activeTab === 'ticketAudit'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Historial de Auditoría ({logs.length})
          </button>
          <button
            onClick={() => setActiveTab('emailLog')}
            className={`pb-2 text-xs font-semibold border-b-2 transition ${
              activeTab === 'emailLog'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Correos Notificados ({emails.length})
          </button>
        </div>

        {/* Body */}
        <div className="p-5 overflow-y-auto flex-1 space-y-3">
          {loading ? (
            <div className="text-center py-10 text-slate-400 text-xs">Cargando eventos...</div>
          ) : activeTab === 'ticketAudit' ? (
            logs.length === 0 ? (
              <div className="text-center py-8 text-slate-500 text-xs">
                No hay eventos de auditoría registrados para este ticket.
              </div>
            ) : (
              <div className="relative border-l-2 border-indigo-500/30 ml-3 space-y-4">
                {logs.map((log) => (
                  <div key={log.id} className="relative pl-6">
                    <div className="absolute -left-[7px] top-1.5 w-3 h-3 rounded-full bg-indigo-500 ring-4 ring-slate-900" />
                    <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-xs shadow-sm">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-indigo-300 font-mono">
                          {log.event_type}
                        </span>
                        <span className="text-[10px] text-slate-400">
                          {new Date(log.created_at).toLocaleString()}
                        </span>
                      </div>
                      <div className="text-slate-300 flex items-center gap-2 font-mono text-[11px] mb-1">
                        <span className="px-1.5 py-0.5 rounded bg-slate-900 text-slate-400">
                          {log.old_status || 'INICIO'}
                        </span>
                        <span>&rarr;</span>
                        <span className="px-1.5 py-0.5 rounded bg-indigo-900/60 text-indigo-300 font-bold">
                          {log.new_status}
                        </span>
                      </div>
                      <p className="text-slate-400 text-[11px] mt-1">{log.details}</p>
                    </div>
                  </div>
                ))}
              </div>
            )
          ) : (
            emails.length === 0 ? (
              <div className="text-center py-8 text-slate-500 text-xs">
                No hay correos en la bandeja de despacho del observador.
              </div>
            ) : (
              <div className="space-y-3">
                {emails.map((mail, idx) => (
                  <div key={idx} className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-3 text-xs">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-cyan-300">
                        {mail.subject}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {new Date(mail.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <pre className="bg-slate-950 p-2.5 rounded-lg text-[11px] text-slate-300 font-mono whitespace-pre-wrap leading-relaxed border border-slate-800">
                      {mail.body}
                    </pre>
                  </div>
                ))}
              </div>
            )
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 flex justify-end bg-slate-900">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
