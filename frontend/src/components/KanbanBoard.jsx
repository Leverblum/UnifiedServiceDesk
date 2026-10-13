import React, { useState } from 'react';

const COLUMNS = [
  { id: 'OPEN', title: 'Abiertos (Open)', bgHeader: 'from-sky-500/20 to-sky-600/10', border: 'border-sky-500/30', badge: 'bg-sky-500/20 text-sky-300' },
  { id: 'IN_PROCESS', title: 'En Proceso (In Process)', bgHeader: 'from-amber-500/20 to-amber-600/10', border: 'border-amber-500/30', badge: 'bg-amber-500/20 text-amber-300' },
  { id: 'RESOLVED', title: 'Resueltos (Resolved)', bgHeader: 'from-emerald-500/20 to-emerald-600/10', border: 'border-emerald-500/30', badge: 'bg-emerald-500/20 text-emerald-300' },
  { id: 'CLOSED', title: 'Cerrados (Closed)', bgHeader: 'from-slate-700/30 to-slate-800/10', border: 'border-slate-700/40', badge: 'bg-slate-700/40 text-slate-300' },
];

export default function KanbanBoard({
  tickets,
  onTransitionStatus,
  onViewAudit,
  onDeleteTicket,
  isLoading,
}) {
  const [filterCategory, setFilterCategory] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [actionLoadingId, setActionLoadingId] = useState(null);

  // Filtrado reactivo
  const filteredTickets = tickets.filter(ticket => {
    const matchesCategory = filterCategory ? ticket.category === filterCategory : true;
    const matchesSearch = searchQuery
      ? ticket.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ticket.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ticket.id.toString().includes(searchQuery)
      : true;
    return matchesCategory && matchesSearch;
  });

  const handleAction = async (ticketId, targetStatus, reason) => {
    try {
      setActionLoadingId(ticketId);
      await onTransitionStatus(ticketId, targetStatus, reason);
    } finally {
      setActionLoadingId(null);
    }
  };

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'MEDIUM':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      default:
        return 'bg-slate-700/40 text-slate-300 border-slate-600/40';
    }
  };

  const getCategoryBadge = (category) => {
    switch (category) {
      case 'HARDWARE':
        return 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30';
      case 'SOFTWARE':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      case 'ACCESS':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      default:
        return 'bg-slate-700/40 text-slate-300 border-slate-600/40';
    }
  };

  return (
    <div className="space-y-4">
      {/* Barra de Filtros y Búsqueda */}
      <div className="bg-slate-900/80 border border-slate-800 p-3.5 rounded-xl flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-72">
          <input
            type="text"
            placeholder="Buscar por ID, título o detalle..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-800/80 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <label className="text-xs text-slate-400 font-medium">Categoría:</label>
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Todas las Fábricas</option>
            <option value="HARDWARE">Hardware (HW Factory)</option>
            <option value="SOFTWARE">Software (SW Factory)</option>
            <option value="ACCESS">Acceso & Seguridad (Access Factory)</option>
          </select>
        </div>
      </div>

      {/* Tablero Kanban (Columnas por Estado) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {COLUMNS.map((col) => {
          const colTickets = filteredTickets.filter((t) => t.status === col.id);

          return (
            <div
              key={col.id}
              className={`bg-slate-900/60 border ${col.border} rounded-2xl flex flex-col min-h-[580px] shadow-lg overflow-hidden`}
            >
              {/* Header de Columna */}
              <div className={`p-3.5 bg-gradient-to-b ${col.bgHeader} border-b border-slate-800/80 flex items-center justify-between`}>
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-xs uppercase tracking-wider text-white">
                    {col.title}
                  </h3>
                </div>
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${col.badge}`}>
                  {colTickets.length}
                </span>
              </div>

              {/* Lista de Tarjetas */}
              <div className="p-3 space-y-3 flex-1 overflow-y-auto">
                {colTickets.length === 0 ? (
                  <div className="h-44 flex flex-col items-center justify-center text-slate-600 text-xs border border-dashed border-slate-800 rounded-xl p-4 text-center">
                    <span>Sin tickets en este estado</span>
                  </div>
                ) : (
                  colTickets.map((ticket) => (
                    <div
                      key={ticket.id}
                      className="bg-slate-800/90 border border-slate-700/80 rounded-xl p-3.5 shadow-md hover:border-slate-600 transition flex flex-col justify-between gap-3 group"
                    >
                      {/* Top Bar: ID + Badges */}
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[11px] font-mono font-bold text-slate-400">
                            #{ticket.id}
                          </span>
                          <div className="flex items-center gap-1.5">
                            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${getCategoryBadge(ticket.category)}`}>
                              {ticket.category}
                            </span>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getPriorityBadge(ticket.priority)}`}>
                              {ticket.priority}
                            </span>
                          </div>
                        </div>

                        {/* Title & Description */}
                        <h4 className="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors">
                          {ticket.title}
                        </h4>
                        <p className="mt-1 text-xs text-slate-300 line-clamp-3 leading-relaxed">
                          {ticket.description}
                        </p>

                        {/* Specific Metadata (Polimorfismo de Factory) */}
                        {ticket.specific_metadata && Object.keys(ticket.specific_metadata).length > 0 && (
                          <div className="mt-2.5 p-2 rounded-lg bg-slate-900/70 border border-slate-800 text-[11px] text-slate-400 space-y-0.5 font-mono">
                            {ticket.category === 'HARDWARE' && (
                              <>
                                {ticket.specific_metadata.serial_number && (
                                  <div><span className="text-indigo-400">S/N:</span> {ticket.specific_metadata.serial_number}</div>
                                )}
                                {ticket.specific_metadata.device_type && (
                                  <div><span className="text-indigo-400">Dispositivo:</span> {ticket.specific_metadata.device_type}</div>
                                )}
                              </>
                            )}
                            {ticket.category === 'SOFTWARE' && (
                              <>
                                <div><span className="text-cyan-400">App:</span> {ticket.specific_metadata.software_name}</div>
                                <div><span className="text-cyan-400">Ver:</span> {ticket.specific_metadata.version}</div>
                              </>
                            )}
                            {ticket.category === 'ACCESS' && (
                              <>
                                <div><span className="text-purple-400">Sistema:</span> {ticket.specific_metadata.target_system}</div>
                                <div><span className="text-purple-400">Aprobación:</span> {ticket.specific_metadata.approval_required ? 'Requerida' : 'Omitida'}</div>
                              </>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Transiciones de Estado (State Pattern Contextual Actions) */}
                      <div className="pt-2 border-t border-slate-700/60 flex flex-col gap-1.5">
                        <div className="flex items-center justify-between text-[10px] text-slate-400">
                          <span>Acciones permitidas (State):</span>
                          <button
                            onClick={() => onViewAudit(ticket)}
                            className="text-indigo-400 hover:text-indigo-300 font-semibold underline"
                          >
                            Trazabilidad
                          </button>
                        </div>

                        {/* Botones según el estado actual */}
                        <div className="grid grid-cols-1 gap-1">
                          {ticket.status === 'OPEN' && (
                            <button
                              disabled={actionLoadingId === ticket.id}
                              onClick={() => handleAction(ticket.id, 'IN_PROCESS', 'Ticket tomado en atención')}
                              className="w-full py-1.5 px-2.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-xs font-semibold transition active:scale-95 text-center"
                            >
                              Tomar en Proceso &rarr;
                            </button>
                          )}

                          {ticket.status === 'IN_PROCESS' && (
                            <div className="flex gap-1.5">
                              <button
                                disabled={actionLoadingId === ticket.id}
                                onClick={() => handleAction(ticket.id, 'RESOLVED', 'Incidencia resuelta')}
                                className="flex-1 py-1.5 px-2 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 text-xs font-semibold transition active:scale-95"
                              >
                                Resolver &rarr;
                              </button>
                              <button
                                disabled={actionLoadingId === ticket.id}
                                onClick={() => handleAction(ticket.id, 'OPEN', 'Devuelto a cola abierta')}
                                className="py-1.5 px-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-slate-300 text-xs font-medium transition"
                                title="Desasignar a Open"
                              >
                                &larr; Desasignar
                              </button>
                            </div>
                          )}

                          {ticket.status === 'RESOLVED' && (
                            <div className="flex gap-1.5">
                              <button
                                disabled={actionLoadingId === ticket.id}
                                onClick={() => handleAction(ticket.id, 'CLOSED', 'Cierre confirmado')}
                                className="flex-1 py-1.5 px-2 rounded-lg bg-slate-600/30 hover:bg-slate-600/50 text-slate-200 border border-slate-600/40 text-xs font-semibold transition active:scale-95"
                              >
                                Cerrar Ticket &check;
                              </button>
                              <button
                                disabled={actionLoadingId === ticket.id}
                                onClick={() => handleAction(ticket.id, 'IN_PROCESS', 'Reabierto por cliente')}
                                className="py-1.5 px-2 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-xs font-medium transition"
                                title="Reabrir a En Proceso"
                              >
                                &larr; Reabrir
                              </button>
                            </div>
                          )}

                          {ticket.status === 'CLOSED' && (
                            <button
                              disabled={actionLoadingId === ticket.id}
                              onClick={() => handleAction(ticket.id, 'OPEN', 'Reapertura formal de caso cerrado')}
                              className="w-full py-1.5 px-2.5 rounded-lg bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 text-xs font-medium transition text-center"
                            >
                              Reabrir a Abierto &#8634;
                            </button>
                          )}
                        </div>

                        {/* Botón eliminar */}
                        <div className="flex justify-end pt-1">
                          <button
                            onClick={() => onDeleteTicket(ticket.id)}
                            className="text-[10px] text-rose-400 hover:text-rose-300 hover:underline"
                          >
                            Eliminar ticket
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
