import React from 'react';

interface LogoProps {
  size?: number;
  className?: string;
}

export default function Logo({ size = 40, className = '' }: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Outer gradient circle */}
      <defs>
        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#3b82f6', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: '#8b5cf6', stopOpacity: 1 }} />
        </linearGradient>
        <linearGradient id="ticketGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#60a5fa', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: '#a78bfa', stopOpacity: 1 }} />
        </linearGradient>
      </defs>

      {/* Background circle */}
      <circle cx="50" cy="50" r="48" fill="url(#logoGradient)" opacity="0.15" />
      
      {/* Stylized "T" lettermark integrated with ticket shape */}
      <path
        d="M 30 25 L 70 25 L 70 35 L 55 35 L 55 75 L 45 75 L 45 35 L 30 35 Z"
        fill="url(#ticketGradient)"
      />
      
      {/* AI circuit nodes - small dots around the T */}
      <circle cx="35" cy="30" r="2.5" fill="#60a5fa" opacity="0.8" />
      <circle cx="65" cy="30" r="2.5" fill="#a78bfa" opacity="0.8" />
      <circle cx="50" cy="45" r="2.5" fill="#8b5cf6" opacity="0.8" />
      <circle cx="45" cy="65" r="2.5" fill="#3b82f6" opacity="0.8" />
      <circle cx="55" cy="65" r="2.5" fill="#8b5cf6" opacity="0.8" />
      
      {/* Connecting lines for circuit effect */}
      <line x1="35" y1="30" x2="45" y2="35" stroke="#60a5fa" strokeWidth="1" opacity="0.4" />
      <line x1="65" y1="30" x2="55" y2="35" stroke="#a78bfa" strokeWidth="1" opacity="0.4" />
      <line x1="50" y1="45" x2="45" y2="65" stroke="#8b5cf6" strokeWidth="1" opacity="0.4" />
      <line x1="50" y1="45" x2="55" y2="65" stroke="#8b5cf6" strokeWidth="1" opacity="0.4" />
      
      {/* Sparkle effect - small star in top right */}
      <path
        d="M 75 20 L 76.5 23 L 80 23 L 77 25.5 L 78 29 L 75 26.5 L 72 29 L 73 25.5 L 70 23 L 73.5 23 Z"
        fill="#fbbf24"
        opacity="0.9"
      />
    </svg>
  );
}

// Alternative compact version for small spaces
export function LogoCompact({ size = 32, className = '' }: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id="compactGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#3b82f6', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: '#8b5cf6', stopOpacity: 1 }} />
        </linearGradient>
      </defs>
      
      {/* Simplified T with gradient */}
      <path
        d="M 25 20 L 75 20 L 75 32 L 58 32 L 58 80 L 42 80 L 42 32 L 25 32 Z"
        fill="url(#compactGradient)"
      />
      
      {/* Small sparkle */}
      <circle cx="72" cy="25" r="3" fill="#fbbf24" opacity="0.9" />
    </svg>
  );
}
