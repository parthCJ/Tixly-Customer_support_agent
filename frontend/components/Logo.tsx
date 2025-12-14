import React from 'react';
import Image from 'next/image';

interface LogoProps {
  size?: number;
  className?: string;
}

export default function Logo({ size = 75, className = '' }: LogoProps) {
  return (
    <div className={`flex items-center justify-center pt-6 ${className}`}>
      <Image 
        src="/tixly-logo.svg" 
        alt="Tixly" 
        width={size * 8} 
        height={size}
        className="object-contain"
        priority
      />
    </div>
  );
}

// Alternative compact version for small spaces (just the ticket icon)
export function LogoCompact({ size = 35, className = '' }: LogoProps) {
  return (
    <Image 
      src="/tixly-icon.svg" 
      alt="Tixly" 
      width={size} 
      height={size}
      className={`object-contain ${className}`}
    />
  );
}
