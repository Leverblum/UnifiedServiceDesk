import React, { useState } from 'react';

export default function LoginModal({ isOpen, users = [], onLogin, onClose }) {
  const [selectedEmail, setSelectedEmail] = useState('');
  const [customEmail, setCustomEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  if (!isOpen) return null;

  const handleSelectQuickUser = async (email) => {
    setIsSubmitting(true);
    setErrorMessage('');
    try {
      await onLogin(email);
      onClose();
    } catch (err) {
      setErrorMessage(err.message || 'Error al iniciar sesión');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCustomLogin = async (e) => {
    e.preventDefault();
    if (!customEmail) return;
    setIsSubmitting(true);
    setErrorMessage('');
    try {
      await onLogin(customEmail);
      onClose();
    } catch (err) {
      setErrorMessage(err.message || 'Error al iniciar sesión');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getRoleBadge = (role) => {
    switch (role) {
      case 'ADMIN':
        return { label: 'Administrador General', color: 'bg-purple-500/20 text-purple-300 border-purple-500/30', icon: '🛡️' };
      case 'STUDENT':
        return { label: 'Estudiante', color: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30', icon: '🎓' };
      case 'STAFF':
        return { label: 'Personal / Docente', color: 'bg-sky-500/20 text-sky-300 border-sky-500/30', icon: '🏫' };
      case 'IT_STUDENT_SUPPORT':
        return { label: 'TI Soporte Estudiantes', color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30', icon: '📚' };
      case 'IT_STAFF_SUPPORT':
        return { label: 'TI Soporte Personal & Campus', color: 'bg-amber-500/20 text-amber-300 border-amber-500/30', icon: '🛠️' };
      default:
        return { label: role, color: 'bg-slate-700 text-slate-300 border-slate-600', icon: '👤' };
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700 rounded-3xl w-full max-w-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 bg-gradient-to-r from-slate-900 via-indigo-950/80 to-slate-900 border-b border-slate-800 text-center relative">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/30 text-white font-black text-2xl mb-3">
            US
          </div>
          <h2 className="text-xl font-extrabold text-white tracking-tight">
            Mesa de Ayuda Universitaria
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
            Portal institucional unificado para trámites estudiantiles, soporte a personal y gestión tecnológica.
          </p>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5">
          {errorMessage && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <span className="font-bold">&times;</span>
              <span>{errorMessage}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
              Ingreso Rápido con Usuarios de Prueba (MVP)
            </label>
            <p className="text-[11px] text-slate-400 mb-3">
              Selecciona uno de los 5 roles preconfigurados para explorar su vista especializada:
            </p>

            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              {users.map((u) => {
                const badge = getRoleBadge(u.role);
                return (
                  <button
                    key={u.id}
                    disabled={isSubmitting}
                    onClick={() => handleSelectQuickUser(u.email)}
                    className="w-full p-3 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700/80 hover:border-indigo-500/60 transition text-left flex items-center justify-between group cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <div className="text-xl">{badge.icon}</div>
                      <div>
                        <p className="text-xs font-bold text-white group-hover:text-indigo-300 transition-colors">
                          {u.full_name}
                        </p>
                        <p className="text-[10px] text-slate-400 font-mono">{u.email}</p>
                        <p className="text-[10px] text-slate-400">{u.department}</p>
                      </div>
                    </div>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border whitespace-nowrap ${badge.color}`}>
                      {badge.label}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="relative border-t border-slate-800 pt-4">
            <span className="absolute -top-2.5 left-1/2 -translate-x-1/2 bg-slate-900 px-3 text-[10px] uppercase font-bold text-slate-500 tracking-wider">
              O ingresar con correo
            </span>
            <form onSubmit={handleCustomLogin} className="flex gap-2">
              <input
                type="email"
                required
                placeholder="ejemplo@universidad.edu.co"
                value={customEmail}
                onChange={(e) => setCustomEmail(e.target.value)}
                className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-md transition disabled:opacity-50"
              >
                {isSubmitting ? 'Iniciando...' : 'Entrar'}
              </button>
            </form>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-950/60 border-t border-slate-800 flex justify-center">
          <p className="text-[11px] text-slate-500">
            Unified Service Desk &bull; Plataforma Universitaria Institucional
          </p>
        </div>
      </div>
    </div>
  );
}

