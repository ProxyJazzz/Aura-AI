import { NavLink } from "react-router-dom"
import { LayoutDashboard, Users, Upload, TrendingUp, BarChart2, Settings, Command, FileText } from "lucide-react"

const NAV_ITEMS = [
  { name: "Dashboard", path: "/", icon: LayoutDashboard },
  { name: "Candidates", path: "/candidates", icon: Users },
  { name: "Upload Center", path: "/upload", icon: Upload },
  { name: "AI Ranking", path: "/ranking", icon: TrendingUp },
  { name: "Analytics", path: "/analytics", icon: BarChart2 },
  { name: "Reports", path: "/reports", icon: FileText },
]

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-[260px] p-6">
      <div className="glass-panel h-full w-full flex flex-col p-4 shadow-2xl">
        
        {/* Logo */}
        <div className="flex items-center space-x-3 mb-10 px-2 pt-2">
          <div className="bg-primary/20 p-2 rounded-xl text-primary border border-primary/30">
            <Command size={24} />
          </div>
          <span className="text-xl font-bold tracking-tight">AURA AI</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-2">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) => `
                flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200
                ${isActive 
                  ? 'bg-primary/20 text-text font-medium border border-primary/30' 
                  : 'text-text-muted hover:bg-surface-hover hover:text-text border border-transparent'
                }
              `}
            >
              <item.icon size={20} className="shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>

        {/* Bottom Actions */}
        <div className="mt-auto space-y-2 pt-4 border-t border-surface-border">
          <NavLink
            to="/settings"
            className={({ isActive }) => `
              flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200
              ${isActive 
                ? 'bg-primary/20 text-text font-medium' 
                : 'text-text-muted hover:bg-surface-hover hover:text-text'
              }
            `}
          >
            <Settings size={20} />
            <span>Settings</span>
          </NavLink>
          
          <div className="mt-4 p-3 bg-surface rounded-xl border border-surface-border flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-xs font-bold shadow-lg">
              JS
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="text-sm font-medium truncate">Jane Smith</p>
              <p className="text-xs text-text-muted truncate">Recruitment Lead</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
