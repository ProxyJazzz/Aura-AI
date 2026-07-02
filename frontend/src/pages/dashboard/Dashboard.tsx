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
    <div className="space-y-8 max-w-[1600px] mx-auto pb-12">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-text">Command Center</h1>
          <p className="text-text-muted mt-2">Real-time intelligence on your recruitment pipeline.</p>
        </div>
        <div className="flex items-center space-x-3 text-sm font-medium text-text-muted bg-surface/50 border border-surface-border px-4 py-2 rounded-lg">
          <Activity size={16} className="text-primary animate-pulse" />
          <span>Live Intelligence Active</span>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, index) => (
          <motion.div
            key={kpi.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.2 }}
          >
            <Card className="hover:shadow-2xl transition-all cursor-pointer bg-surface/30 backdrop-blur-sm border-surface-border/50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-medium text-text-muted">{kpi.title}</h3>
                  <div className="flex items-center space-x-1 text-success bg-success/10 px-2 py-0.5 rounded text-xs font-medium border border-success/20">
                    <span>{kpi.trend}</span>
                    <ArrowUpRight size={14} />
                  </div>
                </div>
                <div className="flex items-end justify-between">
                  <p className="text-4xl font-bold tracking-tight">{kpi.value}</p>
                  <kpi.icon size={24} className="text-primary/50" />
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.2 }}
          className="lg:col-span-2"
        >
          <Card className="h-full min-h-[400px] border-surface-border/50 bg-surface/20">
            <CardHeader className="border-b border-surface-border/30 pb-4">
              <CardTitle className="text-lg">Recruitment Pipeline Activity</CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="flex flex-col items-center justify-center h-[300px] text-text-muted bg-surface/30 rounded-xl border border-surface-border/50 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-tr from-primary/5 via-transparent to-accent/5 pointer-events-none" />
                <Activity size={32} className="opacity-20 mb-4" />
                <span className="text-sm">Interactive Pipeline Chart Available</span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.2 }}
          className="flex flex-col gap-6"
        >
          <Card className="flex-1 border-surface-border/50 bg-surface/20">
            <CardHeader className="border-b border-surface-border/30 pb-4">
              <CardTitle className="text-lg flex items-center"><Activity size={18} className="mr-2 text-primary" /> Live Intelligence</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-surface-border/30">
                <div className="p-5 hover:bg-surface-hover/50 transition-colors">
                  <div className="flex items-center space-x-2 mb-2">
                    <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                    <h4 className="font-semibold text-accent text-sm tracking-wide uppercase">Talent Shift</h4>
                  </div>
                  <p className="text-sm text-text-muted leading-relaxed">45% increase in React Native experience among recent uploads. Consider adjusting requirements.</p>
                </div>
                <div className="p-5 hover:bg-surface-hover/50 transition-colors">
                  <div className="flex items-center space-x-2 mb-2">
                    <div className="w-2 h-2 rounded-full bg-warning" />
                    <h4 className="font-semibold text-warning text-sm tracking-wide uppercase">Risk Alert</h4>
                  </div>
                  <p className="text-sm text-text-muted leading-relaxed">3 candidates flagged with conflicting employment timelines in the last hour.</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
