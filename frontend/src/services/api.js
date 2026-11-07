/**
 * Cliente de API para el backend de Unified Service Desk Universitario (FastAPI).
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = 'Error en el servidor universitario';
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

  // ==========================================
  // AUTENTICACIÓN & USUARIOS
  // ==========================================
  async login(email, password = '12345') {
    const res = await fetch(`${API_BASE_URL}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(res);
  },

  async getUsers(role = null) {
    const url = role ? `${API_BASE_URL}/users/?role=${encodeURIComponent(role)}` : `${API_BASE_URL}/users/`;
    const res = await fetch(url);
    return handleResponse(res);
  },

  async createUser(userData) {
    const res = await fetch(`${API_BASE_URL}/users/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    return handleResponse(res);
  },

  async seedUsers() {
    const res = await fetch(`${API_BASE_URL}/users/seed`, {
      method: 'POST',
    });
    return handleResponse(res);
  },

  async getUserById(userId) {
    const res = await fetch(`${API_BASE_URL}/users/${userId}`);
    return handleResponse(res);
  },

  // ==========================================
  // TICKETS Y CASOS UNIVERSITARIOS
  // ==========================================
  async getTickets(filters = {}) {
    const params = new URLSearchParams();
    if (filters.category) params.append('category', filters.category);
    if (filters.status) params.append('status', filters.status);
    if (filters.created_by_id) params.append('created_by_id', filters.created_by_id);
    if (filters.assigned_to_id) params.append('assigned_to_id', filters.assigned_to_id);
    if (filters.unassigned) params.append('unassigned', 'true');
    if (filters.skip) params.append('skip', filters.skip);
    if (filters.limit) params.append('limit', filters.limit);

    const url = `${API_BASE_URL}/tickets/?${params.toString()}`;
    const res = await fetch(url);
    return handleResponse(res);
  },

  async getTicketById(ticketId) {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}`);
    return handleResponse(res);
  },

  async createTicket(ticketData) {
    const res = await fetch(`${API_BASE_URL}/tickets/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ticketData),
    });
    return handleResponse(res);
  },

  async assignTicket(ticketId, assignedToId, reason = '', assignedByUserId = null) {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}/assign`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        assigned_to_id: assignedToId,
        reason: reason,
        assigned_by_user_id: assignedByUserId,
      }),
    });
    return handleResponse(res);
  },

  async updateTicketStatus(ticketId, targetStatus, reason = '', userId = null) {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_status: targetStatus,
        reason: reason,
        user_id: userId,
      }),
    });
    return handleResponse(res);
  },

  async getTicketAuditLogs(ticketId) {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}/audit-logs`);
    return handleResponse(res);
  },

  async getSentNotifications() {
    const res = await fetch(`${API_BASE_URL}/tickets/notifications/sent`);
    return handleResponse(res);
  },

  async deleteTicket(ticketId) {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },
};
