import { useState, useEffect } from 'react'
import { Command } from 'cmdk'
import { Search, Users, LayoutDashboard, Settings, FileText, Upload, TrendingUp, BarChart2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }

    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  const runCommand = (command: () => void) => {
    setOpen(false)
    command()
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm"
            onClick={() => setOpen(false)}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="fixed left-[50%] top-[20%] z-50 w-full max-w-2xl translate-x-[-50%] overflow-hidden rounded-xl border border-surface-border bg-surface shadow-2xl shadow-accent/5"
          >
            <Command className="flex h-full w-full flex-col overflow-hidden rounded-xl bg-transparent">
              <div className="flex items-center border-b border-surface-border px-4 py-3 text-text-muted">
                <Search size={18} className="mr-3 shrink-0 opacity-50" />
                <Command.Input 
                  autoFocus
                  placeholder="Search candidates, pages, or commands..." 
                  className="flex h-10 w-full rounded-md bg-transparent text-sm outline-none placeholder:text-text-muted disabled:cursor-not-allowed disabled:opacity-50 border-none focus:ring-0 text-text"
                />
              </div>
              
              <Command.List className="max-h-[300px] overflow-y-auto overflow-x-hidden p-2">
                <Command.Empty className="py-6 text-center text-sm text-text-muted">
                  No results found.
                </Command.Empty>
                
                <Command.Group heading="Navigation" className="text-xs font-medium text-text-muted px-2 py-1.5">
                  {[
                    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
                    { name: 'Candidates', path: '/candidates', icon: Users },
                    { name: 'Upload Resumes', path: '/upload', icon: Upload },
                    { name: 'AI Ranking', path: '/ranking', icon: TrendingUp },
                    { name: 'Analytics', path: '/analytics', icon: BarChart2 },
                    { name: 'Settings', path: '/settings', icon: Settings },
                  ].map((item) => (
                    <Command.Item
                      key={item.path}
                      onSelect={() => runCommand(() => navigate(item.path))}
                      className="flex cursor-pointer items-center rounded-md px-2 py-2 text-sm text-text hover:bg-primary/20 hover:text-text aria-selected:bg-primary/20 aria-selected:text-text transition-colors mt-1"
                    >
                      <item.icon size={16} className="mr-3 opacity-70" />
                      {item.name}
                    </Command.Item>
                  ))}
                </Command.Group>
                
                <Command.Group heading="Quick Actions" className="text-xs font-medium text-text-muted px-2 py-1.5 mt-2 border-t border-surface-border/50">
                  <Command.Item
                    onSelect={() => runCommand(() => console.log('Create Profile'))}
                    className="flex cursor-pointer items-center rounded-md px-2 py-2 text-sm text-text hover:bg-primary/20 hover:text-text aria-selected:bg-primary/20 aria-selected:text-text transition-colors mt-1"
                  >
                    <FileText size={16} className="mr-3 opacity-70" />
                    Create Hiring Profile
                  </Command.Item>
                </Command.Group>
              </Command.List>
            </Command>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
