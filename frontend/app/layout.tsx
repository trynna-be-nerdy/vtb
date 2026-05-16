import type { Metadata } from 'next'
import { Providers } from '@/lib/providers'
import { PageInfoWidget } from '@/components/PageInfoWidget'
import './globals.css'

export const metadata: Metadata = {
  title: 'View the Board — Loudoun County Government Decisions',
  description:
    'Plain-English summaries of Loudoun County government board meetings, decisions, and agenda items — updated automatically from official public records.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" data-theme="vtb">
      <body>
        <Providers>
          {children}
          <PageInfoWidget />
        </Providers>
      </body>
    </html>
  )
}
