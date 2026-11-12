/**
 * Cliente de API para el backend de Unified Service Desk Universitario (FastAPI).
 *
 * Seguridad (DEF-04 / H-SEC-04):
 * - El token JWT se almacena en memoria (módulo-level), NO en localStorage.
 * - Todas las peticiones protegidas adjuntan Authorization: Bearer <token>.
 * - Intercepta 401/403 para limpiar sesión o mostrar acceso denegado.
 * - El email NUNCA se usa como credencial de identidad ante el backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Token JWT en memoria del módulo — no persiste en localStorage (DEF-04)
let _accessToken = null;

/** Almacena el token JWT emitido tras un login exitoso. */
export function setAccessToken(token) {
  _accessToken = token;
}

/** Elimina el token JWT de memoria (logout). */
export function clearAccessToken() {
  _accessToken = null;
}

/** Devuelve el token JWT actual (para uso interno). */
export function getAccessToken() {
  return _accessToken;
}

/**
 * Construye los headers HTTP para peticiones al backend.
 * Adjunta Authorization: Bearer <token> si existe un token activo.
 */
function buildHeaders(extra = {}) {
  const headers = { 'Content-Type': 'application/json', ...extra };
  if (_accessToken) {
    headers['Authorization'] = `Bearer ${_accessToken}`;
  }
  return headers;
}

/**
 * Procesa la respuesta HTTP.
 * - 401: limpia sesión y dispara evento para redirigir al login.
 * - 403: lanza error de acceso denegado visible al usuario.
 */
async function handleResponse(response) {
  if (response.status === 401) {
    clearAccessToken();
    // Notifica a App.jsx que debe cerrar sesión y mostrar login
    window.dispatchEvent(new CustomEvent('auth:unauthorized'));
    throw new Error('Sesión expirada. Por favor inicia sesión nuevamente.');
  }

  if (response.status === 403) {
    throw new Error('Acceso denegado. No tienes permiso para realizar esta acción.');
  }

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
  // ==========================================
  // SALUD DEL BACKEND
  // ==========================================
  async checkHealth() {
    try {
      const res = await fetch('http://localhost:8000/health');
      return await res.json();
    } catch {
      return { status: 'offline' };
    }
  },

  // ==========================================
  // AUTENTICACIÓN & USUARIOS (DEF-04)
  // ==========================================

  /**
   * Login real: envía email + password al backend.
   * Almacena el JWT en memoria del módulo (no en localStorage).
   * Retorna el objeto usuario del payload de TokenResponse.
   */
  async login(email, password) {
    if (!password) {
      throw new Error('Se requiere contraseña para iniciar sesión.');
    }
    const res = await fetch(`${API_BASE_URL}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await handleResponse(res);
    // Almacenar token en memoria — nunca en localStorage
    if (data.access_token) {
      setAccessToken(data.access_token);
    }
    return data.user; // UserResponse
  },

  /** Cierra sesión limpiando el token de memoria. */
  logout() {
    clearAccessToken();
  },

  /** Obtiene el usuario autenticado desde el JWT (endpoint /me). */
  async getMe() {
    const res = await fetch(`${API_BASE_URL}/users/me`, {
      headers: buildHeaders(),
    });
    return handleResponse(res);
  },

  async getUsers(role = null) {
    const url = role
      ? `${API_BASE_URL}/users/?role=${encodeURIComponent(role)}`
      : `${API_BASE_URL}/users/`;
    const res = await fetch(url, { headers: buildHeaders() });
    return handleResponse(res);
  },

  async createUser(userData) {
    const res = await fetch(`${API_BASE_URL}/users/`, {
      method: 'POST',
      headers: buildHeaders(),
      body: JSON.stringify(userData),
    });
    return handleResponse(res);
  },

  async seedUsers() {
    const res = await fetch(`${API_BASE_URL}/users/seed`, {
      method: 'POST',
      headers: buildHeaders(),
    });
    return handleResponse(res);
  },

  async getUserById(userId) {
    const res = await fetch(`${API_BASE_URL}/users/${userId}`, {
      headers: buildHeaders(),
    });
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
    const res = await fetch(url, { headers: buildHeaders() });
    return handleResponse(res);
  },

  async getTicketById(ticketId) {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}`, {
      headers: buildHeaders(),
    });
    return handleResponse(res);
  },

  async createTicket(ticketData) {
    const res = await fetch(`${API_BASE_URL}/tickets/`, {
      method: 'POST',
      headers: buildHeaders(),
      body: JSON.stringify(ticketData),
    });
    return handleResponse(res);
  },

  async assignTicket(ticketId, assignedToId, reason = '', assignedByUserId = null) {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}/assign`, {
      method: 'POST',
      headers: buildHeaders(),
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
      headers: buildHeaders(),
      body: JSON.stringify({
        target_status: targetStatus,
        reason: reason,
        user_id: userId,
      }),
    });
    return handleResponse(res);
  },

  async getTicketAuditLogs(ticketId) {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}/audit-logs`, {
      headers: buildHeaders(),
    });
    return handleResponse(res);
  },

  async getSentNotifications() {
    const res = await fetch(`${API_BASE_URL}/tickets/notifications/sent`, {
      headers: buildHeaders(),
    });
    return handleResponse(res);
  },

  async deleteTicket(ticketId) {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}`, {
      method: 'DELETE',
      headers: buildHeaders(),
    });
    return handleResponse(res);
  },

  async getMetrics() {
    const res = await fetch(`${API_BASE_URL}/tickets/metrics`, {
      headers: buildHeaders(),
    });
    return handleResponse(res);
  },
};
