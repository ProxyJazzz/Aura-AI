import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Trophy, ChevronDown, ChevronUp, Download } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

const RANKINGS = [
  { id: 1, rank: 1, name: "Alice Chen", role: "Senior Frontend Engineer", score: 92, semantic: 95, skill: 90, experience: 88, education: 100 },
  { id: 2, rank: 2, name: "Bob Smith", role: "Backend Developer", score: 85, semantic: 80, skill: 85, experience: 90, education: 80 },
  { id: 3, rank: 3, name: "Charlie Davis", role: "Full Stack Engineer", score: 71, semantic: 70, skill: 75, experience: 70, education: 60 },
]

export function Leaderboard() {
  const [expandedId, setExpandedId] = useState<number | null>(null)

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-text flex items-center">
            <Trophy className="mr-3 text-warning" size={32} />
            AI Ranking Leaderboard
          </h1>
          <p className="text-text-muted mt-2">Deterministic hybrid rankings for the active hiring profile.</p>
        </div>
        <Button variant="outline">
          <Download size={16} className="mr-2" /> Export CSV
        </Button>
      </div>

      <Card className="bg-surface/30 backdrop-blur-md border-surface-border/50 shadow-2xl">
        <div className="p-4 bg-surface-hover border-b border-surface-border grid grid-cols-12 gap-4 text-sm font-medium text-text-muted">
          <div className="col-span-1 text-center">Rank</div>
          <div className="col-span-4">Candidate</div>
          <div className="col-span-3 text-center">Overall Score</div>
          <div className="col-span-3 text-center">Recommendation</div>
          <div className="col-span-1"></div>
        </div>
        
        <div className="divide-y divide-surface-border">
          {RANKINGS.map(candidate => (
            <div key={candidate.id} className="group">
              <div 
                className="p-4 grid grid-cols-12 gap-4 items-center hover:bg-surface-hover/50 cursor-pointer transition-colors"
                onClick={() => setExpandedId(expandedId === candidate.id ? null : candidate.id)}
              >
                <div className="col-span-1 flex justify-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${candidate.rank === 1 ? 'bg-warning/20 text-warning' : candidate.rank === 2 ? 'bg-muted/20 text-muted' : candidate.rank === 3 ? 'bg-accent/20 text-accent' : 'bg-surface border border-surface-border'}`}>
                    {candidate.rank}
                  </div>
                </div>
                <div className="col-span-4">
                  <p className="font-semibold">{candidate.name}</p>
                  <p className="text-sm text-text-muted">{candidate.role}</p>
                </div>
                <div className="col-span-3 flex justify-center items-center">
                  <div className="flex items-end gap-1">
                    <span className="text-2xl font-bold">{candidate.score}</span>
                    <span className="text-sm text-text-muted mb-1">/ 100</span>
                  </div>
                </div>
                <div className="col-span-3 flex justify-center">
                  <Badge variant={candidate.score >= 85 ? 'success' : candidate.score >= 70 ? 'accent' : 'warning'}>
                    {candidate.score >= 85 ? 'Strong Hire' : candidate.score >= 70 ? 'Hire' : 'Technical Interview'}
                  </Badge>
                </div>
                <div className="col-span-1 flex justify-end">
                  <Button variant="ghost" size="icon">
                    {expandedId === candidate.id ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </Button>
                </div>
              </div>

              <AnimatePresence>
                {expandedId === candidate.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden bg-surface-hover/30"
                  >
                    <div className="p-8 border-t border-surface-border/50 bg-gradient-to-b from-surface-hover/30 to-transparent">
                      <h4 className="text-sm font-semibold text-text mb-6 flex items-center">
                        <Trophy size={16} className="text-warning mr-2" />
                        AI RANKING EXPLAINABILITY
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="p-4 bg-surface rounded-lg border border-surface-border">
                          <p className="text-xs text-text-muted">Semantic Match</p>
                          <p className="text-xl font-bold mt-1">{candidate.semantic}</p>
                        </div>
                        <div className="p-4 bg-surface rounded-lg border border-surface-border">
                          <p className="text-xs text-text-muted">Skill Alignment</p>
                          <p className="text-xl font-bold mt-1">{candidate.skill}</p>
                        </div>
                        <div className="p-4 bg-surface rounded-lg border border-surface-border">
                          <p className="text-xs text-text-muted">Experience Score</p>
                          <p className="text-xl font-bold mt-1">{candidate.experience}</p>
                        </div>
                        <div className="p-4 bg-surface rounded-lg border border-surface-border">
                          <p className="text-xs text-text-muted">Education Score</p>
                          <p className="text-xl font-bold mt-1">{candidate.education}</p>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
