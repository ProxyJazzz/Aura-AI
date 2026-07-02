import { Bell, Search, Menu, Command } from "lucide-react"
import { AuraPulse } from "./AuraPulse"

export function TopNav() {
  return (
    <header className="h-16 w-full px-8 xl:px-10 flex items-center justify-between sticky top-0 z-30 bg-background border-b border-surface-border">
      <div className="flex items-center gap-4">
        {/* Mobile menu trigger - hidden on desktop */}
        <button className="lg:hidden p-2 rounded-md hover:bg-surface-hover text-text-muted transition-colors">
          <Menu size={20} />
        </button>
        <div className="hidden md:flex items-center gap-3">
          <div className="p-1.5 bg-surface rounded-md border border-surface-border">
            <Command size={16} className="text-text-muted" />
          </div>
          <span className="text-sm text-text-muted font-medium">/</span>
          <span className="text-sm text-text font-medium">Command Center</span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Global Search Trigger */}
        <button className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-surface border border-surface-border text-sm text-text-muted hover:bg-surface-hover transition-colors w-64 group">
          <Search size={14} className="group-hover:text-text transition-colors" />
          <span className="flex-1 text-left">Search...</span>
          <div className="flex space-x-1 opacity-60">
            <kbd className="bg-surface-hover px-1.5 py-0.5 rounded text-[10px] font-medium text-text border border-surface-border">Ctrl</kbd>
            <kbd className="bg-surface-hover px-1.5 py-0.5 rounded text-[10px] font-medium text-text border border-surface-border">K</kbd>
          </div>
        </button>

        {/* Notifications */}
        <button className="p-2 relative rounded-md hover:bg-surface-hover text-text-muted transition-colors">
          <Bell size={18} />
          <span className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-accent" />
        </button>

        <div className="w-px h-6 bg-surface-border mx-2" />

        <div className="flex items-center gap-3">
          <span className="text-xs font-medium text-text-muted uppercase tracking-wider">System Normal</span>
          <AuraPulse state="idle" size={16} />
        </div>
      </div>
    </header>
  )
}
