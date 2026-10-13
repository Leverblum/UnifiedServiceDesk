/**
 * Cliente de API para el backend de Unified Service Desk (FastAPI).
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = 'Error en el servidor';
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || JSON.stringify(errorJson);
    } catch {
      errorDetail = await response.text();
    }
    throw new Error(errorDetail);
  }
  if (response.status === 204) {
    return true;
  }
  return response.json();
}

export const apiService = {
  // Verificación de salud del backend
  async checkHealth() {
    try {
      const res = await fetch('http://localhost:8000/health');
      return await res.json();
    } catch {
      return { status: 'offline' };
    }
  },

  // Obtener todos los tickets con filtros opcionales
  async getTickets(filters = {}) {
    const params = new URLSearchParams();
    if (filters.category) params.append('category', filters.category);
    if (filters.status) params.append('status', filters.status);
    if (filters.skip) params.append('skip', filters.skip);
    if (filters.limit) params.append('limit', filters.limit);

    const url = `${API_BASE_URL}/tickets/?${params.toString()}`;
    const res = await fetch(url);
    return handleResponse(res);
  },

  // Obtener un ticket por ID
  async getTicketById(ticketId) {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}`);
    return handleResponse(res);
  },

  // Crear nuevo ticket (Factory Method + Observer)
  async createTicket(ticketData) {
    const res = await fetch(`${API_BASE_URL}/tickets/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ticketData),
    });
    return handleResponse(res);
  },

  // Transicionar estado de un ticket (State Pattern + Observer)
  async updateTicketStatus(ticketId, targetStatus, reason = '') {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_status: targetStatus,
        reason: reason,
      }),
    });
    return handleResponse(res);
  },

  // Obtener registros de auditoría de un ticket (AuditLogObserver)
  async getTicketAuditLogs(ticketId) {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}/audit-logs`);
    return handleResponse(res);
  },

  // Obtener notificaciones simuladas por correo (EmailNotifierObserver)
  async getSentNotifications() {
    const res = await fetch(`${API_BASE_URL}/tickets/notifications/sent`);
    return handleResponse(res);
  },

  // Eliminar ticket
  async deleteTicket(ticketId) {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },
};
