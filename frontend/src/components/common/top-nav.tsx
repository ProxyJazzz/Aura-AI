import { Bell, Search, Menu } from "lucide-react"

export function TopNav() {
  return (
    <header className="h-20 w-full px-8 flex items-center justify-between sticky top-0 z-30 bg-background/80 backdrop-blur-md border-b border-surface-border/50">
      <div className="flex items-center">
        {/* Mobile menu trigger - hidden on desktop */}
        <button className="mr-4 lg:hidden p-2 rounded-lg hover:bg-surface-hover text-text-muted">
          <Menu size={24} />
        </button>
        <h2 className="text-lg font-medium text-text-muted hidden md:block">
          Good morning, Jane
        </h2>
      </div>

      <div className="flex items-center space-x-4">
        {/* Global Search Trigger */}
        <button className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-surface border border-surface-border text-sm text-text-muted hover:bg-surface-hover hover:border-surface-border/80 transition-colors w-64">
          <Search size={16} />
          <span className="flex-1 text-left">Search anything...</span>
          <div className="flex space-x-1">
            <kbd className="bg-background px-1.5 py-0.5 rounded text-xs">⌘</kbd>
            <kbd className="bg-background px-1.5 py-0.5 rounded text-xs">K</kbd>
          </div>
        </button>

        {/* Notifications */}
        <button className="p-2 relative rounded-lg hover:bg-surface-hover text-text-muted transition-colors">
          <Bell size={20} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-accent animate-pulse" />
        </button>
      </div>
    </header>
  )
}
