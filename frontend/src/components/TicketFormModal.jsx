import React, { useState } from 'react';

export default function TicketFormModal({ isOpen, onClose, onTicketCreated }) {
  const [category, setCategory] = useState('HARDWARE');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Metadatos específicos polimórficos (Factory Method)
  const [hardwareMeta, setHardwareMeta] = useState({ serial_number: '', device_type: '' });
  const [softwareMeta, setSoftwareMeta] = useState({ software_name: '', version: '', os_environment: '' });
  const [accessMeta, setAccessMeta] = useState({ target_system: '', system_role: '', user_account: '' });

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMessage('');

    let specific_metadata = {};
    if (category === 'HARDWARE') {
      specific_metadata = { ...hardwareMeta };
    } else if (category === 'SOFTWARE') {
      specific_metadata = { ...softwareMeta };
    } else if (category === 'ACCESS') {
      specific_metadata = { ...accessMeta };
    }

    const payload = {
      title,
      description,
      category,
      priority: priority || null,
      specific_metadata,
    };

    try {
      await onTicketCreated(payload);
      onClose();
      // Limpiar formulario
      setTitle('');
      setDescription('');
      setPriority('');
      setHardwareMeta({ serial_number: '', device_type: '' });
      setSoftwareMeta({ software_name: '', version: '', os_environment: '' });
      setAccessMeta({ target_system: '', system_role: '', user_account: '' });
    } catch (err) {
      setErrorMessage(err.message || 'Error al crear el ticket');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-850">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <span>Nuevo Ticket de Servicio</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                Factory Method
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Instanciación polimórfica según la fábrica de categoría seleccionada.
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

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4 overflow-y-auto flex-1">
          {errorMessage && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-2">
              <span className="font-bold text-sm">&times;</span>
              <div>{errorMessage}</div>
            </div>
          )}

          {/* Selector de Fábrica (Categoría) */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Seleccionar Fábrica de Ticket (Categoría)
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'HARDWARE', label: 'Hardware', desc: 'HardwareTicketFactory', color: 'indigo' },
                { id: 'SOFTWARE', label: 'Software', desc: 'SoftwareTicketFactory', color: 'cyan' },
                { id: 'ACCESS', label: 'Acceso / Seguridad', desc: 'AccessTicketFactory', color: 'purple' },
              ].map((cat) => (
                <button
                  type="button"
                  key={cat.id}
                  onClick={() => setCategory(cat.id)}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    category === cat.id
                      ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-md'
                      : 'bg-slate-800/60 border-slate-700/60 text-slate-400 hover:bg-slate-800'
                  }`}
                >
                  <p className="text-xs font-bold text-white">{cat.label}</p>
                  <p className="text-[10px] text-slate-400 mt-1 font-mono">{cat.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Campos Generales */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Título de la Incidencia *</label>
            <input
              type="text"
              required
              minLength={3}
              placeholder="Ej: Teclado no responde tras actualización"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Descripción Detallada *</label>
            <textarea
              required
              minLength={5}
              rows={3}
              placeholder="Detalle paso a paso del fallo presentado..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Prioridad Explícita <span className="text-slate-500">(Opcional)</span>
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Por defecto de fábrica</option>
                <option value="LOW">Baja (LOW)</option>
                <option value="MEDIUM">Media (MEDIUM)</option>
                <option value="HIGH">Alta (HIGH)</option>
                <option value="CRITICAL">Crítica (CRITICAL)</option>
              </select>
              <p className="text-[10px] text-slate-500 mt-1">
                {category === 'HARDWARE' && 'Por defecto: HIGH'}
                {category === 'SOFTWARE' && 'Por defecto: MEDIUM'}
                {category === 'ACCESS' && 'Por defecto: CRITICAL'}
              </p>
            </div>
          </div>

          {/* Metadatos Específicos Exigidos por la Fábrica Polimórfica */}
          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 space-y-3">
            <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center justify-between">
              <span>Invariantes de {category} Factory</span>
              <span className="text-[10px] font-normal text-slate-400">Validado en Backend</span>
            </h4>

            {category === 'HARDWARE' && (
              <div className="space-y-2">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Número de Serie (S/N) *</label>
                  <input
                    type="text"
                    required
                    placeholder="Ej: SN-DELL-883921"
                    value={hardwareMeta.serial_number}
                    onChange={(e) => setHardwareMeta({ ...hardwareMeta, serial_number: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Tipo de Dispositivo *</label>
                  <input
                    type="text"
                    required
                    placeholder="Ej: Monitor, Teclado, Laptop ThinkPad"
                    value={hardwareMeta.device_type}
                    onChange={(e) => setHardwareMeta({ ...hardwareMeta, device_type: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <p className="text-[10px] text-indigo-400">&bull; La fábrica marcará automáticamente garantía requerida.</p>
              </div>
            )}

            {category === 'SOFTWARE' && (
              <div className="space-y-2">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Nombre del Software / Aplicación *</label>
                  <input
                    type="text"
                    required
                    placeholder="Ej: PostgreSQL, Docker, Excel, VPN"
                    value={softwareMeta.software_name}
                    onChange={(e) => setSoftwareMeta({ ...softwareMeta, software_name: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs text-slate-300 mb-1">Versión</label>
                    <input
                      type="text"
                      placeholder="Ej: 16.2 / v2.4.0"
                      value={softwareMeta.version}
                      onChange={(e) => setSoftwareMeta({ ...softwareMeta, version: e.target.value })}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-300 mb-1">Sistema Operativo</label>
                    <input
                      type="text"
                      placeholder="Ej: Windows 11 / Ubuntu"
                      value={softwareMeta.os_environment}
                      onChange={(e) => setSoftwareMeta({ ...softwareMeta, os_environment: e.target.value })}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>
              </div>
            )}

            {category === 'ACCESS' && (
              <div className="space-y-2">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Sistema Destino / Recurso *</label>
                  <input
                    type="text"
                    required
                    placeholder="Ej: Producción AWS, ERP SAP, Active Directory"
                    value={accessMeta.target_system}
                    onChange={(e) => setAccessMeta({ ...accessMeta, target_system: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs text-slate-300 mb-1">Rol Solicitado *</label>
                    <input
                      type="text"
                      required
                      placeholder="Ej: ReadOnly, Admin, DBA"
                      value={accessMeta.system_role}
                      onChange={(e) => setAccessMeta({ ...accessMeta, system_role: e.target.value })}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-300 mb-1">Cuenta de Usuario</label>
                    <input
                      type="text"
                      placeholder="Ej: jdoe@company.com"
                      value={accessMeta.user_account}
                      onChange={(e) => setAccessMeta({ ...accessMeta, user_account: e.target.value })}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>
                <p className="text-[10px] text-purple-400">&bull; Por seguridad, se exigirá aprobación previa antes del alta.</p>
              </div>
            )}
          </div>

          {/* Modal Footer */}
          <div className="pt-2 border-t border-slate-800 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
            >
              {isSubmitting ? 'Instanciando con Factory...' : 'Crear Ticket'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
