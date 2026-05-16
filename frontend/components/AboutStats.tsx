interface HealthData {
  items_this_month?: number
  last_pipeline_run?: string | null
}

interface AboutStatsProps {
  health: HealthData | null
}

export function AboutStats({ health }: AboutStatsProps) {
  const lastUpdated = health?.last_pipeline_run
    ? new Date(health.last_pipeline_run).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
      })
    : null

  return (
    <div
      style={{
        background: 'var(--color-background-primary)',
        border: '0.5px solid var(--color-border-tertiary)',
        borderRadius: 'var(--border-radius-lg)',
        padding: '20px 24px',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        gap: 32,
      }}
    >
      <div
        style={{
          fontSize: 13,
          color: 'var(--color-text-secondary)',
          lineHeight: 1.6,
          maxWidth: 560,
        }}
      >
        View the Board converts official county and LCPS meeting records into plain-English summaries, structured action logs, and decision timelines — powered by Gemma 4, linked to every official source.
      </div>

      {health && (
        <div
          style={{
            flexShrink: 0,
            textAlign: 'right',
            display: 'flex',
            flexDirection: 'column',
            gap: 10,
          }}
        >
          {lastUpdated && (
            <div>
              <div style={{ fontSize: 11, color: 'var(--color-text-secondary)', marginBottom: 2 }}>
                Last updated
              </div>
              <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--color-text-primary)' }}>
                {lastUpdated}
              </div>
            </div>
          )}
          {health.items_this_month != null && (
            <div>
              <div style={{ fontSize: 11, color: 'var(--color-text-secondary)', marginBottom: 2 }}>
                Items this month
              </div>
              <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--color-text-primary)' }}>
                {health.items_this_month} agenda items
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
