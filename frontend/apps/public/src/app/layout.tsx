import React from 'react';
import './global.css';
import Providers from './providers';
import { Inter as FontSans } from 'next/font/google';
import { cn } from '@shared/utils';
import { Footer } from '../components/footer/footer';
import { Metadata, Viewport } from 'next';
import { fetchPublicInfo } from '../utils/queries/public-info';
import { Header } from '../components/header/header';
import { TailwindIndicator } from '@shared/components/tailwind-indicator'

export async function generateMetadata(): Promise<Metadata> {
  const data = await fetchPublicInfo();
  const name = data?.result.name.name ?? "Hell Let Loose"
  return {
    title: {
      template: `%s - ${name}`,
      default: name,
    },
  }
}

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "white" },
    { media: "(prefers-color-scheme: dark)", color: "black" },
  ],
}
  
const fontSans = FontSans({
  subsets: ['latin'],
  variable: '--font-sans',
});

type RootLayoutProps = {
  children: React.ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <>
      <html lang="en" suppressHydrationWarning>
        <head />
        <body
          className={cn(
            'min-h-screen bg-background font-sans antialiased',
            fontSans.variable
          )}
        >
          <Providers>
            <div className="relative flex min-h-screen flex-col">
              <Header />
              <main className='container px-1 sm:px-4 relative flex min-h-screen flex-col bg-background gap-1'>
                {children}
              </main>
              <Footer />
            </div>
          </Providers>
          <TailwindIndicator />
        </body>
      </html>
    </>
  );
}
