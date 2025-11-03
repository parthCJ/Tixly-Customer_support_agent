// Ticket Types
export enum TicketStatus {
  NEW = "new",
  IN_PROGRESS = "in_progress",
  RESOLVED = "resolved",
  CLOSED = "closed"
}

export enum TicketPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical"
}

export enum TicketCategory {
  SHIPPING = "SHIPPING",
  BILLING = "BILLING",
  REFUND = "REFUND",
  PRODUCT_INQUIRY = "PRODUCT_INQUIRY",
  TECHNICAL = "TECHNICAL",
  RETURNS = "RETURNS",
  ACCOUNT_ACCESS = "ACCOUNT_ACCESS",
  PAYMENT_ISSUE = "PAYMENT_ISSUE",
  OTHER = "OTHER"
}

export interface AIClassification {
  category?: string;
  priority?: string;
  suggested_reply?: string;
  confidence?: number;
  sentiment?: string;
}

export interface Ticket {
  ticket_id: string;
  subject: string;
  description: string;
  customer_email: string;
  customer_name?: string;
  customer_id: string;
  status: TicketStatus;
  priority?: TicketPriority;
  category?: TicketCategory;
  assigned_to?: string;
  assigned_agent_id?: string; // Agent ID assigned to ticket
  team?: string;
  sentiment?: string;
  ai_classification?: AIClassification; // AI-generated classification
  ai_suggested_category?: TicketCategory;
  ai_suggested_priority?: TicketPriority;
  ai_suggested_reply?: string;
  ai_confidence?: number;
  urgency_keywords?: string[];
  created_at: string;
  updated_at: string;
  resolved_at?: string;
}

// Agent Types
export enum AgentStatus {
  ACTIVE = "active",
  AWAY = "away",
  OFFLINE = "offline"
}

export interface Agent {
  agent_id: string;
  name: string;
  email: string;
  team?: string;
  skills: string[];
  max_tickets_per_day: number;
  current_load: number;
  status: AgentStatus;
  active: boolean;
  created_at: string;
  last_active: string;
  total_tickets_resolved: number;
  avg_resolution_time_minutes?: number;
}

export interface AgentStats {
  agent_id: string;
  name: string;
  current_load: number;
  max_tickets_per_day: number;
  utilization_percentage: number;
  available_capacity: number;
  is_available: boolean;
  total_tickets_resolved: number;
  avg_resolution_time_minutes?: number;
  status: AgentStatus;
}

// Forecasting Types
export interface HourlyForecast {
  hour: number;
  predicted_tickets: number;
  timestamp: string;
}

export interface DailyForecast {
  date: string;
  predicted_tickets: number;
  day_of_week: string;
}

export interface StaffingRecommendation {
  predicted_tickets: number;
  recommended_agents: number;
  tickets_per_agent: number;
  urgency: string;
  message: string;
}

// API Response Types
export interface TicketResponse {
  ticket: Ticket;
  ai_suggested_category?: TicketCategory;
  ai_suggested_priority?: TicketPriority;
  ai_suggested_reply?: string;
  ai_confidence?: number;
}

export interface AssignmentResponse {
  ticket: Ticket;
  assignment: {
    mode: string;
    agent_id: string;
    agent_name: string;
    agent_load: number;
    message: string;
  };
}
