import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import KanbanBoard from './components/KanbanBoard';
import TicketFormModal from './components/TicketFormModal';
import AuditLogModal from './components/AuditLogModal';
import { apiService } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('kanban'); // 'kanban' | 'dashboard' | 'audit'
  const [tickets, setTickets] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isOnline, setIsOnline] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [notificationToast, setNotificationToast] = useState(null);

  // Modales
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedTicketForAudit, setSelectedTicketForAudit] = useState(null);
  const [isAuditModalOpen, setIsAuditModalOpen] = useState(false);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const showToast = (message, type = 'info') => {
    setNotificationToast({ message, type });
    setTimeout(() => {
      setNotificationToast(null);
    }, 4000);
  };

  const fetchInitialData = async () => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      // 1. Health check
      const health = await apiService.checkHealth();
      setIsOnline(health.status === 'healthy');

      // 2. Load tickets
      const data = await apiService.getTickets();
      setTickets(data);
    } catch (err) {
      console.error('Error al conectar con la API:', err);
      setIsOnline(false);
      setErrorMessage(
        'No se pudo conectar con el servidor backend FastAPI. Asegúrate de que el backend esté ejecutándose en http://localhost:8000'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTicket = async (ticketPayload) => {
    try {
      const newTicket = await apiService.createTicket(ticketPayload);
      setTickets((prev) => [newTicket, ...prev]);
      showToast(`¡Ticket #${newTicket.id} creado exitosamente con ${newTicket.category} Factory!`, 'success');
    } catch (err) {
      throw err;
    }
  };

  const handleTransitionStatus = async (ticketId, targetStatus, reason) => {
    try {
      const updatedTicket = await apiService.updateTicketStatus(ticketId, targetStatus, reason);
      setTickets((prev) =>
        prev.map((t) => (t.id === ticketId ? updatedTicket : t))
      );
      showToast(
        `Ticket #${ticketId} transicionado a '${targetStatus}' (State Pattern & Observer actualizados)`,
        'success'
      );
    } catch (err) {
      showToast(`Transición rechazada: ${err.message}`, 'error');
    }
  };

  const handleDeleteTicket = async (ticketId) => {
    if (!window.confirm(`¿Estás seguro de eliminar el ticket #${ticketId}?`)) return;
    try {
      await apiService.deleteTicket(ticketId);
      setTickets((prev) => prev.filter((t) => t.id !== ticketId));
      showToast(`Ticket #${ticketId} eliminado`, 'info');
    } catch (err) {
      showToast(`Error al eliminar: ${err.message}`, 'error');
    }
  };

  const handleOpenAudit = (ticket) => {
    setSelectedTicketForAudit(ticket);
    setIsAuditModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Toast Notification */}
      {notificationToast && (
        <div className="fixed bottom-6 right-6 z-50 animate-bounce">
          <div
            className={`px-4 py-3 rounded-xl shadow-2xl text-xs font-semibold flex items-center gap-3 border ${
              notificationToast.type === 'error'
                ? 'bg-rose-950 border-rose-500/50 text-rose-200'
                : notificationToast.type === 'success'
                ? 'bg-emerald-950 border-emerald-500/50 text-emerald-200'
                : 'bg-indigo-950 border-indigo-500/50 text-indigo-200'
            }`}
          >
            <span>{notificationToast.message}</span>
          </div>
        </div>
      )}

      {/* Navbar Superior */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenCreateModal={() => setIsCreateModalOpen(true)}
        isOnline={isOnline}
        onRefresh={fetchInitialData}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {errorMessage && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm">Aviso:</span>
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={fetchInitialData}
              className="px-3 py-1 bg-rose-600/30 hover:bg-rose-600/50 rounded-lg text-rose-200 font-semibold"
            >
              Reintentar
            </button>
          </div>
        )}

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-24 text-slate-400">
            <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-sm font-medium">Cargando Unified Service Desk...</p>
          </div>
        ) : (
          <>
            {activeTab === 'kanban' && (
              <KanbanBoard
                tickets={tickets}
                onTransitionStatus={handleTransitionStatus}
                onViewAudit={handleOpenAudit}
                onDeleteTicket={handleDeleteTicket}
                isLoading={isLoading}
              />
            )}

            {activeTab === 'dashboard' && (
              <Dashboard
                tickets={tickets}
                onSelectTicket={handleOpenAudit}
                onOpenCreateModal={() => setIsCreateModalOpen(true)}
              />
            )}

            {activeTab === 'audit' && (
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                <div className="mb-4">
                  <h2 className="text-xl font-bold text-white">Centro de Auditoría & Notificaciones</h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Inspección centralizada de eventos del patrón Observer (`AuditLogObserver` y `EmailNotifierObserver`).
                  </p>
                </div>
                <button
                  onClick={() => {
                    setSelectedTicketForAudit(null);
                    setIsAuditModalOpen(true);
                  }}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                >
                  Abrir Registro Completo de Notificaciones
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {/* Footer Arquitectónico */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 py-4 text-center text-xs text-slate-500">
        <p>
          Unified Service Desk &bull; Diseñado con principios Clean Architecture &bull; Monolito Modular
        </p>
      </footer>

      {/* Modales */}
      <TicketFormModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onTicketCreated={handleCreateTicket}
      />

      <AuditLogModal
        ticket={selectedTicketForAudit}
        isOpen={isAuditModalOpen}
        onClose={() => {
          setIsAuditModalOpen(false);
          setSelectedTicketForAudit(null);
        }}
      />
    </div>
  );
}
