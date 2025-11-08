'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { Suspense } from 'react';

function SuccessContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const ticketId = searchParams.get('ticket_id');

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Success Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center border border-gray-100">
          {/* Success Icon */}
          <div className="mb-6">
            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>

          {/* Success Message */}
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Ticket Submitted!
          </h1>
          <p className="text-gray-600 mb-6">
            Your support ticket has been received and is being processed by our AI
          </p>

          {/* Ticket ID */}
          {ticketId && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-500 mb-1">Your Ticket ID</p>
              <p className="text-lg font-mono font-semibold text-gray-900">{ticketId}</p>
            </div>
          )}

          {/* Timeline */}
          <div className="mb-8 text-left">
            <div className="space-y-4">
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3">
                  <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Ticket Created</p>
                  <p className="text-sm text-gray-500">Your ticket has been logged</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                  <svg className="w-4 h-4 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">AI Processing</p>
                  <p className="text-sm text-gray-500">Analyzing and categorizing...</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center mr-3">
                  <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
                    <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Agent Response</p>
                  <p className="text-sm text-gray-500">You'll hear from us soon!</p>
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-3">
            <button
              onClick={() => router.push('/submit-ticket')}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all"
            >
              Submit Another Ticket
            </button>
            <button
              onClick={() => router.push('/agent/tickets')}
              className="w-full bg-gray-100 text-gray-700 font-semibold py-3 px-6 rounded-lg hover:bg-gray-200 transition-all"
            >
              View Agent Dashboard
            </button>
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Check your email</strong> - We've sent a confirmation to your inbox with your ticket details.
          </p>
        </div>
      </div>
    </div>
  );
}

export default function SuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    }>
      <SuccessContent />
    </Suspense>
  );
}
