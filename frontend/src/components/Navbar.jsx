import React from 'react';

export default function Navbar({
  activeTab,
  setActiveTab,
  currentUser,
  users,
  onSwitchUser,
  onOpenCreateModal,
  isOnline,
  onRefresh,
  onLogout,
}) {
  const getRoleBadge = (role) => {
    switch (role) {
      case 'ADMIN':
        return { label: 'ADMIN', color: 'bg-purple-500/20 text-purple-300 border-purple-500/30', icon: '🛡️' };
      case 'IT_STUDENT_SUPPORT':
        return { label: 'TI ESTUDIANTES', color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30', icon: '📚' };
      case 'IT_STAFF_SUPPORT':
        return { label: 'TI PERSONAL', color: 'bg-amber-500/20 text-amber-300 border-amber-500/30', icon: '🛠️' };
      case 'STUDENT':
        return { label: 'ESTUDIANTE', color: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30', icon: '🎓' };
      case 'STAFF':
        return { label: 'PERSONAL', color: 'bg-sky-500/20 text-sky-300 border-sky-500/30', icon: '🏫' };
      default:
        return { label: 'INVITADO', color: 'bg-slate-700', icon: '👤' };
    }
  };

  const roleInfo = currentUser ? getRoleBadge(currentUser.role) : { label: 'INVITADO', color: 'bg-slate-700', icon: '👤' };

  return (
    <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-3">
          {/* Brand */}
          <div className="flex items-center space-x-3 shrink-0">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 text-white font-black text-xl tracking-wider">
              US
            </div>
            <div>
              <span className="text-base sm:text-lg font-bold text-white tracking-tight">
                Unified Service Desk
              </span>
            </div>
          </div>

          {/* Navigation Links (Adaptativos al Rol) */}
          <nav className="flex items-center space-x-1 sm:space-x-2">
            {['STUDENT', 'STAFF'].includes(currentUser?.role) ? (
              <>
                <button
                  onClick={() => setActiveTab('user_portal')}
                  className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                    activeTab === 'user_portal'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  Mis Solicitudes
                </button>
                <button
                  onClick={() => setActiveTab('audit')}
                  className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                    activeTab === 'audit'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  Notificaciones
                </button>
              </>
            ) : ['IT_STUDENT_SUPPORT', 'IT_STAFF_SUPPORT'].includes(currentUser?.role) ? (
              <>
                <button
                  onClick={() => setActiveTab('kanban')}
                  className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                    activeTab === 'kanban'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  Tablero TI (Kanban)
                </button>
                <button
                  onClick={() => setActiveTab('dashboard')}
                  className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                    activeTab === 'dashboard'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  Métricas TI
                </button>
                <button
                  onClick={() => setActiveTab('audit')}
                  className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                    activeTab === 'audit'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  Auditoría & Eventos
                </button>
              </>
            ) : (
              // ADMIN
              <>
                <button
                  onClick={() => setActiveTab('kanban')}
                  className={`px-2.5 sm:px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                    activeTab === 'kanban'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  Kanban Global
                </button>
                <button
                  onClick={() => setActiveTab('admin_users')}
                  className={`px-2.5 sm:px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                    activeTab === 'admin_users'
                      ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  Usuarios & RBAC
                </button>
                <button
                  onClick={() => setActiveTab('dashboard')}
                  className={`px-2.5 sm:px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                    activeTab === 'dashboard'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  Métricas
                </button>
                <button
                  onClick={() => setActiveTab('audit')}
                  className={`px-2.5 sm:px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                    activeTab === 'audit'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  Auditoría
                </button>
              </>
            )}
          </nav>

          {/* Persona / Role Switcher & New Ticket Button */}
          <div className="flex items-center space-x-2 sm:space-x-3 shrink-0">
            {/* Selector de Usuario Activo / Persona */}
            <div className="flex items-center gap-1.5 bg-slate-800/80 border border-slate-700/80 rounded-xl px-2.5 py-1 text-xs">
              <span className="text-sm">{roleInfo.icon}</span>
              <div className="flex flex-col text-left">
                <span className="text-[10px] text-slate-400 font-semibold leading-tight">
                  Rol activo: <span className={`px-1 py-0.2 rounded font-bold ${roleInfo.color}`}>{roleInfo.label}</span>
                </span>
                <span className="text-white font-semibold text-xs truncate max-w-[120px]">
                  {currentUser?.full_name || 'Sin usuario'}
                </span>
              </div>
            </div>

            {/* Recargar */}
            <button
              onClick={onRefresh}
              title="Recargar datos"
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition hidden sm:inline-flex"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>

            {/* Botón Crear Ticket */}
            <button
              onClick={onOpenCreateModal}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700 text-white text-xs font-semibold shadow-md shadow-indigo-500/25 transition active:scale-95"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 4v16m8-8H4" />
              </svg>
              <span className="hidden sm:inline">Nuevo Ticket</span>
            </button>

            {/* Botón Cerrar Sesión */}
            {onLogout && (
              <button
                onClick={onLogout}
                title="Cerrar sesión"
                className="p-2 rounded-xl bg-rose-900/40 hover:bg-rose-800/60 text-rose-300 hover:text-white transition text-xs font-semibold"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
