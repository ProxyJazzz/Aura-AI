import { motion } from "framer-motion"
import { Download, FileText, Calendar, Filter } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

const REPORTS = [
  { id: 1, title: "Q2 Engineering Hiring Summary", date: "Jul 1, 2026", type: "Quarterly", status: "Ready" },
  { id: 2, title: "Diversity & Inclusion Metrics", date: "Jun 15, 2026", type: "Compliance", status: "Ready" },
  { id: 3, title: "Time-to-Hire Analysis", date: "Jun 01, 2026", type: "Performance", status: "Ready" },
]

export function ReportsPage() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-text flex items-center">
            <FileText className="mr-3 text-primary" size={32} />
            Reports
          </h1>
          <p className="text-text-muted mt-2">Exportable compliance and performance intelligence reports.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <Filter size={16} className="mr-2" /> Filter
          </Button>
          <Button variant="default">
            Generate New Report
          </Button>
        </div>
      </div>

      <div className="grid gap-4">
        {REPORTS.map((report, index) => (
          <motion.div
            key={report.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="hover:ambient-glow transition-all">
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-surface-hover rounded-xl text-text-muted">
                    <FileText size={24} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-text">{report.title}</h3>
                    <div className="flex items-center gap-3 mt-1 text-xs text-text-muted">
                      <span className="flex items-center gap-1"><Calendar size={12}/> {report.date}</span>
                      <span>•</span>
                      <Badge variant="secondary">{report.type}</Badge>
                    </div>
                  </div>
                </div>
                <Button variant="ghost" size="icon" className="text-text-muted hover:text-primary">
                  <Download size={20} />
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
