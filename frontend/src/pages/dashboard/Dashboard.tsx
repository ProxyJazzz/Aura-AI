import { motion } from "framer-motion"
import { Users, FileText, CheckCircle, Activity, ArrowUpRight } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export function Dashboard() {
  const kpis = [
    { title: "Total Candidates", value: "2,845", trend: "+12%", icon: Users },
    { title: "Recent Uploads", value: "145", trend: "+4%", icon: FileText },
    { title: "Strong Hires", value: "32", trend: "+18%", icon: CheckCircle },
    { title: "AI Activity Rate", value: "98%", trend: "+2%", icon: Activity },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-text">Overview</h1>
        <p className="text-text-muted mt-2">Welcome to AURA AI. Here is what's happening with your recruitment funnel.</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, index) => (
          <motion.div
            key={kpi.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="hover:ambient-glow cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="p-3 bg-primary/10 rounded-xl text-primary">
                    <kpi.icon size={24} />
                  </div>
                  <div className="flex items-center space-x-1 text-success text-sm font-medium">
                    <span>{kpi.trend}</span>
                    <ArrowUpRight size={16} />
                  </div>
                </div>
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-text-muted">{kpi.title}</h3>
                  <p className="text-3xl font-bold mt-1">{kpi.value}</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-2"
        >
          <Card className="h-full min-h-[400px]">
            <CardHeader>
              <CardTitle>Recruitment Funnel</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-center h-[300px] text-text-muted border-2 border-dashed border-surface-border rounded-xl">
                [Recharts Funnel Chart Placeholder]
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="h-full">
            <CardHeader>
              <CardTitle>AI Insights</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 rounded-xl bg-accent/10 border border-accent/20">
                <h4 className="font-semibold text-accent mb-1">New Trend Detected</h4>
                <p className="text-sm text-text-muted">45% increase in candidates with React Native experience this week.</p>
              </div>
              <div className="p-4 rounded-xl bg-surface border border-surface-border">
                <h4 className="font-semibold mb-1">Risk Alert</h4>
                <p className="text-sm text-text-muted">3 candidates flagged as potential honeypots in the last hour.</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
