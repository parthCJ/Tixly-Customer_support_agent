'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Users, BarChart3, Settings, LogOut, Menu, X } from 'lucide-react';
import { useState } from 'react';
import Logo, { LogoCompact } from './Logo';

export default function Sidebar() {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/agent', icon: Home },
    { name: 'My Tickets', href: '/agent/tickets', icon: Users },
    { name: 'Analytics', href: '/manager', icon: BarChart3 },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 flex h-24 items-center justify-between bg-gray-900 px-4 border-b border-gray-800">
        <div className="flex items-center gap-3 flex-1">
          <img src="/tixly-logo.svg" alt="Tixly" className="h-20 w-auto max-w-[75%]" />
        </div>
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="text-white p-2 hover:bg-gray-800 rounded-lg transition-colors"
        >
          {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 z-40 bg-black bg-opacity-50"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-40
        flex h-screen w-64 flex-col bg-gray-900
        transform transition-transform duration-300 ease-in-out
        lg:translate-x-0
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:mt-0 mt-24
      `}>
      {/* Logo - Hidden on mobile, shown on desktop */}
      <div className="hidden lg:flex h-24 items-center justify-center gap-3 border-b border-gray-800 px-4">
        <Logo size={64} />
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              onClick={() => setIsMobileMenuOpen(false)}
              className={`
                flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors
                ${
                  isActive
                    ? 'bg-gray-800 text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }
              `}
            >
              <Icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* User info */}
      <div className="border-t border-gray-800 p-4">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-white text-sm font-medium">
            A
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-white">Agent User</p>
            <p className="text-xs text-gray-400">agent@company.com</p>
          </div>
          <button className="text-gray-400 hover:text-white">
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </div>
      </div>
    </>
  );
}
