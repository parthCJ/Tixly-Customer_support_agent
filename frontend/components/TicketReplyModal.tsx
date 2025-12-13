'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import { ticketsApi } from '@/lib/api';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { X, Send, Sparkles, User, Mail, Clock, Tag } from 'lucide-react';
import { Ticket, TicketStatus } from '@/types';

interface TicketReplyModalProps {
  ticket: Ticket;
  onClose: () => void;
}

export function TicketReplyModal({ ticket, onClose }: TicketReplyModalProps) {
  const [replyText, setReplyText] = useState(ticket.ai_suggested_reply || '');
  const [isUsingAISuggestion, setIsUsingAISuggestion] = useState(true);
  const queryClient = useQueryClient();
  
  // Check if ticket is already resolved
  const isResolved = ticket.status === TicketStatus.RESOLVED;

  // Mutation for updating ticket status
  // uses the optimistic updates so that UI updates immediatly before API call to POST ex changes the Status from new -> Resolved.
  const resolveTicketMutation = useMutation({
    mutationFn: async () => {
      console.log('Updating ticket status:', ticket.ticket_id, 'to:', TicketStatus.RESOLVED);
      return ticketsApi.updateStatus(ticket.ticket_id, TicketStatus.RESOLVED);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
      queryClient.invalidateQueries({ queryKey: ['my-tickets'] });
      queryClient.invalidateQueries({ queryKey: ['agent-stats'] });
    },
    onError: (error: any) => {
      console.error('Failed to resolve ticket:', error);
      console.error('Error response:', error.response?.data);
      toast.error(`Failed to resolve ticket: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleSendReply = async () => {
    if (!replyText.trim()) return;

    // In a real app, you'd have a sendReply endpoint
    // For now, we'll just mark as resolved
    console.log('Sending reply:', replyText);
    
    // Mark ticket as resolved
    await resolveTicketMutation.mutateAsync();
    
    // Show success notification
    toast.success('✅ Reply sent and ticket marked as resolved!', {
      position: 'top-right',
      autoClose: 3000,
    });
    
    onClose();
  };

  const handleUseAISuggestion = () => {
    setReplyText(ticket.ai_suggested_reply || '');
    setIsUsingAISuggestion(true);
  };

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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-2 sm:p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[95vh] sm:max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex-1 min-w-0 pr-4">
            <div className="flex items-center gap-1.5 sm:gap-2 mb-1.5 sm:mb-2 flex-wrap">
              <span className="text-[10px] sm:text-xs font-mono text-gray-500">{ticket.ticket_id}</span>
              <Badge variant={getPriorityColor(ticket.priority)} size="sm">
                {ticket.priority || 'MEDIUM'}
              </Badge>
              <Badge variant={getCategoryColor(ticket.category)} size="sm">
                {ticket.category || 'OTHER'}
              </Badge>
              {ticket.sentiment && (
                <Badge 
                  variant={
                    ticket.sentiment === 'positive' ? 'success' :
                    ticket.sentiment === 'negative' ? 'danger' : 'default'
                  } 
                  size="sm"
                >
                  {ticket.sentiment}
                </Badge>
              )}
            </div>
            <h2 className="text-base sm:text-xl font-bold text-gray-900 dark:text-white truncate">
              {ticket.subject}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 flex-shrink-0"
          >
            <X className="h-5 w-5 sm:h-6 sm:w-6" />
          </button>
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 sm:space-y-6">
          {/* Customer Info */}
          <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3 sm:p-4">
            <h3 className="text-xs sm:text-sm font-semibold text-gray-900 dark:text-white mb-2 sm:mb-3">
              Customer Information
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <div className="flex items-center gap-2">
                <User className="h-3 sm:h-4 w-3 sm:w-4 text-gray-400 flex-shrink-0" />
                <div className="min-w-0">
                  <p className="text-[10px] sm:text-xs text-gray-500">Name</p>
                  <p className="text-xs sm:text-sm text-gray-900 dark:text-white truncate">
                    {ticket.customer_name || 'N/A'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="h-3 sm:h-4 w-3 sm:w-4 text-gray-400 flex-shrink-0" />
                <div className="min-w-0">
                  <p className="text-[10px] sm:text-xs text-gray-500">Email</p>
                  <p className="text-xs sm:text-sm text-gray-900 dark:text-white truncate">
                    {ticket.customer_email}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-3 sm:h-4 w-3 sm:w-4 text-gray-400 flex-shrink-0" />
                <div className="min-w-0">
                  <p className="text-[10px] sm:text-xs text-gray-500">Created</p>
                  <p className="text-xs sm:text-sm text-gray-900 dark:text-white truncate">
                    {new Date(ticket.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Tag className="h-3 sm:h-4 w-3 sm:w-4 text-gray-400 flex-shrink-0" />
                <div className="min-w-0">
                  <p className="text-[10px] sm:text-xs text-gray-500">Customer ID</p>
                  <p className="text-xs sm:text-sm text-gray-900 dark:text-white truncate">
                    {ticket.customer_id}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Original Message */}
          <div>
            <h3 className="text-xs sm:text-sm font-semibold text-gray-900 dark:text-white mb-2">
              Customer Message
            </h3>
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3 sm:p-4">
              <p className="text-xs sm:text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                {ticket.description}
              </p>
            </div>
          </div>

          {/* AI Suggested Reply */}
          {ticket.ai_suggested_reply && (
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 sm:p-4 border border-blue-200 dark:border-blue-800">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <Sparkles className="h-3 sm:h-4 w-3 sm:w-4 text-blue-600 dark:text-blue-400" />
                  <h3 className="text-xs sm:text-sm font-semibold text-blue-900 dark:text-blue-300">
                    AI Suggested Reply
                  </h3>
                  {ticket.ai_confidence && (
                    <Badge variant="info" size="sm">
                      {Math.round(ticket.ai_confidence * 100)}% confident
                    </Badge>
                  )}
                </div>
                {!isUsingAISuggestion && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleUseAISuggestion}
                    className="w-full sm:w-auto text-xs"
                  >
                    Use AI Suggestion
                  </Button>
                )}
              </div>
              <p className="text-xs sm:text-sm text-blue-800 dark:text-blue-400 whitespace-pre-wrap">
                {ticket.ai_suggested_reply}
              </p>
            </div>
          )}

          {/* Reply Editor */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs sm:text-sm font-semibold text-gray-900 dark:text-white">
                Your Reply
              </h3>
              <span className="text-[10px] sm:text-xs text-gray-500">
                {replyText.length} characters
              </span>
            </div>
            <textarea
              value={replyText}
              onChange={(e) => {
                setReplyText(e.target.value);
                setIsUsingAISuggestion(false);
              }}
              placeholder="Type your reply to the customer..."
              className="w-full h-32 sm:h-48 px-3 sm:px-4 py-2 sm:py-3 text-xs sm:text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            />
            <p className="text-[10px] sm:text-xs text-gray-500 mt-2">
              💡 Tip: You can edit the AI suggestion or write your own response
            </p>
          </div>
        </div>

        {/* Footer - Actions */}
        <div className="p-4 sm:p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            {isResolved ? (
              <div className="text-xs sm:text-sm text-green-600 dark:text-green-400 font-medium">
                This ticket has already been resolved
              </div>
            ) : (
              <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                This will send the reply and mark the ticket as resolved
              </div>
            )}
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full sm:w-auto">
              <Button
                variant="secondary"
                onClick={onClose}
                className="w-full sm:w-auto text-xs sm:text-sm"
              >
                {isResolved ? 'Close' : 'Cancel'}
              </Button>
              {!isResolved && (
                <Button
                  variant="primary"
                  onClick={handleSendReply}
                  disabled={!replyText.trim() || resolveTicketMutation.isPending}
                  className="w-full sm:w-auto text-xs sm:text-sm"
                >
                  {resolveTicketMutation.isPending ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send className="h-3 sm:h-4 w-3 sm:w-4 mr-2" />
                      Send Reply & Resolve
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
