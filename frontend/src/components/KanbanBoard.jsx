import React, { useState } from 'react';

const COLUMNS = [
  { id: 'OPEN', title: 'Abiertos (Open)', bgHeader: 'from-sky-500/20 to-sky-600/10', border: 'border-sky-500/30', badge: 'bg-sky-500/20 text-sky-300' },
  { id: 'IN_PROCESS', title: 'En Proceso (In Process)', bgHeader: 'from-amber-500/20 to-amber-600/10', border: 'border-amber-500/30', badge: 'bg-amber-500/20 text-amber-300' },
  { id: 'RESOLVED', title: 'Resueltos (Resolved)', bgHeader: 'from-emerald-500/20 to-emerald-600/10', border: 'border-emerald-500/30', badge: 'bg-emerald-500/20 text-emerald-300' },
  { id: 'CLOSED', title: 'Cerrados (Closed)', bgHeader: 'from-slate-700/30 to-slate-800/10', border: 'border-slate-700/40', badge: 'bg-slate-700/40 text-slate-300' },
];

export default function KanbanBoard({
  tickets,
  currentUser,
  technicians = [],
  onTransitionStatus,
  onAssignTicket,
  onViewAudit,
  onDeleteTicket,
  isLoading,
}) {
  const [filterCategory, setFilterCategory] = useState('');
  const [filterScope, setFilterScope] = useState('ALL'); // 'ALL' | 'UNASSIGNED' | 'ASSIGNED_TO_ME'
  const [searchQuery, setSearchQuery] = useState('');
  const [actionLoadingId, setActionLoadingId] = useState(null);

  // Filtrado reactivo combinado
  const filteredTickets = tickets.filter(ticket => {
    const matchesCategory = filterCategory ? ticket.category === filterCategory : true;
    const matchesSearch = searchQuery
      ? ticket.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ticket.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ticket.id.toString().includes(searchQuery) ||
        (ticket.creator?.full_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (ticket.assignee?.full_name || '').toLowerCase().includes(searchQuery.toLowerCase())
      : true;

    let matchesScope = true;
    if (filterScope === 'UNASSIGNED') {
      matchesScope = !ticket.assigned_to_id && !ticket.assignee;
    } else if (filterScope === 'ASSIGNED_TO_ME') {
      matchesScope = ticket.assigned_to_id === currentUser?.id || ticket.assignee?.id === currentUser?.id;
    }

    return matchesCategory && matchesSearch && matchesScope;
  });

  const handleAction = async (ticketId, targetStatus, reason) => {
    try {
      setActionLoadingId(ticketId);
      await onTransitionStatus(ticketId, targetStatus, reason, currentUser?.id);
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleSelfAssign = async (ticketId) => {
    if (!currentUser) return;
    try {
      setActionLoadingId(ticketId);
      await onAssignTicket(ticketId, currentUser.id, `Ticket tomado por ${currentUser.full_name}`);
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleReassign = async (ticketId, newTechId) => {
    try {
      setActionLoadingId(ticketId);
      const parsedId = newTechId === '' ? null : parseInt(newTechId, 10);
      await onAssignTicket(ticketId, parsedId, 'Reasignación desde tablero Kanban');
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

  const unassignedCount = tickets.filter(t => !t.assigned_to_id && !t.assignee).length;
  const myAssignedCount = tickets.filter(t => t.assigned_to_id === currentUser?.id || t.assignee?.id === currentUser?.id).length;

  return (
    <div className="space-y-4">
      {/* Barra de Filtros, Triage y Búsqueda */}
      <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl flex flex-col lg:flex-row gap-3 items-center justify-between shadow-md">
        {/* Scope selector (Triage de TI) */}
        <div className="flex rounded-xl bg-slate-950 p-1 border border-slate-800 text-xs w-full lg:w-auto">
          <button
            onClick={() => setFilterScope('ALL')}
            className={`flex-1 lg:flex-initial px-3.5 py-1.5 rounded-lg transition font-medium ${
              filterScope === 'ALL'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Todos los Casos ({tickets.length})
          </button>
          <button
            onClick={() => setFilterScope('UNASSIGNED')}
            className={`flex-1 lg:flex-initial px-3.5 py-1.5 rounded-lg transition font-medium flex items-center justify-center gap-1.5 ${
              filterScope === 'UNASSIGNED'
                ? 'bg-amber-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <span>Cola Sin Asignar</span>
            {unassignedCount > 0 && (
              <span className="w-4 h-4 rounded-full bg-amber-400 text-slate-950 text-[10px] font-black flex items-center justify-center">
                {unassignedCount}
              </span>
            )}
          </button>
          <button
            onClick={() => setFilterScope('ASSIGNED_TO_ME')}
            className={`flex-1 lg:flex-initial px-3.5 py-1.5 rounded-lg transition font-medium ${
              filterScope === 'ASSIGNED_TO_ME'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Asignados a Mí ({myAssignedCount})
          </button>
        </div>

        {/* Búsqueda y categoría */}
        <div className="flex flex-col sm:flex-row items-center gap-3 w-full lg:w-auto">
          <div className="relative w-full sm:w-64">
            <input
              type="text"
              placeholder="Buscar por ID, solicitante o texto..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <label className="text-xs text-slate-400 font-medium whitespace-nowrap">Fábrica:</label>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Todas</option>
              <option value="HARDWARE">Hardware</option>
              <option value="SOFTWARE">Software</option>
              <option value="ACCESS">Acceso & Seguridad</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tablero Kanban (Columnas por Estado del patrón State) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {COLUMNS.map((col) => {
          const colTickets = filteredTickets.filter((t) => t.status === col.id);

          return (
            <div
              key={col.id}
              className={`bg-slate-900/60 border ${col.border} rounded-2xl flex flex-col min-h-[600px] shadow-lg overflow-hidden`}
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
                    <span>Sin tickets en esta columna</span>
                  </div>
                ) : (
                  colTickets.map((ticket) => {
                    const isAssignedToMe = ticket.assigned_to_id === currentUser?.id || ticket.assignee?.id === currentUser?.id;

                    return (
                      <div
                        key={ticket.id}
                        className={`bg-slate-800/90 border ${
                          isAssignedToMe ? 'border-indigo-500/60 ring-1 ring-indigo-500/20' : 'border-slate-700/80'
                        } rounded-xl p-3.5 shadow-md hover:border-slate-600 transition flex flex-col justify-between gap-3 group`}
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
                          <p className="mt-1 text-xs text-slate-300 line-clamp-2 leading-relaxed">
                            {ticket.description}
                          </p>

                          {/* Solicitante Info */}
                          <div className="mt-2.5 flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-700/50 pt-2">
                            <span className="text-slate-400 font-medium">
                              👤 {ticket.creator ? ticket.creator.full_name : 'Usuario anónimo'}
                            </span>
                            {ticket.creator?.department && (
                              <span className="text-[10px] text-slate-400 px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800">
                                {ticket.creator.department}
                              </span>
                            )}
                          </div>

                          {/* Técnico Asignado & Selector de Reasignación */}
                          <div className="mt-2 p-2 rounded-lg bg-slate-900/80 border border-slate-800 flex flex-col gap-1.5">
                            <div className="flex items-center justify-between text-[10px]">
                              <span className="text-slate-400 font-semibold">Especialista TI:</span>
                              {ticket.assignee ? (
                                <span className="font-bold text-emerald-400">
                                  {ticket.assignee.full_name} {isAssignedToMe && '(Tú)'}
                                </span>
                              ) : (
                                <span className="text-amber-400 font-bold flex items-center gap-1">
                                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                                  Sin asignar
                                </span>
                              )}
                            </div>

                            {/* Acciones de Asignación */}
                            <div className="flex items-center gap-1.5 pt-1">
                              {!ticket.assignee && (
                                <button
                                  disabled={actionLoadingId === ticket.id}
                                  onClick={() => handleSelfAssign(ticket.id)}
                                  className="px-2 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-[10px] font-bold transition flex-1 text-center"
                                >
                                  Tomar Ticket ✋
                                </button>
                              )}

                              <select
                                disabled={actionLoadingId === ticket.id}
                                value={ticket.assigned_to_id || ''}
                                onChange={(e) => handleReassign(ticket.id, e.target.value)}
                                className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-[10px] text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 flex-1"
                              >
                                <option value="">Reasignar...</option>
                                {technicians.map((tech) => (
                                  <option key={tech.id} value={tech.id}>
                                    {tech.full_name} ({tech.role})
                                  </option>
                                ))}
                              </select>
                            </div>
                          </div>
                        </div>

                        {/* Transiciones de Estado del State Pattern */}
                        <div className="pt-2 border-t border-slate-700/60 flex flex-col gap-1.5">
                          <div className="flex items-center justify-between text-[10px] text-slate-400">
                            <span>Transiciones de Estado:</span>
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
                                onClick={() => handleAction(ticket.id, 'IN_PROCESS', 'Ticket tomado en atención técnica')}
                                className="w-full py-1.5 px-2.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-xs font-semibold transition active:scale-95 text-center"
                              >
                                Tomar en Proceso &rarr;
                              </button>
                            )}

                            {ticket.status === 'IN_PROCESS' && (
                              <div className="flex gap-1.5">
                                <button
                                  disabled={actionLoadingId === ticket.id}
                                  onClick={() => handleAction(ticket.id, 'RESOLVED', 'Incidencia resuelta por el técnico')}
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
                                  onClick={() => handleAction(ticket.id, 'CLOSED', 'Cierre confirmado con usuario')}
                                  className="flex-1 py-1.5 px-2 rounded-lg bg-slate-600/30 hover:bg-slate-600/50 text-slate-200 border border-slate-600/40 text-xs font-semibold transition active:scale-95"
                                >
                                  Cerrar Caso &check;
                                </button>
                                <button
                                  disabled={actionLoadingId === ticket.id}
                                  onClick={() => handleAction(ticket.id, 'IN_PROCESS', 'Reabierto por verificación técnica')}
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
                                onClick={() => handleAction(ticket.id, 'OPEN', 'Reapertura formal de caso')}
                                className="w-full py-1.5 px-2.5 rounded-lg bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 text-xs font-medium transition text-center"
                              >
                                Reabrir a Abierto &#8634;
                              </button>
                            )}
                          </div>

                          {/* Eliminar ticket si es Admin */}
                          {currentUser?.role === 'ADMIN' && (
                            <div className="flex justify-end pt-1">
                              <button
                                onClick={() => onDeleteTicket(ticket.id)}
                                className="text-[10px] text-rose-400 hover:text-rose-300 hover:underline"
                              >
                                Eliminar ticket (Admin)
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
