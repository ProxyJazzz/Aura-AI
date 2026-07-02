import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Search, Filter, Star, AlertTriangle, ShieldCheck, ExternalLink } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

// Mock data
const CANDIDATES = [
  { id: 1, name: "Alice Chen", role: "Senior Frontend Engineer", score: 92, status: "Strong Hire", risk: "Low" },
  { id: 2, name: "Bob Smith", role: "Backend Developer", score: 85, status: "Hire", risk: "Low" },
  { id: 3, name: "Charlie Davis", role: "Full Stack Engineer", score: 71, status: "Technical Interview", risk: "Medium" },
  { id: 4, name: "Diana Prince", role: "Product Manager", score: 45, status: "Reject", risk: "High" },
]

export function CandidateExplorer() {
  const [selectedId, setSelectedId] = useState<number | null>(1)

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col md:flex-row gap-6">
      
      {/* Panel 1: List */}
      <Card className="w-full md:w-1/3 h-full flex flex-col overflow-hidden bg-surface/30 backdrop-blur-md border-surface-border/50 shadow-2xl">
        <div className="p-5 border-b border-surface-border/30 space-y-4">
          <div className="relative group">
            <Search className="absolute left-3 top-2.5 text-text-muted group-focus-within:text-primary transition-colors" size={16} />
            <input 
              type="text" 
              placeholder="Search candidates..." 
              className="w-full bg-surface-hover/50 rounded-lg pl-9 pr-4 py-2 focus:outline-none focus:ring-1 focus:ring-primary/50 transition-all text-sm border border-transparent focus:bg-surface"
            />
          </div>
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
            <Badge variant="secondary" className="cursor-pointer whitespace-nowrap bg-surface-hover hover:bg-surface-border font-normal text-xs"><Filter size={12} className="mr-1"/> All Roles</Badge>
            <Badge variant="secondary" className="cursor-pointer whitespace-nowrap bg-surface-hover hover:bg-surface-border font-normal text-xs">Status</Badge>
            <Badge variant="secondary" className="cursor-pointer whitespace-nowrap bg-surface-hover hover:bg-surface-border font-normal text-xs">Risk</Badge>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2 space-y-2">
          {CANDIDATES.map(c => (
            <div 
              key={c.id}
              onClick={() => setSelectedId(c.id)}
              className={`p-4 rounded-xl cursor-pointer transition-all duration-200 ${selectedId === c.id ? 'bg-primary/10 border-l-2 border-l-primary shadow-inner bg-gradient-to-r from-primary/5 to-transparent' : 'hover:bg-surface-hover/50 border-l-2 border-l-transparent'}`}
            >
              <div className="flex justify-between items-start mb-1">
                <h4 className="font-semibold">{c.name}</h4>
                <Badge variant={c.score >= 85 ? 'success' : c.score >= 70 ? 'accent' : c.score >= 50 ? 'warning' : 'destructive'}>
                  {c.score}
                </Badge>
              </div>
              <p className="text-sm text-text-muted">{c.role}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Panel 2 & 3 wrapper for responsive logic */}
      <div className="w-full md:w-2/3 h-full flex flex-col lg:flex-row gap-6">
        
        <AnimatePresence mode="wait">
          {selectedId ? (
            <>
              {/* Panel 2: Profile */}
              <motion.div 
                key={`profile-${selectedId}`}
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.2 }}
                className="w-full lg:w-1/2 h-full"
              >
                <Card className="h-full flex flex-col overflow-hidden bg-surface/30 backdrop-blur-md border-surface-border/50 shadow-2xl">
                  <div className="p-6 border-b border-surface-border">
                    <div className="flex justify-between items-start">
                      <div>
                        <h2 className="text-2xl font-bold">Alice Chen</h2>
                        <p className="text-text-muted">Senior Frontend Engineer • San Francisco, CA</p>
                      </div>
                      <a href="#" className="p-2 hover:bg-surface-hover rounded-full transition-colors">
                        <ExternalLink size={20} className="text-text-muted hover:text-accent" />
                      </a>
                    </div>
                  </div>
                  <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    <section>
                      <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-3">Experience</h3>
                      <div className="space-y-4">
                        <div className="border-l-2 border-surface-border pl-4">
                          <h4 className="font-medium">Senior Frontend Engineer @ TechCorp</h4>
                          <p className="text-xs text-text-muted mb-2">2020 - Present</p>
                          <p className="text-sm">Led the migration to React 18, improving TTI by 40%. Architected a new component library.</p>
                        </div>
                      </div>
                    </section>
                    <section>
                      <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-3">Skills</h3>
                      <div className="flex flex-wrap gap-2">
                        {['React', 'TypeScript', 'Next.js', 'Tailwind', 'GraphQL'].map(s => (
                          <Badge key={s} variant="secondary">{s}</Badge>
                        ))}
                      </div>
                    </section>
                  </div>
                </Card>
              </motion.div>

              {/* Panel 3: AI Analysis */}
              <motion.div 
                key={`analysis-${selectedId}`}
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ delay: 0.1, duration: 0.2 }}
                className="w-full lg:w-1/2 h-full"
              >
                <Card className="h-full flex flex-col bg-accent/5 backdrop-blur-md border-accent/20 overflow-hidden shadow-2xl shadow-accent/5">
                  <div className="p-6 border-b border-accent/10 flex items-center justify-between">
                    <h2 className="text-lg font-semibold flex items-center text-accent">
                      <ShieldCheck size={20} className="mr-2" />
                      AI Decision Profile
                    </h2>
                    <Badge variant="success">Strong Hire</Badge>
                  </div>
                  <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-surface rounded-xl border border-surface-border text-center">
                        <p className="text-xs text-text-muted mb-1">Overall Match</p>
                        <p className="text-3xl font-bold text-success">92%</p>
                      </div>
                      <div className="p-4 bg-surface rounded-xl border border-surface-border text-center">
                        <p className="text-xs text-text-muted mb-1">Confidence</p>
                        <p className="text-3xl font-bold">0.89</p>
                      </div>
                    </div>

                    <div>
                      <h3 className="font-medium mb-3 flex items-center">
                        <Star size={16} className="text-success mr-2" /> Key Strengths
                      </h3>
                      <ul className="space-y-2 text-sm text-text-muted pl-6 list-disc">
                        <li>High semantic context match</li>
                        <li>Exceptional skill alignment (React, TS)</li>
                        <li>Strong relevant experience</li>
                      </ul>
                    </div>

                    <div>
                      <h3 className="font-medium mb-3 flex items-center">
                        <AlertTriangle size={16} className="text-warning mr-2" /> Risk Factors
                      </h3>
                      <div className="p-3 bg-surface rounded-lg border border-surface-border">
                        <p className="text-sm text-text-muted">No significant risks detected. Low risk profile.</p>
                      </div>
                    </div>

                  </div>
                </Card>
              </motion.div>
            </>
          ) : (
            <div className="w-full h-full flex items-center justify-center text-text-muted">
              Select a candidate to view details
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
