import axios from 'axios';
import type {
  Ticket,
  TicketResponse,
  Agent,
  AgentStats,
  HourlyForecast,
  DailyForecast,
  StaffingRecommendation,
  AssignmentResponse,
  TicketStatus
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

console.log('🔧 API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout for API calls
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('📤 API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('❌ Request setup error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.config.url, response.status);
    return response;
  },
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('⏱️ Request timeout - backend may be slow');
      console.error('   URL:', error.config?.url);
      console.error('   Timeout:', error.config?.timeout, 'ms');
    } else if (error.response?.status === 500) {
      console.error('🔥 Server error:', error.response.data);
    } else if (!error.response) {
      console.error('🔌 Network error - backend not reachable:', error.message);
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Tickets API
// ============================================================================

export const ticketsApi = {
  // Get all tickets
  getAll: async (): Promise<Ticket[]> => {
    const response = await api.get('/api/tickets');
    return response.data;
  },

  // Get single ticket
  getById: async (ticketId: string): Promise<Ticket> => {
    const response = await api.get(`/api/tickets/${ticketId}`);
    return response.data;
  },

  // Create ticket
  create: async (data: {
    subject: string;
    description: string;
    customer_email: string;
    customer_name?: string;
  }): Promise<TicketResponse> => {
    const response = await api.post('/api/tickets/create', data);
    return response.data;
  },

  // Update ticket status
  updateStatus: async (ticketId: string, status: TicketStatus): Promise<Ticket> => {
    const response = await api.put(`/api/tickets/${ticketId}/status?status=${status}`);
    return response.data;
  },

  // Assign ticket
  assign: async (
    ticketId: string,
    options: { agent_id?: string; auto_assign?: boolean }
  ): Promise<AssignmentResponse> => {
    const response = await api.put(`/api/tickets/${ticketId}/assign`, null, {
      params: options,
    });
    return response.data;
  },

  // Unassign ticket
  unassign: async (ticketId: string): Promise<{ ticket: Ticket; message: string }> => {
    const response = await api.put(`/api/tickets/${ticketId}/unassign`);
    return response.data;
  },
};

// ============================================================================
// Agents API
// ============================================================================

export const agentsApi = {
  // Get all agents
  getAll: async (filters?: {
    team?: string;
    status?: string;
    active_only?: boolean;
  }): Promise<Agent[]> => {
    const response = await api.get('/api/agents/', { params: filters });
    return response.data;
  },

  // Get agent by ID
  getById: async (agentId: string): Promise<Agent> => {
    const response = await api.get(`/api/agents/${agentId}`);
    return response.data;
  },

  // Get agent statistics
  getStats: async (team?: string): Promise<AgentStats[]> => {
    const response = await api.get('/api/agents/stats', {
      params: team ? { team } : undefined,
    });
    return response.data;
  },

  // Get available agents by skill
  getAvailableBySkill: async (skill: string): Promise<{
    skill: string;
    available_count: number;
    agents: any[];
  }> => {
    const response = await api.get('/api/agents/available/by-skill', {
      params: { skill },
    });
    return response.data;
  },

  // Update agent status
  updateStatus: async (
    agentId: string,
    status: string
  ): Promise<{ agent_id: string; name: string; status: string; message: string }> => {
    const response = await api.post(`/api/agents/${agentId}/status`, null, {
      params: { status },
    });
    return response.data;
  },

  // Create agent
  create: async (data: {
    agent_id: string;
    name: string;
    email: string;
    team?: string;
    skills?: string[];
    max_tickets_per_day?: number;
  }): Promise<Agent> => {
    const response = await api.post('/api/agents/', data);
    return response.data;
  },

  // Update agent
  update: async (
    agentId: string,
    data: Partial<Agent>
  ): Promise<Agent> => {
    const response = await api.put(`/api/agents/${agentId}`, data);
    return response.data;
  },

  // Delete agent
  delete: async (
    agentId: string,
    permanent: boolean = false
  ): Promise<{ message: string }> => {
    const response = await api.delete(`/api/agents/${agentId}`, {
      params: { permanent },
    });
    return response.data;
  },
};

// ============================================================================
// Forecasting API
// ============================================================================

export const forecastingApi = {
  // Get hourly forecast
  getHourly: async (hours: number = 24): Promise<HourlyForecast[]> => {
    const response = await api.get(`/api/forecast/hourly/${hours}`);
    return response.data.forecast;
  },

  // Get daily forecast
  getDaily: async (days: number = 7): Promise<DailyForecast[]> => {
    const response = await api.get(`/api/forecast/daily/${days}`);
    return response.data.predictions;
  },

  // Get current staffing recommendation
  getStaffing: async (): Promise<StaffingRecommendation & { current_hour: string }> => {
    const response = await api.get('/api/forecast/staffing/current');
    return response.data;
  },

  // Get model info
  getModelInfo: async (): Promise<{
    model_loaded: boolean;
    model_path: string;
    sequence_length: number;
    features: string[];
  }> => {
    const response = await api.get('/api/forecast/model/info');
    return response.data;
  },
};

export default api;
