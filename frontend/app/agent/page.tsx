'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ticketsApi, agentsApi } from '@/lib/api';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { TicketReplyModal } from '@/components/TicketReplyModal';
import { Clock, User, MessageSquare, CheckCircle2, AlertCircle } from 'lucide-react';
import type { Ticket } from '@/types';

export default function AgentDashboard() {
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const { data: tickets = [], isLoading: ticketsLoading } = useQuery({
    queryKey: ['tickets'],
    queryFn: () => ticketsApi.getAll(),
  });

  const { data: agentStats = [], isLoading: statsLoading } = useQuery({
    queryKey: ['agent-stats'],
    queryFn: () => agentsApi.getStats(),
  });

  // Filter tickets for current agent (AGENT-001 for demo)
  const myTickets = tickets.filter(t => t.assigned_to === 'AGENT-001' || t.assigned_agent_id === 'AGENT-001');
  const newTickets = myTickets.filter(t => t.status === 'new');
  const inProgressTickets = myTickets.filter(t => t.status === 'in_progress');
  const resolvedTickets = myTickets.filter(t => t.status === 'resolved');

  const getPriorityColor = (priority?: string) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
      case 'urgent':
        return 'danger';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'default';
      default:
        return 'default';
    }
  };

  const getCategoryColor = (category?: string) => {
    const colors: Record<string, 'default' | 'success' | 'warning' | 'danger' | 'info'> = {
      'billing_issue': 'warning',
      'technical_support': 'danger',
      'shipping_delay': 'info',
      'product_defect': 'warning',
      'account_access': 'danger',
      'refund_request': 'warning',
      'general_inquiry': 'success',
      'other': 'default',
    };
    return colors[category || ''] || 'default';
  };

  if (ticketsLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Agent Dashboard
        </h1>
        <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
          Welcome back! Here's what's happening with your tickets today.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">My Tickets</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {myTickets.length}
              </p>
            </div>
            <User className="h-8 w-8 text-gray-400" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">New</p>
              <p className="text-2xl font-bold text-yellow-600">
                {newTickets.length}
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-yellow-400" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">In Progress</p>
              <p className="text-2xl font-bold text-blue-600">
                {inProgressTickets.length}
              </p>
            </div>
            <Clock className="h-8 w-8 text-blue-400" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Resolved</p>
              <p className="text-2xl font-bold text-green-600">
                {resolvedTickets.length}
              </p>
            </div>
            <CheckCircle2 className="h-8 w-8 text-green-400" />
          </div>
        </Card>
      </div>

      {/* Recent Tickets */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Recent Tickets
        </h2>

        {myTickets.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No tickets assigned to you yet
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                When tickets are assigned to you, they'll appear here.
              </p>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-3 sm:gap-4">
            {myTickets.slice(0, 6).map((ticket) => (
              <Card key={ticket.ticket_id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <span className="text-xs font-mono text-gray-500">{ticket.ticket_id}</span>
                        <Badge variant={getPriorityColor(ticket.priority)} size="sm">
                          {ticket.priority || 'MEDIUM'}
                        </Badge>
                        <Badge variant={getCategoryColor(ticket.category)} size="sm">
                          {ticket.category || 'OTHER'}
                        </Badge>
                      </div>
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-1 text-sm sm:text-base">
                        {ticket.subject}
                      </h3>
                      <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300 line-clamp-2">
                        {ticket.description}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-xs text-gray-500 dark:text-gray-400">
                    <div className="flex items-center gap-1 truncate">
                      <User className="h-3 w-3 flex-shrink-0" />
                      <span className="truncate">{ticket.customer_email}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3 flex-shrink-0" />
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </div>
                  </div>

                  {ticket.ai_suggested_reply && (
                    <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                      <div className="flex items-start gap-2">
                        <MessageSquare className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-medium text-blue-900 dark:text-blue-300 mb-1">
                            AI Suggested Reply
                          </p>
                          <p className="text-xs text-blue-800 dark:text-blue-400 line-clamp-2">
                            {ticket.ai_suggested_reply}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="flex flex-col sm:flex-row gap-2 pt-2">
                    <Button 
                      size="sm" 
                      variant="primary" 
                      className="flex-1 w-full sm:w-auto"
                      onClick={() => setSelectedTicket(ticket)}
                    >
                      Reply
                    </Button>
                    <Button 
                      size="sm" 
                      variant="secondary" 
                      className="flex-1 w-full sm:w-auto"
                      onClick={() => setSelectedTicket(ticket)}
                    >
                      View Details
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Reply Modal */}
      {selectedTicket && (
        <TicketReplyModal
          ticket={selectedTicket}
          onClose={() => setSelectedTicket(null)}
        />
      )}
    </div>
  );
}
