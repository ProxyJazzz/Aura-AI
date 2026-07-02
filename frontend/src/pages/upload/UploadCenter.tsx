import { useState, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { UploadCloud, FileText, CheckCircle2, XCircle, Loader2 } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"

type UploadStatus = "idle" | "uploading" | "success" | "error"

interface UploadFile {
  id: string
  name: string
  status: UploadStatus
  progress: number
  error?: string
}

export function UploadCenter() {
  const [files, setFiles] = useState<UploadFile[]>([])
  const [isDragging, setIsDragging] = useState(false)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true)
    } else if (e.type === "dragleave") {
      setIsDragging(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const newFiles = Array.from(e.dataTransfer.files).map(file => ({
        id: Math.random().toString(36).substring(7),
        name: file.name,
        status: "idle" as UploadStatus,
        progress: 0
      }))
      setFiles(prev => [...newFiles, ...prev])
      simulateUpload(newFiles)
    }
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files).map(file => ({
        id: Math.random().toString(36).substring(7),
        name: file.name,
        status: "idle" as UploadStatus,
        progress: 0
      }))
      setFiles(prev => [...newFiles, ...prev])
      simulateUpload(newFiles)
    }
  }

  const simulateUpload = (newFiles: UploadFile[]) => {
    newFiles.forEach(file => {
      setFiles(prev => prev.map(f => f.id === file.id ? { ...f, status: "uploading" } : f))
      
      let progress = 0
      const interval = setInterval(() => {
        progress += Math.random() * 30
        if (progress >= 100) {
          progress = 100
          clearInterval(interval)
          setFiles(prev => prev.map(f => f.id === file.id ? { ...f, progress: 100, status: "success" } : f))
        } else {
          setFiles(prev => prev.map(f => f.id === file.id ? { ...f, progress } : f))
        }
      }, 500)
    })
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-text">Resume Upload Center</h1>
        <p className="text-text-muted mt-2">Drag and drop candidate resumes. AURA AI will automatically parse, evaluate, and rank them.</p>
      </div>

      <Card className="bg-surface/30 backdrop-blur-md border-surface-border/50 shadow-2xl">
        <CardContent className="pt-6">
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`
              relative border-2 border-dashed rounded-xl p-16 text-center transition-all duration-200
              ${isDragging ? 'border-accent bg-accent/5 scale-[1.01] shadow-2xl shadow-accent/10' : 'border-surface-border/60 hover:bg-surface-hover/30 hover:border-surface-border'}
            `}
          >
            <input
              type="file"
              multiple
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              onChange={handleFileInput}
              accept=".pdf,.doc,.docx,.txt"
            />
            <div className="flex flex-col items-center justify-center space-y-4 pointer-events-none">
              <div className={`p-4 rounded-full bg-surface ${isDragging ? 'text-accent ambient-glow' : 'text-text-muted'}`}>
                <UploadCloud size={40} />
              </div>
              <div>
                <p className="text-lg font-semibold">Drop files here or click to browse</p>
                <p className="text-sm text-text-muted mt-1">Supports PDF, DOCX, TXT (Max 5MB)</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {files.length > 0 && (
        <Card className="bg-surface/30 backdrop-blur-md border-surface-border/50 shadow-2xl">
          <CardHeader>
            <CardTitle>Upload Queue</CardTitle>
            <CardDescription>Real-time processing status of your uploads.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <AnimatePresence>
                {files.map(file => (
                  <motion.div
                    key={file.id}
                    initial={{ opacity: 0, y: 10, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, height: 0, scale: 0.98 }}
                    transition={{ duration: 0.2 }}
                    className="flex items-center justify-between p-4 rounded-xl bg-surface-hover/30 border border-surface-border/50"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="p-2 bg-background rounded-md">
                        <FileText size={20} className="text-primary" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{file.name}</p>
                        <p className="text-xs text-text-muted capitalize">{file.status}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      {file.status === "uploading" && (
                        <div className="w-32">
                          <div className="h-2 w-full bg-background rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-accent transition-all duration-300"
                              style={{ width: `${file.progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                      
                      <div className="w-8 flex justify-end">
                        {file.status === "uploading" && <Loader2 className="animate-spin text-text-muted" size={20} />}
                        {file.status === "success" && <CheckCircle2 className="text-success" size={20} />}
                        {file.status === "error" && <XCircle className="text-danger" size={20} />}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
