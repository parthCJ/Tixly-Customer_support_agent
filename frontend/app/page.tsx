'use client';

import Link from 'next/link';
import Image from 'next/image';

export default function HomePage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="text-center px-4 sm:px-6">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <Image 
            src="/tixly-logo.svg" 
            alt="Tixly" 
            width={400} 
            height={100}
            className="h-24 sm:h-32 w-auto"
            priority
          />
        </div>

        {/* Heading */}
        <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
          AI-Powered Customer Support
        </h1>
        <p className="text-lg sm:text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Get instant assistance with our intelligent support system
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            href="/submit-ticket"
            className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg font-semibold rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
          >
            Create Ticket
          </Link>
          <Link
            href="/agent"
            className="w-full sm:w-auto px-8 py-4 bg-gray-800 text-white text-lg font-semibold rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
          >
            Agent Dashboard
          </Link>
        </div>

        {/* Features */}
        <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <div className="p-6 bg-white rounded-xl shadow-md">
            <h3 className="font-semibold text-gray-900 mb-2">Instant Response</h3>
            <p className="text-sm text-gray-600">AI-powered instant ticket analysis and routing</p>
          </div>
          <div className="p-6 bg-white rounded-xl shadow-md">
            <h3 className="font-semibold text-gray-900 mb-2">Smart Routing</h3>
            <p className="text-sm text-gray-600">Intelligent ticket assignment to the right agent</p>
          </div>
          <div className="p-6 bg-white rounded-xl shadow-md">
            <h3 className="font-semibold text-gray-900 mb-2">Analytics</h3>
            <p className="text-sm text-gray-600">Real-time insights and forecasting</p>
          </div>
        </div>
      </div>
    </div>
  );
}
