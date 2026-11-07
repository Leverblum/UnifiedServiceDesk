import React, { useState } from 'react';

export default function AdminPanel({
  users,
  tickets,
  onCreateUser,
  onOpenCreateTicketModal,
}) {
  const [activeSubTab, setActiveSubTab] = useState('users'); // 'users' | 'analytics'
  const [newFullName, setNewFullName] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newRole, setNewRole] = useState('STUDENT');
  const [newDepartment, setNewDepartment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const handleCreateUserSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setFeedback(null);
    try {
      await onCreateUser({
        full_name: newFullName,
        email: newEmail,
        role: newRole,
        department: newDepartment || null,
      });
      setFeedback({ type: 'success', text: `Usuario ${newFullName} registrado exitosamente.` });
      setNewFullName('');
      setNewEmail('');
      setNewDepartment('');
      setNewRole('STUDENT');
    } catch (err) {
      setFeedback({ type: 'error', text: err.message || 'Error al crear usuario' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const getRoleBadge = (role) => {
    switch (role) {
      case 'ADMIN':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      case 'IT_STUDENT_SUPPORT':
      case 'IT_STAFF_SUPPORT':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
      case 'STUDENT':
      case 'STAFF':
      default:
        return 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* Banner de Administración */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-purple-950/50 to-slate-900 border border-purple-500/20 p-6 md:p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold mb-2">
              <span>🛡️ Panel de Administración Global</span>
              <span>&bull;</span>
              <span>Control de Acceso Basado en Roles (RBAC)</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Gestión de Usuarios & Control Corporativo
            </h1>
            <p className="mt-1 text-sm text-slate-300 max-w-2xl">
              Administración centralizada de cuentas de usuario, asignación de roles jerárquicos (Solicitantes, Especialistas TI, Administradores) y supervisión global del Service Desk.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onOpenCreateTicketModal}
              className="px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-lg shadow-purple-600/30 transition"
            >
              + Nuevo Ticket Admin
            </button>
          </div>
        </div>
      </div>

      {/* Selector de Sub-pestañas */}
      <div className="flex border-b border-slate-800 gap-4">
        <button
          onClick={() => setActiveSubTab('users')}
          className={`pb-3 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${
            activeSubTab === 'users'
              ? 'border-purple-500 text-purple-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>👥 Directorio de Usuarios ({users.length})</span>
        </button>
        <button
          onClick={() => setActiveSubTab('analytics')}
          className={`pb-3 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${
            activeSubTab === 'analytics'
              ? 'border-purple-500 text-purple-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>📊 Métricas de Roles & Carga</span>
        </button>
      </div>

      {activeSubTab === 'users' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Formulario de Registro de Nuevo Usuario */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg flex flex-col justify-between">
            <div>
              <h3 className="text-base font-bold text-white mb-1">Registrar Nuevo Usuario</h3>
              <p className="text-xs text-slate-400 mb-4">
                Agrega un nuevo colaborador y define sus privilegios en el sistema.
              </p>

              {feedback && (
                <div
                  className={`p-3 rounded-xl mb-4 text-xs border ${
                    feedback.type === 'error'
                      ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                      : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  }`}
                >
                  {feedback.text}
                </div>
              )}

              <form onSubmit={handleCreateUserSubmit} className="space-y-3.5">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Nombre Completo *</label>
                  <input
                    type="text"
                    required
                    placeholder="Ej: Sofía Herrera"
                    value={newFullName}
                    onChange={(e) => setNewFullName(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Correo Electrónico *</label>
                  <input
                    type="email"
                    required
                    placeholder="Ej: sofia.herrera@empresa.com"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Departamento / Área</label>
                  <input
                    type="text"
                    placeholder="Ej: Operaciones, Ventas, TI"
                    value={newDepartment}
                    onChange={(e) => setNewDepartment(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Rol en el Sistema (RBAC) *</label>
                  <select
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="STUDENT">STUDENT (Estudiante)</option>
                    <option value="STAFF">STAFF (Personal / Docente)</option>
                    <option value="IT_STUDENT_SUPPORT">IT_STUDENT_SUPPORT (Soporte a estudiantes)</option>
                    <option value="IT_STAFF_SUPPORT">IT_STAFF_SUPPORT (Soporte a personal)</option>
                    <option value="ADMIN">ADMIN (Administrador TI)</option>
                  </select>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-lg shadow-purple-600/30 transition disabled:opacity-50"
                >
                  {isSubmitting ? 'Guardando...' : 'Crear Usuario'}
                </button>
              </form>
            </div>
          </div>

          {/* Tabla de Directorio de Usuarios */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg lg:col-span-2 overflow-x-auto">
            <h3 className="text-base font-bold text-white mb-1">Usuarios Registrados en el Sistema</h3>
            <p className="text-xs text-slate-400 mb-4">
              Directorio con estadísticas de tickets creados y tickets asignados.
            </p>

            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Usuario</th>
                  <th className="py-2.5 px-3">Departamento</th>
                  <th className="py-2.5 px-3">Rol RBAC</th>
                  <th className="py-2.5 px-3 text-center">Tickets Creados</th>
                  <th className="py-2.5 px-3 text-center">Tickets Asignados</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {users.map((u) => {
                  const createdCount = tickets.filter(
                    (t) => t.created_by_id === u.id || t.creator?.id === u.id
                  ).length;
                  const assignedCount = tickets.filter(
                    (t) => t.assigned_to_id === u.id || t.assignee?.id === u.id
                  ).length;

                  return (
                    <tr key={u.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3 px-3">
                        <p className="font-semibold text-white">{u.full_name}</p>
                        <p className="text-[10px] text-slate-400 font-mono">{u.email}</p>
                      </td>
                      <td className="py-3 px-3 text-slate-300">
                        {u.department || 'Sin área asignada'}
                      </td>
                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getRoleBadge(u.role)}`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-center font-mono font-bold text-indigo-300">
                        {createdCount}
                      </td>
                      <td className="py-3 px-3 text-center font-mono font-bold text-emerald-300">
                        {u.role === 'STUDENT' || u.role === 'STAFF' ? '-' : assignedCount}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeSubTab === 'analytics' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
              Distribución de Personal por Rol
            </h4>
            <div className="space-y-3 mt-4 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-indigo-300">Usuarios Solicitantes (USER):</span>
                <span className="font-bold text-white font-mono">
                  {users.filter(u => u.role === 'STUDENT' || u.role === 'STAFF').length}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-emerald-300">Especialistas TI (IT_SUPPORT):</span>
                <span className="font-bold text-white font-mono">
                  {users.filter(u => u.role === 'IT_STUDENT_SUPPORT' || u.role === 'IT_STAFF_SUPPORT').length}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-purple-300">Administradores (ADMIN):</span>
                <span className="font-bold text-white font-mono">
                  {users.filter(u => u.role === 'ADMIN').length}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 md:col-span-2">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
              Carga Operativa de Técnicos de Soporte
            </h4>
            <div className="space-y-3 mt-3">
              {users.filter(u => u.role === 'IT_STUDENT_SUPPORT' || u.role === 'IT_STAFF_SUPPORT' || u.role === 'ADMIN').map(tech => {
                const assigned = tickets.filter(t => t.assigned_to_id === tech.id || t.assignee?.id === tech.id).length;
                const inProgress = tickets.filter(t => (t.assigned_to_id === tech.id || t.assignee?.id === tech.id) && t.status === 'IN_PROCESS').length;

                return (
                  <div key={tech.id} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between text-xs">
                    <div>
                      <p className="font-semibold text-white">{tech.full_name} <span className="text-slate-500">({tech.role})</span></p>
                      <p className="text-[11px] text-slate-400">{tech.department}</p>
                    </div>
                    <div className="flex items-center gap-4 text-right">
                      <div>
                        <p className="text-[10px] text-slate-400">Total asignados</p>
                        <p className="font-mono font-bold text-indigo-400">{assigned}</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-slate-400">En proceso</p>
                        <p className="font-mono font-bold text-amber-400">{inProgress}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
