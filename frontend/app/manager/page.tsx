'use client';

import { useQuery } from '@tanstack/react-query';
import { agentsApi, forecastingApi } from '@/lib/api';
import { Card, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Users, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';

export default function ManagerDashboard() {
  // Fetch data
  const { data: agentStats, isLoading: statsLoading } = useQuery({
    queryKey: ['agent-stats'],
    queryFn: () => agentsApi.getStats(),
  });

  const { data: dailyForecast, isLoading: forecastLoading } = useQuery({
    queryKey: ['daily-forecast'],
    queryFn: () => forecastingApi.getDaily(7),
  });

  const { data: staffing, isLoading: staffingLoading } = useQuery({
    queryKey: ['staffing'],
    queryFn: () => forecastingApi.getStaffing(),
  });

  if (statsLoading || forecastLoading || staffingLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading analytics...</p>
        </div>
      </div>
    );
  }

  // Calculate team metrics
  const totalAgents = agentStats?.length || 0;
  const activeAgents = agentStats?.filter((a) => a.is_available).length || 0;
  const totalLoad = agentStats?.reduce((sum, a) => sum + a.current_load, 0) || 0;
  const totalCapacity = agentStats?.reduce((sum, a) => sum + a.max_tickets_per_day, 0) || 0;
  const avgUtilization = totalCapacity > 0 ? (totalLoad / totalCapacity) * 100 : 0;

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Manager Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Team performance and forecasting overview
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Agents</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {totalAgents}
              </p>
              <p className="text-xs text-gray-500 mt-1">{activeAgents} active</p>
            </div>
            <div className="h-12 w-12 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
              <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Tickets</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {totalLoad}
              </p>
              <p className="text-xs text-gray-500 mt-1">of {totalCapacity} capacity</p>
            </div>
            <div className="h-12 w-12 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Team Utilization</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {avgUtilization.toFixed(0)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">Average across team</p>
            </div>
            <div className="h-12 w-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
              <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Recommended Staff</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {staffing?.recommended_agents || 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {staffing?.urgency || 'normal'} priority
              </p>
            </div>
            <div className={`h-12 w-12 rounded-full flex items-center justify-center ${
              staffing?.urgency === 'critical' ? 'bg-red-100 dark:bg-red-900' :
              staffing?.urgency === 'high' ? 'bg-orange-100 dark:bg-orange-900' :
              'bg-yellow-100 dark:bg-yellow-900'
            }`}>
              <AlertTriangle className={`h-6 w-6 ${
                staffing?.urgency === 'critical' ? 'text-red-600 dark:text-red-400' :
                staffing?.urgency === 'high' ? 'text-orange-600 dark:text-orange-400' :
                'text-yellow-600 dark:text-yellow-400'
              }`} />
            </div>
          </div>
        </Card>
      </div>

      {/* Staffing Alert */}
      {staffing && (
        <div className={`mb-8 p-4 rounded-lg ${
          staffing.urgency === 'critical' ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800' :
          staffing.urgency === 'high' ? 'bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800' :
          'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900 dark:text-white">{staffing.message}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Based on {staffing.predicted_tickets} predicted tickets ({staffing.tickets_per_agent} tickets/agent)
              </p>
            </div>
            <Button variant="primary" size="sm">Schedule Agents</Button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Agent Performance */}
        <Card>
          <CardHeader
            title="Agent Performance"
            subtitle={`${activeAgents} agents currently active`}
          />
          <div className="space-y-4">
            {agentStats?.slice(0, 5).map((agent) => (
              <div key={agent.agent_id} className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-medium text-gray-900 dark:text-white">{agent.name}</p>
                    <Badge variant={agent.is_available ? 'success' : 'default'}>
                      {agent.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>{agent.current_load}/{agent.max_tickets_per_day} tickets</span>
                    <span>•</span>
                    <span>{agent.utilization_percentage.toFixed(0)}% utilized</span>
                    <span>•</span>
                    <span>{agent.total_tickets_resolved} resolved</span>
                  </div>
                  <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        agent.utilization_percentage > 80 ? 'bg-red-600' :
                        agent.utilization_percentage > 60 ? 'bg-yellow-600' :
                        'bg-green-600'
                      }`}
                      style={{ width: `${Math.min(agent.utilization_percentage, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* 7-Day Forecast */}
        <Card>
          <CardHeader
            title="7-Day Ticket Forecast"
            subtitle="LSTM predictions"
          />
          <div className="space-y-3">
            {dailyForecast?.map((day, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <p className="font-medium text-gray-900 dark:text-white">
                      {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {day.predicted_tickets} tickets
                    </p>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${Math.min((day.predicted_tickets / 150) * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
