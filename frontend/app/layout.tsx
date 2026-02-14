import type { Metadata } from 'next';
import './globals.css';
import 'react-toastify/dist/ReactToastify.css';
import Providers from './providers';

export const metadata: Metadata = {
  title: 'Customer Support Copilot - AI-Powered Support Platform',
  description: 'Intelligent ticket management with AI classification, automated replies, and predictive analytics',
  icons: {
    icon: '/favicon.svg',
    apple: '/apple-touch-icon.svg',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
