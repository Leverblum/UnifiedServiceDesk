import React, { useState } from 'react';

export default function UserPortal({
  currentUser,
  tickets,
  onOpenCreateModal,
  onViewAudit,
  onReopenTicket,
}) {
  const [filterState, setFilterState] = useState('ALL'); // 'ALL' | 'ACTIVE' | 'RESOLVED'

  // Filtrar exclusivamente los tickets del usuario activo
  const myTickets = tickets.filter(
    (t) => t.created_by_id === currentUser.id || t.creator?.id === currentUser.id
  );

  const activeTickets = myTickets.filter(
    (t) => t.status === 'OPEN' || t.status === 'IN_PROCESS'
  );
  const resolvedTickets = myTickets.filter(
    (t) => t.status === 'RESOLVED' || t.status === 'CLOSED'
  );

  const displayedTickets =
    filterState === 'ACTIVE'
      ? activeTickets
      : filterState === 'RESOLVED'
      ? resolvedTickets
      : myTickets;

  const getStatusBadge = (status) => {
    switch (status) {
      case 'OPEN':
        return {
          label: 'Abierto (En Espera)',
          classes: 'bg-sky-500/20 text-sky-300 border-sky-500/30',
          dot: 'bg-sky-400',
        };
      case 'IN_PROCESS':
        return {
          label: 'En Atención Técnica',
          classes: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
          dot: 'bg-amber-400 animate-pulse',
        };
      case 'RESOLVED':
        return {
          label: 'Solución Entregada',
          classes: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
          dot: 'bg-emerald-400',
        };
      case 'CLOSED':
        return {
          label: 'Caso Cerrado',
          classes: 'bg-slate-700/40 text-slate-400 border-slate-600/40',
          dot: 'bg-slate-500',
        };
      default:
        return {
          label: status,
          classes: 'bg-slate-700 text-slate-300 border-slate-600',
          dot: 'bg-slate-400',
        };
    }
  };

  return (
    <div className="space-y-6">
      {/* Banner de Bienvenida del Portal de Usuario */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/70 to-slate-900 border border-indigo-500/20 p-6 sm:p-8 shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold mb-2">
              <span>👤 Portal de Solicitante TI</span>
              <span>&bull;</span>
              <span>{currentUser.department || 'Colaborador'}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Bienvenido/a, {currentUser.full_name}
            </h1>
            <p className="mt-1 text-sm text-slate-300 max-w-2xl">
              Desde este portal puedes registrar nuevos requerimientos de TI, consultar el estado en tiempo real de tus incidencias y ver qué especialista técnico está asignado a tu caso.
            </p>
          </div>

          <button
            onClick={onOpenCreateModal}
            className="self-start md:self-auto inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700 text-white font-semibold text-sm shadow-lg shadow-indigo-500/30 transition transform hover:-translate-y-0.5 active:scale-95"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 4v16m8-8H4" />
            </svg>
            <span>Crear Solicitud de Soporte</span>
          </button>
        </div>
      </div>

      {/* Resumen de Métricas Personales */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Mis Solicitudes Totales</p>
            <p className="mt-1 text-2xl font-bold text-white">{myTickets.length}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 text-lg font-bold">
            📋
          </div>
        </div>

        <div className="bg-slate-900/80 border border-amber-500/20 rounded-xl p-4 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-amber-400 uppercase tracking-wider">En Atención Activa</p>
            <p className="mt-1 text-2xl font-bold text-amber-300">{activeTickets.length}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 text-lg font-bold">
            ⏳
          </div>
        </div>

        <div className="bg-slate-900/80 border border-emerald-500/20 rounded-xl p-4 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-emerald-400 uppercase tracking-wider">Solucionados / Cerrados</p>
            <p className="mt-1 text-2xl font-bold text-emerald-300">{resolvedTickets.length}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 text-lg font-bold">
            ✅
          </div>
        </div>
      </div>

      {/* Barra de Filtros de Mis Tickets */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <h2 className="text-base font-bold text-white">Mis Requerimientos</h2>
          <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
            {displayedTickets.length}
          </span>
        </div>

        <div className="flex rounded-lg bg-slate-900 p-1 border border-slate-800 text-xs">
          <button
            onClick={() => setFilterState('ALL')}
            className={`px-3 py-1 rounded-md transition ${
              filterState === 'ALL'
                ? 'bg-indigo-600 text-white font-semibold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Todos ({myTickets.length})
          </button>
          <button
            onClick={() => setFilterState('ACTIVE')}
            className={`px-3 py-1 rounded-md transition ${
              filterState === 'ACTIVE'
                ? 'bg-indigo-600 text-white font-semibold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Activos ({activeTickets.length})
          </button>
          <button
            onClick={() => setFilterState('RESOLVED')}
            className={`px-3 py-1 rounded-md transition ${
              filterState === 'RESOLVED'
                ? 'bg-indigo-600 text-white font-semibold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Resueltos ({resolvedTickets.length})
          </button>
        </div>
      </div>

      {/* Lista de Tickets del Solicitante */}
      {displayedTickets.length === 0 ? (
        <div className="bg-slate-900/60 border border-dashed border-slate-800 rounded-2xl p-12 text-center">
          <div className="w-16 h-16 mx-auto rounded-full bg-slate-800/80 flex items-center justify-center text-2xl mb-3 text-slate-500">
            📨
          </div>
          <h3 className="text-base font-semibold text-white">No tienes solicitudes en esta sección</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            {filterState === 'ACTIVE'
              ? 'Todos tus casos han sido atendidos o resueltos satisfactoriamente.'
              : '¿Tienes alguna incidencia de hardware, software o acceso a un sistema? Crea tu ticket con un solo clic.'}
          </p>
          <button
            onClick={onOpenCreateModal}
            className="mt-4 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
          >
            + Registrar Incidencia
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {displayedTickets.map((ticket) => {
            const statusInfo = getStatusBadge(ticket.status);

            return (
              <div
                key={ticket.id}
                className="bg-slate-900/80 border border-slate-800 hover:border-slate-700/80 rounded-2xl p-5 shadow-lg transition flex flex-col justify-between gap-4"
              >
                <div>
                  {/* Top Bar: ID + Status + Category */}
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-mono font-bold text-slate-400">
                      Ticket #{ticket.id}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                        {ticket.category}
                      </span>
                      <span
                        className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full border ${statusInfo.classes}`}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${statusInfo.dot}`} />
                        {statusInfo.label}
                      </span>
                    </div>
                  </div>

                  {/* Title & Description */}
                  <h3 className="text-base font-bold text-white tracking-tight">
                    {ticket.title}
                  </h3>
                  <p className="mt-1 text-xs text-slate-300 leading-relaxed">
                    {ticket.description}
                  </p>

                  {/* Specific Metadata info */}
                  {ticket.specific_metadata && Object.keys(ticket.specific_metadata).length > 0 && (
                    <div className="mt-3 p-2.5 rounded-xl bg-slate-950/60 border border-slate-800 text-[11px] text-slate-400 font-mono space-y-0.5">
                      {ticket.category === 'HARDWARE' && (
                        <div>
                          <span className="text-indigo-400">S/N:</span> {ticket.specific_metadata.serial_number || 'N/A'} &bull; Dispositivo: {ticket.specific_metadata.device_type || 'N/A'}
                        </div>
                      )}
                      {ticket.category === 'SOFTWARE' && (
                        <div>
                          <span className="text-cyan-400">Software:</span> {ticket.specific_metadata.software_name} (v{ticket.specific_metadata.version || 'General'})
                        </div>
                      )}
                      {ticket.category === 'ACCESS' && (
                        <div>
                          <span className="text-purple-400">Sistema:</span> {ticket.specific_metadata.target_system} &bull; Rol: {ticket.specific_metadata.system_role || 'General'}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Bottom Bar: Assigned Technician & Actions */}
                <div className="pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  {/* Técnico Asignado */}
                  <div className="flex items-center gap-2">
                    {ticket.assignee ? (
                      <div className="flex items-center gap-2 text-xs">
                        <div className="w-7 h-7 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-bold text-[10px]">
                          🛠️
                        </div>
                        <div>
                          <p className="text-white font-medium">{ticket.assignee.full_name}</p>
                          <p className="text-[10px] text-slate-400">{ticket.assignee.department || 'Soporte TI'}</p>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1.5 text-xs text-amber-400/90">
                        <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                        <span className="text-[11px] font-medium">Esperando asignación de especialista TI</span>
                      </div>
                    )}
                  </div>

                  {/* Actions for End User */}
                  <div className="flex items-center gap-2 self-end sm:self-auto">
                    <button
                      onClick={() => onViewAudit(ticket)}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-semibold transition"
                    >
                      Ver Trazabilidad
                    </button>

                    {/* Si está resuelto o cerrado, el usuario solicitante puede solicitar reapertura */}
                    {(ticket.status === 'RESOLVED' || ticket.status === 'CLOSED') && (
                      <button
                        onClick={() => onReopenTicket(ticket.id)}
                        className="px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 text-xs font-semibold transition"
                        title="Reabrir si el problema persiste"
                      >
                        Reabrir Caso &#8634;
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

