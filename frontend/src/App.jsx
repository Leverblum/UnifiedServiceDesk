import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import LoginModal from './components/LoginModal';
import Dashboard from './components/Dashboard';
import KanbanBoard from './components/KanbanBoard';
import UserPortal from './components/UserPortal';
import AdminPanel from './components/AdminPanel';
import TicketFormModal from './components/TicketFormModal';
import AuditLogModal from './components/AuditLogModal';
import { apiService } from './services/api';

export default function App() {
  const [users, setUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('user_portal');
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
    // Check localStorage for stored session
    const storedEmail = localStorage.getItem('currentUserEmail');
    if (storedEmail) {
      // Try to restore session
      apiService.login(storedEmail).then((user) => {
        setCurrentUser(user);
        setIsLoginModalOpen(false);
        setActiveTabForRole(user.role);
      }).catch(() => {
        localStorage.removeItem('currentUserEmail');
      });
    }
    fetchInitialData();
  }, []);

  const showToast = (message, type = 'info') => {
    setNotificationToast({ message, type });
    setTimeout(() => {
      setNotificationToast(null);
    }, 4500);
  };

  const setActiveTabForRole = (role) => {
    if (['STUDENT', 'STAFF'].includes(role)) {
      setActiveTab('user_portal');
    } else if (['IT_STUDENT_SUPPORT', 'IT_STAFF_SUPPORT'].includes(role)) {
      setActiveTab('kanban');
    } else if (role === 'ADMIN') {
      setActiveTab('kanban');
    }
  };

  const handleLogin = async (email) => {
    try {
      const user = await apiService.login(email);
      setCurrentUser(user);
      setIsLoginModalOpen(false);
      localStorage.setItem('currentUserEmail', user.email);
      setActiveTabForRole(user.role);
      showToast(`Bienvenido/a ${user.full_name}`, 'success');
    } catch (err) {
      throw err;
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('currentUserEmail');
    setIsLoginModalOpen(true);
    setActiveTab('user_portal');
    showToast('Sesión cerrada', 'info');
  };

  const fetchInitialData = async () => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      // 1. Health check
      const health = await apiService.checkHealth();
      setIsOnline(health.status === 'healthy');

      // 2. Cargar usuarios del sistema (o sembrar si está vacío)
      let loadedUsers = await apiService.getUsers();
      if (!loadedUsers || loadedUsers.length === 0) {
        loadedUsers = await apiService.seedUsers();
      }
      setUsers(loadedUsers);

      // 3. Cargar tickets
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

  const handleSwitchUser = (userId) => {
    const selected = users.find((u) => u.id === userId);
    if (!selected) return;

    setCurrentUser(selected);
    localStorage.setItem('currentUserEmail', selected.email);
    setActiveTabForRole(selected.role);

    const roleLabels = {
      STUDENT: 'Estudiante',
      STAFF: 'Personal Universitario',
      IT_STUDENT_SUPPORT: 'Soporte TI Estudiantes',
      IT_STAFF_SUPPORT: 'Soporte TI Personal',
      ADMIN: 'Administrador',
    };
    showToast(`Cambiado a: ${selected.full_name} (${roleLabels[selected.role] || selected.role})`, 'info');
  };

  const handleCreateTicket = async (ticketPayload) => {
    try {
      const newTicket = await apiService.createTicket(ticketPayload);
      setTickets((prev) => [newTicket, ...prev]);
      showToast(
        `¡Ticket #${newTicket.id} registrado exitosamente!`,
        'success'
      );
    } catch (err) {
      throw err;
    }
  };

  const handleAssignTicket = async (ticketId, assignedToId, reason) => {
    try {
      const updated = await apiService.assignTicket(
        ticketId,
        assignedToId,
        reason,
        currentUser?.id
      );
      setTickets((prev) => prev.map((t) => (t.id === ticketId ? updated : t)));
      showToast(
        `Ticket #${ticketId} ${assignedToId ? 'asignado a técnico' : 'desasignado'} correctamente.`,
        'success'
      );
    } catch (err) {
      showToast(`Error al asignar ticket: ${err.message}`, 'error');
    }
  };

  const handleTransitionStatus = async (ticketId, targetStatus, reason, userId) => {
    try {
      const updatedTicket = await apiService.updateTicketStatus(
        ticketId,
        targetStatus,
        reason,
        userId || currentUser?.id
      );
      setTickets((prev) =>
        prev.map((t) => (t.id === ticketId ? updatedTicket : t))
      );
      showToast(
        `Ticket #${ticketId} transicionado a '${targetStatus}'`,
        'success'
      );
    } catch (err) {
      showToast(`Transición rechazada: ${err.message}`, 'error');
    }
  };

  const handleReopenTicket = async (ticketId) => {
    try {
      const updatedTicket = await apiService.updateTicketStatus(
        ticketId,
        'OPEN',
        'Reapertura solicitada por el usuario',
        currentUser?.id
      );
      setTickets((prev) =>
        prev.map((t) => (t.id === ticketId ? updatedTicket : t))
      );
      showToast(`Ticket #${ticketId} reabierto exitosamente.`, 'success');
    } catch (err) {
      showToast(`Error al reabrir ticket: ${err.message}`, 'error');
    }
  };

  const handleCreateUser = async (userData) => {
    try {
      const newUser = await apiService.createUser(userData);
      setUsers((prev) => [...prev, newUser]);
      showToast(`Usuario ${newUser.full_name} (${newUser.role}) creado exitosamente.`, 'success');
    } catch (err) {
      throw err;
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

  const technicians = users.filter(
    (u) => ['IT_STUDENT_SUPPORT', 'IT_STAFF_SUPPORT', 'ADMIN'].includes(u.role)
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Login Modal */}
      <LoginModal
        isOpen={isLoginModalOpen}
        users={users}
        onLogin={handleLogin}
        onClose={() => {
          if (currentUser) setIsLoginModalOpen(false);
        }}
      />

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

      {/* Navbar Superior con Selector de Rol/Persona */}
      {currentUser && (
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          currentUser={currentUser}
          users={users}
          onSwitchUser={handleSwitchUser}
          onOpenCreateModal={() => setIsCreateModalOpen(true)}
          isOnline={isOnline}
          onRefresh={fetchInitialData}
          onLogout={handleLogout}
        />
      )}

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
        ) : !currentUser ? (
          <div className="flex flex-col items-center justify-center py-24 text-slate-400">
            <p className="text-lg font-semibold mb-2">Bienvenido a Unified Service Desk</p>
            <p className="text-sm">Inicia sesión para continuar</p>
          </div>
        ) : (
          <>
            {/* 1. Vista de Solicitante (Estudiante o Personal) */}
            {activeTab === 'user_portal' && currentUser && (
              <UserPortal
                currentUser={currentUser}
                tickets={tickets}
                onOpenCreateModal={() => setIsCreateModalOpen(true)}
                onViewAudit={handleOpenAudit}
                onReopenTicket={handleReopenTicket}
              />
            )}

            {/* 2. Vista de Mesa de Ayuda TI / Kanban */}
            {activeTab === 'kanban' && (
              <KanbanBoard
                tickets={tickets}
                currentUser={currentUser}
                technicians={technicians}
                onTransitionStatus={handleTransitionStatus}
                onAssignTicket={handleAssignTicket}
                onViewAudit={handleOpenAudit}
                onDeleteTicket={handleDeleteTicket}
                isLoading={isLoading}
              />
            )}

            {/* 3. Panel de Administración de Usuarios (RBAC) */}
            {activeTab === 'admin_users' && (
              <AdminPanel
                users={users}
                tickets={tickets}
                onCreateUser={handleCreateUser}
                onOpenCreateTicketModal={() => setIsCreateModalOpen(true)}
              />
            )}

            {/* 4. Dashboard de Métricas TI */}
            {activeTab === 'dashboard' && (
              <Dashboard
                tickets={tickets}
                onSelectTicket={handleOpenAudit}
                onOpenCreateModal={() => setIsCreateModalOpen(true)}
              />
            )}

            {/* 5. Auditoría & Notificaciones */}
            {activeTab === 'audit' && (
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                <div className="mb-4">
                  <h2 className="text-xl font-bold text-white">Centro de Auditoría & Notificaciones</h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Inspección centralizada de eventos y notificaciones del sistema.
                  </p>
                </div>
                <button
                  onClick={() => {
                    setSelectedTicketForAudit(null);
                    setIsAuditModalOpen(true);
                  }}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md"
                >
                  Abrir Registro Completo de Notificaciones
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 py-4 text-center text-xs text-slate-500">
        <p>
          Unified Service Desk &bull; Plataforma Universitaria de Soporte Institucional
        </p>
      </footer>

      {/* Modales */}
      <TicketFormModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onTicketCreated={handleCreateTicket}
        currentUser={currentUser}
        users={users}
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
