import React from 'react';

export default function Dashboard({ tickets, onSelectTicket, onOpenCreateModal }) {
  const total = tickets.length;
  const openCount = tickets.filter(t => t.status === 'OPEN').length;
  const inProcessCount = tickets.filter(t => t.status === 'IN_PROCESS').length;
  const resolvedCount = tickets.filter(t => t.status === 'RESOLVED').length;
  const closedCount = tickets.filter(t => t.status === 'CLOSED').length;

  const hardwareCount = tickets.filter(t => t.category === 'HARDWARE').length;
  const softwareCount = tickets.filter(t => t.category === 'SOFTWARE').length;
  const accessCount = tickets.filter(t => t.category === 'ACCESS').length;

  const criticalTickets = tickets.filter(t => t.priority === 'CRITICAL' && t.status !== 'CLOSED');

  return (
    <div className="space-y-6">
      {/* Banner Superior con Identidad Arquitectónica */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/60 to-slate-900 border border-indigo-500/20 p-6 md:p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Panel de Control de Servicios TI
            </h1>
            <p className="mt-1 text-sm text-slate-300 max-w-2xl">
              Monitoreo en tiempo real con arquitectura modular y orquestación basada en los 6 patrones GoF:
              <span className="text-indigo-400 font-semibold"> Factory Method</span>, 
              <span className="text-cyan-400 font-semibold"> Singleton</span>, 
              <span className="text-emerald-400 font-semibold"> Repository</span>, 
              <span className="text-amber-400 font-semibold"> Facade</span>, 
              <span className="text-rose-400 font-semibold"> State</span> y 
              <span className="text-purple-400 font-semibold"> Observer</span>.
            </p>
          </div>
          <button
            onClick={onOpenCreateModal}
            className="self-start md:self-auto px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition transform hover:-translate-y-0.5"
          >
            + Crear Incidencia
          </button>
        </div>
      </div>

      {/* KPI Cards por Estado del Ticket (State Pattern) */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-sm">
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Tickets</p>
          <p className="mt-2 text-3xl font-bold text-white">{total}</p>
          <div className="mt-2 text-xs text-indigo-400">100% inventario</div>
        </div>

        <div className="bg-slate-900/80 border border-sky-500/20 rounded-xl p-4 shadow-sm">
          <p className="text-xs font-medium text-sky-400 uppercase tracking-wider">Abiertos (Open)</p>
          <p className="mt-2 text-3xl font-bold text-sky-300">{openCount}</p>
          <div className="mt-2 text-xs text-slate-400">Esperando atención</div>
        </div>

        <div className="bg-slate-900/80 border border-amber-500/20 rounded-xl p-4 shadow-sm">
          <p className="text-xs font-medium text-amber-400 uppercase tracking-wider">En Proceso</p>
          <p className="mt-2 text-3xl font-bold text-amber-300">{inProcessCount}</p>
          <div className="mt-2 text-xs text-slate-400">En atención técnica</div>
        </div>

        <div className="bg-slate-900/80 border border-emerald-500/20 rounded-xl p-4 shadow-sm">
          <p className="text-xs font-medium text-emerald-400 uppercase tracking-wider">Resueltos</p>
          <p className="mt-2 text-3xl font-bold text-emerald-300">{resolvedCount}</p>
          <div className="mt-2 text-xs text-slate-400">Solución entregada</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-700/40 rounded-xl p-4 shadow-sm col-span-2 md:col-span-1">
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Cerrados</p>
          <p className="mt-2 text-3xl font-bold text-slate-300">{closedCount}</p>
          <div className="mt-2 text-xs text-slate-500">Ciclo completado</div>
        </div>
      </div>

      {/* Grid de Desglose por Fábricas y Casos Críticos */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Distribución por Fábrica (Factory Method) */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-4 flex items-center justify-between">
            <span>Fábricas de Ticket</span>
            <span className="text-xs font-normal text-slate-500">Factory Method</span>
          </h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span className="font-medium text-indigo-300">Hardware Ticket</span>
                <span>{hardwareCount} ({total > 0 ? Math.round((hardwareCount / total) * 100) : 0}%)</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${total > 0 ? (hardwareCount / total) * 100 : 0}%` }}
                />
              </div>
              <p className="text-[10px] text-slate-500 mt-0.5">Valida serial & tipo de periférico</p>
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span className="font-medium text-cyan-300">Software Ticket</span>
                <span>{softwareCount} ({total > 0 ? Math.round((softwareCount / total) * 100) : 0}%)</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-cyan-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${total > 0 ? (softwareCount / total) * 100 : 0}%` }}
                />
              </div>
              <p className="text-[10px] text-slate-500 mt-0.5">Valida aplicación & entorno OS</p>
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span className="font-medium text-purple-300">Access Ticket</span>
                <span>{accessCount} ({total > 0 ? Math.round((accessCount / total) * 100) : 0}%)</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${total > 0 ? (accessCount / total) * 100 : 0}%` }}
                />
              </div>
              <p className="text-[10px] text-slate-500 mt-0.5">Valida credenciales & aprobación estricta</p>
            </div>
          </div>
        </div>

        {/* Tickets con Prioridad Crítica */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 md:col-span-2">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-4 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
              Incidencias Críticas Activas
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 font-semibold border border-rose-500/20">
              {criticalTickets.length} activas
            </span>
          </h3>

          {criticalTickets.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-sm">
              <p>No hay tickets críticos pendientes en este momento.</p>
              <p className="text-xs text-slate-600 mt-1">El SLA operativo se encuentra dentro del rango óptimo.</p>
            </div>
          ) : (
            <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1">
              {criticalTickets.map(ticket => (
                <div
                  key={ticket.id}
                  onClick={() => onSelectTicket(ticket)}
                  className="p-3 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 hover:border-indigo-500/40 cursor-pointer transition flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono font-bold text-slate-400">#{ticket.id}</span>
                    <div>
                      <p className="text-sm font-medium text-white">{ticket.title}</p>
                      <p className="text-xs text-slate-400">{ticket.category} &bull; {ticket.status}</p>
                    </div>
                  </div>
                  <span className="text-xs px-2.5 py-1 rounded bg-rose-500/20 text-rose-300 font-bold border border-rose-500/30">
                    CRITICAL
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
