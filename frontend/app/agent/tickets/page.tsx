'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ticketsApi } from '@/lib/api';
import { Card, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { TicketReplyModal } from '@/components/TicketReplyModal';
import { Clock, User, Tag, AlertCircle, CheckCircle2, MessageSquare } from 'lucide-react';
import { Ticket, TicketStatus } from '@/types';

export default function MyTicketsPage() {
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const { data: tickets = [], isLoading, error } = useQuery({
    queryKey: ['my-tickets'],
    queryFn: () => ticketsApi.getAll(),
    staleTime: 10000, // Data stays fresh for 10 seconds (reduces refetches)
    refetchInterval: 30000, // Auto-refetch every 30 seconds
    retry: 2, // Retry failed requests twice
  });

  // Filter tickets assigned to current agent (AGENT-001 for demo)
  const myTickets = tickets.filter(t => t.assigned_to === 'AGENT-001' || t.assigned_agent_id === 'AGENT-001');

  // Group tickets by status
  const newTickets = myTickets.filter(t => t.status === TicketStatus.NEW);
  const inProgressTickets = myTickets.filter(t => t.status === TicketStatus.IN_PROGRESS);
  const resolvedTickets = myTickets.filter(t => t.status === TicketStatus.RESOLVED);

  // Loading state with skeleton
  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-6"></div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white dark:bg-gray-800 rounded-lg p-4">
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/3"></div>
              </div>
            ))}
          </div>
          
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-white dark:bg-gray-800 rounded-lg p-4 h-32"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
            <h3 className="font-semibold text-red-900 dark:text-red-100">Failed to load tickets</h3>
          </div>
          <p className="text-red-700 dark:text-red-300 text-sm">
            {error instanceof Error ? error.message : 'An error occurred while fetching tickets'}
          </p>
          <Button 
            onClick={() => window.location.reload()} 
            variant="secondary" 
            size="sm"
            className="mt-3"
          >
            Retry
          </Button>
        </div>
      </div>
    );
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'URGENT': return 'danger';
      case 'HIGH': return 'warning';
      case 'MEDIUM': return 'info';
      case 'LOW': return 'default';
      default: return 'default';
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, 'default' | 'success' | 'warning' | 'danger' | 'info'> = {
      'BILLING': 'warning',
      'TECHNICAL': 'danger',
      'SHIPPING': 'info',
      'PRODUCT_INQUIRY': 'success',
      'REFUND': 'warning',
      'ACCOUNT_ACCESS': 'danger',
      'PAYMENT_ISSUE': 'warning',
      'RETURNS': 'info',
      'OTHER': 'default',
    };
    return colors[category] || 'default';
  };

  const TicketCard = ({ ticket }: { ticket: Ticket }) => (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer">
      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-mono text-gray-500">{ticket.ticket_id}</span>
              <Badge variant={getPriorityColor((ticket.ai_classification?.priority || ticket.priority) as string)} size="sm">
                {ticket.ai_classification?.priority || ticket.priority || 'medium'}
              </Badge>
              <Badge variant={getCategoryColor((ticket.ai_classification?.category || ticket.category) as string)} size="sm">
                {ticket.ai_classification?.category || ticket.category || 'general_inquiry'}
              </Badge>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
              {ticket.subject}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-2">
              {ticket.description}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 mb-3">
          <div className="flex items-center gap-1">
            <User className="h-3 w-3" />
            {ticket.customer_email}
          </div>
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {new Date(ticket.created_at).toLocaleDateString()}
          </div>
        </div>

        {ticket.ai_classification?.suggested_reply && (
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 mb-3">
            <div className="flex items-start gap-2">
              <MessageSquare className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-xs font-medium text-blue-900 dark:text-blue-300 mb-1">
                  AI Suggested Reply
                </p>
                <p className="text-xs text-blue-800 dark:text-blue-400 line-clamp-3">
                  {ticket.ai_classification.suggested_reply}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="flex gap-2">
          <Button 
            size="sm" 
            variant="primary" 
            className="flex-1"
            onClick={() => setSelectedTicket(ticket)}
          >
            Reply
          </Button>
          <Button 
            size="sm" 
            variant="secondary" 
            className="flex-1"
            onClick={() => setSelectedTicket(ticket)}
          >
            View Details
          </Button>
        </div>
      </div>
    </Card>
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          My Tickets
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Manage your assigned support tickets
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {myTickets.length}
                </p>
              </div>
              <Tag className="h-8 w-8 text-gray-400" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">New</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {newTickets.length}
                </p>
              </div>
              <AlertCircle className="h-8 w-8 text-yellow-400" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">In Progress</p>
                <p className="text-2xl font-bold text-blue-600">
                  {inProgressTickets.length}
                </p>
              </div>
              <Clock className="h-8 w-8 text-blue-400" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Resolved</p>
                <p className="text-2xl font-bold text-green-600">
                  {resolvedTickets.length}
                </p>
              </div>
              <CheckCircle2 className="h-8 w-8 text-green-400" />
            </div>
          </div>
        </Card>
      </div>

      {/* Ticket Lists */}
      <div className="space-y-6">
        {/* New Tickets */}
        {newTickets.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-yellow-500" />
              New Tickets ({newTickets.length})
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {newTickets.map(ticket => (
                <TicketCard key={ticket.ticket_id} ticket={ticket} />
              ))}
            </div>
          </div>
        )}

        {/* In Progress Tickets */}
        {inProgressTickets.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-500" />
              In Progress ({inProgressTickets.length})
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {inProgressTickets.map(ticket => (
                <TicketCard key={ticket.ticket_id} ticket={ticket} />
              ))}
            </div>
          </div>
        )}

        {/* Resolved Tickets */}
        {resolvedTickets.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              Resolved ({resolvedTickets.length})
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {resolvedTickets.slice(0, 6).map(ticket => (
                <TicketCard key={ticket.ticket_id} ticket={ticket} />
              ))}
            </div>
          </div>
        )}

        {/* No tickets message */}
        {myTickets.length === 0 && (
          <div className="text-center py-12">
            <Tag className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No tickets assigned
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              You don't have any tickets assigned to you yet.
            </p>
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
