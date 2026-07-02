import { useState } from "react"
import { motion } from "framer-motion"
import { BarChart3, TrendingUp, Filter, Download } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState("30d")

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-text flex items-center">
            <BarChart3 className="mr-3 text-primary" size={32} />
            Analytics & Insights
          </h1>
          <p className="text-text-muted mt-2">Deep dive into recruitment pipeline metrics and AI evaluation trends.</p>
        </div>
        <div className="flex gap-3">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-surface border border-surface-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          <Button variant="outline">
            <Filter size={16} className="mr-2" /> Filters
          </Button>
          <Button variant="default">
            <Download size={16} className="mr-2" /> Export Report
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card>
            <CardContent className="p-6">
              <p className="text-sm text-text-muted mb-1">Time to Hire (Avg)</p>
              <h3 className="text-3xl font-bold">14.2 <span className="text-lg text-text-muted font-normal">days</span></h3>
              <p className="text-sm text-success flex items-center mt-2">
                <TrendingUp size={16} className="mr-1" /> 12% faster than last month
              </p>
            </CardContent>
          </Card>
        </motion.div>
        
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card>
            <CardContent className="p-6">
              <p className="text-sm text-text-muted mb-1">AI Acceptance Rate</p>
              <h3 className="text-3xl font-bold">87%</h3>
              <p className="text-sm text-success flex items-center mt-2">
                <TrendingUp size={16} className="mr-1" /> 4% higher than last month
              </p>
            </CardContent>
          </Card>
        </motion.div>
        
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card>
            <CardContent className="p-6">
              <p className="text-sm text-text-muted mb-1">Pipeline Drop-off</p>
              <h3 className="text-3xl font-bold text-warning">24%</h3>
              <p className="text-sm text-text-muted flex items-center mt-2">
                Occurs mostly at technical assessment
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card className="h-96">
            <CardHeader>
              <CardTitle>Score Distribution</CardTitle>
            </CardHeader>
            <CardContent className="h-[250px] flex items-center justify-center border-2 border-dashed border-surface-border rounded-xl">
              [Recharts Area Chart Placeholder]
            </CardContent>
          </Card>
        </motion.div>
        
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Card className="h-96">
            <CardHeader>
              <CardTitle>Skill Gap Analysis</CardTitle>
            </CardHeader>
            <CardContent className="h-[250px] flex items-center justify-center border-2 border-dashed border-surface-border rounded-xl">
              [Recharts Radar Chart Placeholder]
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
