'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Upload, MessageCircle, BookOpen, Brain, Download, FileText, Youtube, Send, Loader2, AlertCircle, History, Trash2, Home, Plus, X, Map, Lightbulb, FileSearch, Copy, Maximize2, Minimize2, Eye, Volume2, Zap, ZoomIn, ZoomOut } from 'lucide-react'
import * as api from '@/lib/api'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'
import dynamic from 'next/dynamic'
import MermaidChart from '@/components/MermaidChart'

// Set up PDF.js worker (ESM module worker)
pdfjs.GlobalWorkerOptions.workerSrc = `/pdf.worker.min.mjs`

interface SessionData {
  id?: string
  pages?: number
  chunks?: number
  title?: string
  type?: string
  documents?: any[]
  chat_history?: any[]
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sources?: any[]
}

interface DocumentHistory {
  id: string
  title: string
  type: 'pdf' | 'text' | 'youtube'
  date: string
  pages?: number
  preview?: string
}

function markdownToMermaid(md: string): string {
  // Strip markdown fences and empty lines
  const clean = md.replace(/```(?:markdown)?|```/g, '').trim()
  const lines = clean.split(/\r?\n/).filter((l) => l.trim().length > 0)
  if (lines.length === 0) return 'mindmap\n  (empty)'

  // Build a Mermaid mind-map that always has exactly one root node
  let output = 'mindmap\n'

  // Use the first non-empty line as the root
  const firstMatch = lines[0].match(/^(\s*)([\-*]?)\s*(.+)$/)
  const rootText = firstMatch ? firstMatch[3] : lines[0]
  output += `  ${rootText}\n`

  // Helper to compute indent level relative to original indent
  const baseIndent = firstMatch ? firstMatch[1].length : 0

  // Helper to sanitise each label so Mermaid parser doesn't choke on exotic markdown
  const cleanLabel = (raw: string) => {
    let txt = raw.trim()
    // Remove problematic characters that confuse Mermaid
    txt = txt.replace(/["()\[\]]/g, '')
    // Strip citation-like leading numbers e.g., '1.' or '1 ' or '1.' inside label
    txt = txt.replace(/^\d+\.?\s*/, '')
    // Collapse excessive whitespace
    txt = txt.replace(/\s+/g, ' ').trim()
    // If label still contains spaces or punctuation, wrap in quotes so Mermaid treats it as one token
    if (/[^A-Za-z0-9_-]/.test(txt)) {
      txt = `"${txt}"`
    }
    return txt || '(blank)'
  }

  for (let i = 1; i < lines.length; i++) {
    const match = lines[i].match(/^(\s*)([\-*]?)\s*(.+)$/)
    if (!match) continue
    // Skip reference section lines to avoid overwhelming diagram
    if (/^references?/i.test(match[3])) continue

    const indent = Math.max(0, match[1].length - baseIndent)
    const level = Math.floor(indent / 2) + 2 // +2 because root is already indented once
    output += '  '.repeat(level) + cleanLabel(match[3]) + '\n'
  }

  return output
}

export default function KenshoPage() {
  const [currentView, setCurrentView] = useState<'home' | 'workspace'>('home')
  const [sessionData, setSessionData] = useState<SessionData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)
  const [textInput, setTextInput] = useState('')
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [showTextModal, setShowTextModal] = useState(false)
  const [showYoutubeModal, setShowYoutubeModal] = useState(false)
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState<string | null>(null)
  const [selectedText, setSelectedText] = useState('')
  const [showTextActions, setShowTextActions] = useState(false)
  const [textActionPosition, setTextActionPosition] = useState({ x: 0, y: 0 })
  const [documentHistory, setDocumentHistory] = useState<DocumentHistory[]>([])
  const [activeWorkspaceTab, setActiveWorkspaceTab] = useState('chat')
  const [documentContent, setDocumentContent] = useState('')
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [summary, setSummary] = useState<string | null>(null)
  const [flashcards, setFlashcards] = useState<any[]>([])
  const [currentFlashcard, setCurrentFlashcard] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)
  const [quiz, setQuiz] = useState<any>(null)
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<{[key: number]: string}>({})
  const [showQuizResults, setShowQuizResults] = useState(false)
  const [exportSelections, setExportSelections] = useState<{[key:string]: boolean}>({
    summaries: true,
    chat: true,
    flashcards: false,
    quizzes: false,
    mindmap: false,
  })
  const [mindMap, setMindMap] = useState<string | null>(null)
  const [numPages, setNumPages] = useState<number | null>(null)
  const [pageNumber, setPageNumber] = useState(1)
  const [selectedPdfText, setSelectedPdfText] = useState('')
  const [textActionMenu, setTextActionMenu] = useState<{x: number, y: number, show: boolean}>({x: 0, y: 0, show: false})
  const [pdfLoading, setPdfLoading] = useState(false)
  const [pdfScale, setPdfScale] = useState(1.2)
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const documentRef = useRef<HTMLDivElement>(null)
  const shouldAutoScroll = useRef(true)

  // Progress overlay JSX element
  const progressOverlay = (loading && uploadProgress > 0 && uploadProgress < 100) ? (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-900 border border-slate-700 rounded-xl p-8 min-w-[300px]">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-white animate-spin" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Processing Document</h3>
          <p className="text-slate-400 mb-4">Please wait while we analyze your content...</p>
          <div className="w-full bg-slate-700 rounded-full h-2 mb-2">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300" style={{ width: `${uploadProgress}%` }}></div>
          </div>
          <p className="text-sm text-slate-400">{uploadProgress}% complete</p>
        </div>
      </div>
    </div>
  ) : null;

  useEffect(() => {
    initializeSession()
    loadDocumentHistory()
  }, [])

  useEffect(() => {
    return () => {
      if (pdfPreviewUrl) {
        URL.revokeObjectURL(pdfPreviewUrl)
      }
    }
  }, [pdfPreviewUrl])

   useEffect(() => {
     if (chatMessages.length === 0) return

       setTimeout(() => {
      if (chatContainerRef.current && shouldAutoScroll.current) {
           chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
         }
       }, 100)
  }, [chatMessages.length])

  const loadDocumentHistory = () => {
    const stored = localStorage.getItem('kensho-document-history')
    if (stored) {
      setDocumentHistory(JSON.parse(stored))
    }
  }

  const saveDocumentToHistory = (doc: DocumentHistory) => {
    const updated = [doc, ...documentHistory.filter(d => d.id !== doc.id)].slice(0, 10)
    setDocumentHistory(updated)
    localStorage.setItem('kensho-document-history', JSON.stringify(updated))
  }

  const deleteFromHistory = (id: string) => {
    const updated = documentHistory.filter(d => d.id !== id)
    setDocumentHistory(updated)
    localStorage.setItem('kensho-document-history', JSON.stringify(updated))
  }

  const handleDocumentTextSelection = () => {
    const selection = window.getSelection()
    if (selection && selection.toString().trim()) {
      const selectedText = selection.toString().trim()
      setSelectedText(selectedText)
      const range = selection.getRangeAt(0)
      const rect = range.getBoundingClientRect()
      setTextActionPosition({ 
        x: rect.left + rect.width / 2, 
        y: rect.top - 60 
      })
      setShowTextActions(true)
    } else {
      setShowTextActions(false)
    }
  }

  const initializeSession = async () => {
    try {
      const result = await api.createSession()
      setSessionData({ ...result.session, id: result.session_id })
    } catch (err) {
      setError('Failed to initialize session')
    }
  }

  const handleFileUpload = async (file: File) => {
    // Always start a fresh session for each new document
    let newSessionId: string | undefined
    try {
      const newSession = await api.createSession()
      newSessionId = newSession.session_id
      setSessionData({ ...newSession.session, id: newSessionId })
      // reset UI states for fresh session
      setChatMessages([])
      setSummary(null)
      setFlashcards([])
      setQuiz(null)
      setMindMap(null)
    } catch (err) {
      setError('Failed to start a new session')
      return
    }
    if (!newSessionId) return
    
    setLoading(true)
    setError(null)
    setUploadProgress(5)
    setPdfLoading(true)
    
    try {
      const objectUrl = URL.createObjectURL(file)
      setPdfPreviewUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev)
        return objectUrl
      })
      
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90))
      }, 200)
      
      const result = await api.uploadPDF(file, newSessionId)
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      const sessionInfo = await api.getSessionInfo(newSessionId)
      
      const newSessionData = {
        ...sessionData,
        ...sessionInfo.session,
        pages: sessionInfo.stats.pages,
        chunks: sessionInfo.stats.chunks,
        documents: sessionInfo.session.documents || []
      }
      
      setSessionData(newSessionData)
      
      const docHistoryItem: DocumentHistory = {
        id: newSessionId || 'unknown',
        title: file.name,
        type: 'pdf',
        date: new Date().toISOString(),
        pages: newSessionData.pages,
        preview: file.name
      }
      saveDocumentToHistory(docHistoryItem)
      
      setTimeout(() => {
        setUploadProgress(0)
        setCurrentView('workspace')
        setActiveWorkspaceTab('chat')
      }, 1000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleTextUpload = async () => {
    if (!textInput.trim()) return

    let newSessionId: string | undefined
    try {
      const newSession = await api.createSession()
      newSessionId = newSession.session_id
      setSessionData({ ...newSession.session, id: newSessionId })
      setChatMessages([])
      setSummary(null)
      setFlashcards([])
      setQuiz(null)
      setMindMap(null)
    } catch (err) {
      setError('Failed to start a new session')
      return
    }

    setPdfPreviewUrl(null)
    setDocumentContent('')
    setLoading(true)
    setError(null)
    setUploadProgress(5)
    
    try {
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 20, 90))
      }, 100)
      
      const result = await api.uploadText(textInput, newSessionId)
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      const sessionInfo = await api.getSessionInfo(newSessionId)
      setSessionData(prev => ({
        ...prev,
        ...sessionInfo.session,
        chunks: sessionInfo.stats.chunks,
        documents: sessionInfo.session.documents || []
      }))
      
      setDocumentContent(textInput)
      
      // Save to history
      const docHistoryItem: DocumentHistory = {
        id: newSessionId || 'unknown',
        title: textInput.slice(0, 30) + (textInput.length > 30 ? '...' : ''),
        type: 'text',
        date: new Date().toISOString(),
        pages: undefined,
        preview: undefined
      }
      saveDocumentToHistory(docHistoryItem)
      
      setTimeout(() => {
        setUploadProgress(0)
        setShowTextModal(false)
        setTextInput('')
        setCurrentView('workspace')
        setActiveWorkspaceTab('chat')
      }, 1000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Text upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleYoutubeUpload = async () => {
    if (!youtubeUrl.trim()) return

    let newSessionId: string | undefined
    try {
      const newSession = await api.createSession()
      newSessionId = newSession.session_id
      setSessionData({ ...newSession.session, id: newSessionId })
      setChatMessages([])
      setSummary(null)
      setFlashcards([])
      setQuiz(null)
      setMindMap(null)
    } catch (err) {
      setError('Failed to start a new session')
      return
    }

    setPdfPreviewUrl(null)
    setDocumentContent('')
    setLoading(true)
    setError(null)
    setUploadProgress(5)
    
    try {
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 5, 90))
      }, 500)
      
      const result = await api.uploadYouTube(youtubeUrl, newSessionId)
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      const sessionInfo = await api.getSessionInfo(newSessionId)
      
      setSessionData(prev => ({
        ...prev,
        ...sessionInfo.session,
        chunks: sessionInfo.stats.chunks,
        documents: sessionInfo.session.documents || []
      }))
      
      const docHistoryItem: DocumentHistory = {
        id: newSessionId || 'unknown',
        title: youtubeUrl,
        type: 'youtube',
        date: new Date().toISOString(),
        pages: undefined,
        preview: youtubeUrl
      }
      saveDocumentToHistory(docHistoryItem)
      
      // Show transcript in document viewer if returned
      if (result.transcript) {
        setDocumentContent(result.transcript as string)
      }
      
      setTimeout(() => {
        setUploadProgress(0)
        setShowYoutubeModal(false)
        setYoutubeUrl('')
        setCurrentView('workspace')
        setActiveWorkspaceTab('chat')
      }, 1000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'YouTube upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleChatSubmit = async () => {
    if (!chatInput.trim() || !sessionData?.id || loading) return
    
    const userMessage: ChatMessage = {
      role: 'user',
      content: chatInput,
      timestamp: new Date().toLocaleTimeString()
    }
    
    setChatMessages(prev => [...prev, userMessage])
    setChatInput('')
    setLoading(true)
    
    try {
      const assistantMessage: ChatMessage = {
        role: 'assistant', content: '', timestamp: new Date().toLocaleTimeString(), sources: []
      }
      setChatMessages(prev => [...prev, assistantMessage])

      await api.streamChatMessage(chatInput, sessionData.id, tok => {
        assistantMessage.content += tok
        setChatMessages(prev => [...prev])
      }).then((fullEntry) => {
        if (fullEntry && fullEntry.sources) {
          assistantMessage.sources = fullEntry.sources
          setChatMessages(prev => [...prev])
        }
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat failed')
    } finally {
      setLoading(false)
    }
  }

  const generateSummary = async (type: string) => {
    if (!sessionData?.id) return
    
    setLoading(true)
    setError(null)
    
    try {
      const result = await api.generateSummary(sessionData.id, type)
      setSummary(result.summary)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Summary generation failed')
    } finally {
      setLoading(false)
    }
  }

  const generateFlashcards = async (numCards: number) => {
    if (!sessionData?.id) return
    
    setLoading(true)
    setError(null)
    
    try {
      const result = await api.generateFlashcards(sessionData.id, numCards)
      setFlashcards(result.flashcards)
      setCurrentFlashcard(0)
      setShowAnswer(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Flashcard generation failed')
    } finally {
      setLoading(false)
    }
  }

  const generateQuiz = async (numQuestions: number = 5, difficulty: string = 'mixed') => {
    if (!sessionData?.id) return
    
    setLoading(true)
    setError(null)
    
    try {
      const result = await api.generateQuiz(sessionData.id, numQuestions, difficulty)
      setQuiz(result)
      setCurrentQuestion(0)
      setSelectedAnswers({})
      setShowQuizResults(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Quiz generation failed')
    } finally {
      setLoading(false)
    }
  }

  const generateMindMap = async () => {
    if (!sessionData?.id) return
    
    setLoading(true)
    setError(null)
    
    try {
      const result = await api.generateMindMap(sessionData.id)
      const mm = markdownToMermaid(result.mindmap)
      setMindMap(mm)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Mind map generation failed')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectedTextAction = async (action: string) => {
    if (!selectedPdfText || !sessionData?.id) return
    
    setTextActionMenu({x: 0, y: 0, show: false})
    
    const prompt = `${action} the following text: "${selectedPdfText}"`
    
    try {
      setLoading(true)

      // Push user prompt first
      setChatMessages(prev => [
        ...prev,
        { role: 'user', content: `${action}: "${selectedPdfText}"`, timestamp: new Date().toISOString(), sources: [] }
      ])

      const assistantMessage: ChatMessage = {
        role: 'assistant', content: '', timestamp: new Date().toISOString(), sources: []
      }
      setChatMessages(prev => [...prev, assistantMessage])

      await api.streamChatMessage(prompt, sessionData.id, tok => {
        assistantMessage.content += tok
        setChatMessages(prev => [...prev])
      }).then((fullEntry) => {
        if (fullEntry && fullEntry.sources) {
          assistantMessage.sources = fullEntry.sources
          setChatMessages(prev => [...prev])
        }
      })

      setActiveWorkspaceTab('chat')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process selected text')
    } finally {
      setLoading(false)
    }
  }

  const handleTextSelection = () => {
    const selection = window.getSelection()
    if (selection && selection.toString().length > 0) {
      const selectedText = selection.toString().trim()
      if (selectedText.length > 3) {
        setSelectedPdfText(selectedText)
        const range = selection.getRangeAt(0)
        const rect = range.getBoundingClientRect()
        setTextActionMenu({
          x: rect.left + rect.width / 2,
          y: rect.top - 10,
          show: true
        })
      }
    } else {
      setTextActionMenu({x: 0, y: 0, show: false})
    }
  }

  const handleExportDownload = async () => {
    if (!sessionData?.id || loading) return

    const selected = Object.entries(exportSelections)
      .filter(([, v]) => v)
      .map(([k]) => k)

    if (selected.length === 0) {
      setError('Select at least one category to export')
      return
    }

    try {
      setLoading(true)
      const blob = await api.exportSession(sessionData.id, selected)
      const url = window.URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = `kensho_session_${sessionData.id}.zip`
      document.body.appendChild(anchor)
      anchor.click()
      anchor.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed')
    } finally {
      setLoading(false)
    }
  }

  const renderDocumentViewer = () => {
    if (pdfPreviewUrl) {
      return (
        <div className="w-full h-full relative bg-white rounded-lg overflow-hidden" onMouseUp={handleTextSelection}>
          {pdfLoading && (
            <div className="absolute inset-0 bg-white/70 flex items-center justify-center z-20">
              <Loader2 className="h-10 w-10 text-blue-600 animate-spin" />
            </div>
          )}
          <Document
            file={pdfPreviewUrl}
            onLoadSuccess={({ numPages }) => { setNumPages(numPages); setPdfLoading(false); }}
            onLoadError={() => setPdfLoading(false)}
            loading={<div className="flex items-center justify-center h-full"><Loader2 className="h-8 w-8 animate-spin text-blue-600" /></div>}
            className="h-full"
          >
            <div className="h-full overflow-y-auto p-4">
              {numPages && Array.from(new Array(numPages), (el, index) => (
                <Page
                  key={`page_${index + 1}`}
                  pageNumber={index + 1}
                  className="mb-4 mx-auto"
                  scale={pdfScale}
                />
              ))}
            </div>
          </Document>
          
          {/* Text Selection Action Menu */}
          {textActionMenu.show && (
            <div 
              className="fixed z-50 bg-slate-800 border border-slate-600 rounded-lg shadow-lg p-2 flex gap-2"
              style={{
                left: `${textActionMenu.x - 150}px`,
                top: `${textActionMenu.y}px`,
                transform: 'translateX(50%)'
              }}
            >
              <Button
                size="sm"
                variant="ghost"
                onClick={() => handleSelectedTextAction('Explain')}
                className="text-xs text-white hover:bg-slate-700"
              >
                <Lightbulb className="h-3 w-3 mr-1" />
                Explain
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => handleSelectedTextAction('Summarize')}
                className="text-xs text-white hover:bg-slate-700"
              >
                <FileSearch className="h-3 w-3 mr-1" />
                Summarize
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => handleSelectedTextAction('Create mind map for')}
                className="text-xs text-white hover:bg-slate-700"
              >
                <Map className="h-3 w-3 mr-1" />
                Mind Map
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  navigator.clipboard.writeText(selectedPdfText)
                  setTextActionMenu({x: 0, y: 0, show: false})
                }}
                className="text-xs text-white hover:bg-slate-700"
              >
                <Copy className="h-3 w-3 mr-1" />
                Copy
              </Button>
              </div>
          )}

          {/* Zoom Controls */}
          <div className="absolute top-2 right-2 z-30 flex gap-2 bg-white/80 backdrop-blur-sm rounded-md p-1">
            <Button size="icon" variant="ghost" onClick={() => setPdfScale(prev => Math.max(0.5, prev - 0.1))} className="h-7 w-7 text-slate-800 hover:bg-slate-200">
              <ZoomOut className="h-4 w-4" />
            </Button>
            <Button size="icon" variant="ghost" onClick={() => setPdfScale(prev => Math.min(3, prev + 0.1))} className="h-7 w-7 text-slate-800 hover:bg-slate-200">
              <ZoomIn className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )
    }
    
    if (documentContent) {
      return (
        <div 
          ref={documentRef}
          className="w-full h-full p-6 overflow-y-auto bg-white text-gray-900 rounded-lg"
          onMouseUp={handleDocumentTextSelection}
          style={{ userSelect: 'text' }}
        >
          <div className="prose prose-lg max-w-none">
            {documentContent.split('\n').map((paragraph, index) => (
              <p key={index} className="mb-4 leading-relaxed">
                {paragraph}
              </p>
            ))}
              </div>
            </div>
      )
    }
    
    return (
      <div className="flex items-center justify-center h-full text-slate-400">
        <div className="text-center">
          <Upload className="h-16 w-16 mx-auto mb-4" />
          <p className="text-lg mb-2">No document loaded</p>
          <p className="text-sm">Upload a PDF or paste text to start</p>
                </div>
              </div>
    )
  }

  // Home View
  if (currentView === 'home') {
    return (
      <div className="min-h-screen bg-slate-950 text-white relative">
        {progressOverlay}
        <div className="container mx-auto px-6 py-8">
          <div className="text-center py-8">
            <h1 className="text-4xl font-bold text-white mb-4">
              <span className="bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                Kensho
              </span>
            </h1>
            <p className="text-slate-400 max-w-2xl mx-auto text-lg">
              Your AI-powered learning companion. Upload documents, analyze content, and enhance your understanding.
            </p>
          </div>

          {/* Quick Upload Section */}
          <div className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-xl p-8 mb-8">
            <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
              <Plus className="mr-2 h-5 w-5 text-blue-400" />
              Start Learning
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <button 
                onClick={() => fileInputRef.current?.click()}
                className="bg-slate-800/50 border-2 border-dashed border-slate-600 hover:border-blue-400 rounded-xl p-8 text-center transition-all hover:bg-slate-800/70"
              >
                <FileText className="h-12 w-12 text-blue-400 mx-auto mb-4" />
                <h4 className="font-medium text-white mb-2 text-lg">Upload PDF</h4>
                <p className="text-slate-400">Drag & drop or click to browse</p>
              </button>
              <button
                onClick={() => setShowTextModal(true)}
                className="bg-slate-800/50 border-2 border-dashed border-slate-600 hover:border-green-400 rounded-xl p-8 text-center transition-all hover:bg-slate-800/70"
              >
                <FileText className="h-12 w-12 text-green-400 mx-auto mb-4" />
                <h4 className="font-medium text-white mb-2 text-lg">Paste Text</h4>
                <p className="text-slate-400">Articles, notes, or any content</p>
              </button>
              <button
                onClick={() => setShowYoutubeModal(true)}
                className="bg-slate-800/50 border-2 border-dashed border-slate-600 hover:border-red-400 rounded-xl p-8 text-center transition-all hover:bg-slate-800/70"
              >
                <Youtube className="h-12 w-12 text-red-400 mx-auto mb-4" />
                <h4 className="font-medium text-white mb-2 text-lg">YouTube URL</h4>
                <p className="text-slate-400">Transcribe and analyze videos</p>
            </button>
          </div>
        </div>

          {/* Document History */}
          {documentHistory.length > 0 && (
            <div className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-xl p-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white flex items-center">
                  <History className="mr-2 h-5 w-5 text-purple-400" />
                  Recent Documents
                </h3>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => {
                    setDocumentHistory([])
                    localStorage.removeItem('kensho-document-history')
                  }}
                  className="border-slate-600 text-slate-400 hover:text-white"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear All
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {documentHistory.map((doc) => (
                  <div
                    key={doc.id}
                    className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 hover:bg-slate-800/70 transition-all cursor-pointer group"
                    onClick={() => {
                      setCurrentView('workspace')
                      setActiveWorkspaceTab('chat')
                    }}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center flex-1 min-w-0">
                        {doc.type === 'pdf' && <FileText className="h-5 w-5 text-blue-400 mr-2 flex-shrink-0" />}
                        {doc.type === 'youtube' && <Youtube className="h-5 w-5 text-red-400 mr-2 flex-shrink-0" />}
                        {doc.type === 'text' && <FileText className="h-5 w-5 text-green-400 mr-2 flex-shrink-0" />}
                        <span className="text-sm font-medium text-white truncate">
                          {doc.title}
                        </span>
                    </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteFromHistory(doc.id)
                        }}
                        className="text-slate-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                      >
                        <X className="h-4 w-4" />
                      </button>
                      </div>
                    <p className="text-xs text-slate-400 mb-2">
                      {new Date(doc.date).toLocaleDateString()}
                    </p>
                    {doc.pages && (
                      <p className="text-xs text-slate-500">
                        {doc.pages} pages
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
                </div>
                
        {/* Hidden file input */}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  className="hidden"
                  onChange={(e) => {
                    const file = e.target.files?.[0]
                    if (file) handleFileUpload(file)
                  }}
                />
                
        {/* Modals */}
        {showTextModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-2xl w-full p-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white">Add Text Content</h3>
                <button
                  onClick={() => setShowTextModal(false)}
                  className="text-slate-400 hover:text-white text-2xl"
                >
                  ×
                </button>
              </div>
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Paste your text content here..."
                className="w-full h-64 p-4 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 resize-none mb-6 focus:outline-none focus:border-blue-400"
              />
              <div className="flex gap-3 justify-end">
                  <Button 
                    variant="outline" 
                  onClick={() => setShowTextModal(false)}
                  className="border-slate-600 text-slate-400 hover:text-white"
                >
                  Cancel
                  </Button>
                  <Button 
                  onClick={handleTextUpload}
                  disabled={!textInput.trim() || loading}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <FileText className="mr-2 h-4 w-4" />
                  )}
                  Process Text
                  </Button>
                </div>
              </div>
                  </div>
        )}

        {showYoutubeModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-lg w-full p-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white">Add YouTube Video</h3>
                  <button
                  onClick={() => setShowYoutubeModal(false)}
                  className="text-slate-400 hover:text-white text-2xl"
                >
                  ×
                  </button>
              </div>
              <input
                type="url"
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="w-full p-4 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 mb-6 focus:outline-none focus:border-red-400"
              />
              <div className="flex gap-3 justify-end">
                <Button
                  variant="outline"
                  onClick={() => setShowYoutubeModal(false)}
                  className="border-slate-600 text-slate-400 hover:text-white"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleYoutubeUpload}
                  disabled={!youtubeUrl.trim() || loading}
                  className="bg-red-600 hover:bg-red-700"
                >
                  {loading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Youtube className="mr-2 h-4 w-4" />
                  )}
                  Process Video
                </Button>
                </div>
              </div>
            </div>
        )}
          </div>
    )
  }

  // Workspace View - Perfect 50/50 Split Screen Layout
  return (
    <div className="h-screen bg-slate-950 text-white flex flex-col overflow-hidden">
      {/* Top Header */}
      <div className="bg-slate-900/90 backdrop-blur border-b border-slate-800 px-6 py-3 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setCurrentView('home')}
              className="text-slate-400 hover:text-white"
            >
              <Home className="h-4 w-4 mr-2" />
              Home
            </Button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <span className="text-xl">🌌</span>
              </div>
              <div className="text-lg font-semibold text-white">
                Kensho Workspace
              </div>
            </div>
          </div>
          
          {/* Tab Navigation */}
          <div className="flex items-center gap-1">
            {[
              { id: 'chat', label: 'Chat', icon: MessageCircle },
              { id: 'summary', label: 'Summary', icon: BookOpen },
              { id: 'flashcards', label: 'Flashcards', icon: Brain },
              { id: 'quiz', label: 'Quiz', icon: FileText },
              { id: 'mindmap', label: 'Mind Map', icon: Map },
              { id: 'export', label: 'Export', icon: Download },
            ].map((tab) => (
              <Button 
                key={tab.id}
                variant={activeWorkspaceTab === tab.id ? "default" : "ghost"}
                size="sm"
                onClick={() => setActiveWorkspaceTab(tab.id)}
                className={`${
                  activeWorkspaceTab === tab.id 
                    ? 'bg-blue-600 text-white' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                <tab.icon className="h-4 w-4 mr-2" />
                {tab.label}
              </Button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <Button 
              variant="ghost"
              size="sm"
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="text-slate-400 hover:text-white"
            >
              {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content - Perfect 50/50 Split */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Document (Exactly 50%) */}
        {!isFullscreen && (
          <div className="w-1/2 border-r border-slate-800 bg-slate-900/30 overflow-hidden">
            <div className="h-full p-4">
              {renderDocumentViewer()}
            </div>
          </div>
        )}

        {/* Right Panel - Chat (Exactly 50%) */}
        <div className={`${isFullscreen ? 'w-full' : 'w-1/2'} bg-slate-950 overflow-hidden flex flex-col`}>
          {activeWorkspaceTab === 'chat' && (
            <div className="flex-1 flex flex-col overflow-hidden">
              {/* Chat Messages */}
              <div 
                ref={chatContainerRef}
                className="flex-1 overflow-y-auto p-6 space-y-4"
                onMouseUp={handleDocumentTextSelection}
              >
                {chatMessages.length === 0 ? (
                  <div className="flex items-center justify-center h-full text-slate-400">
                    <div className="text-center">
                      <MessageCircle className="h-16 w-16 mx-auto mb-4" />
                      <p className="text-lg mb-2">Start a conversation</p>
                      <p className="text-sm">Ask questions about your document</p>
                    </div>
                  </div>
                ) : (
                  chatMessages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[85%] p-4 rounded-2xl ${
                          message.role === 'user'
                            ? 'bg-blue-400/40 text-white'
                            : 'bg-slate-800 text-slate-100 border border-slate-700'
                        }`}
                      >
                        <div className="prose prose-invert prose-sm max-w-none">
                          <ReactMarkdown 
                            remarkPlugins={[remarkGfm]}
                            rehypePlugins={[rehypeHighlight]}
                          >
                            {message.content}
                          </ReactMarkdown>
                        </div>
                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-slate-600/30">
                            <div className="text-xs text-slate-400 mb-2 font-medium">Sources:</div>
                            <div className="flex flex-wrap gap-1">
                              {message.sources.map((source, idx) => (
                                <span key={idx} className="text-xs bg-blue-600/20 border border-blue-500/30 px-2 py-1 rounded text-blue-300">
                                  {source.page ? `Page ${source.page}` : `Source ${idx + 1}`}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        <div className="text-xs text-slate-400 mt-2">
                          {message.timestamp}
                        </div>
                      </div>
                    </div>
                  ))
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Chat Input */}
              <div className="border-t border-slate-800 p-4 flex-shrink-0">
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask a question about your document..."
                    className="flex-1 px-4 py-3 bg-slate-800 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-blue-400"
                    onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleChatSubmit())}
                    disabled={loading}
                  />
                  <Button 
                    onClick={handleChatSubmit}
                    disabled={!chatInput.trim() || loading}
                    className="px-4 py-3 bg-blue-600 hover:bg-blue-700 rounded-xl"
                  >
                    {loading ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <Send className="h-5 w-5" />
                    )}
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Summary Tab */}
          {activeWorkspaceTab === 'summary' && (
            <div className="flex-1 flex flex-col overflow-hidden p-6">
              <div className="flex items-center gap-4 mb-6">
                <h2 className="text-xl font-semibold text-white">📜 Summary Generation</h2>
                <div className="flex gap-2">
                  <Button 
                    variant="default"
                    size="sm"
                    onClick={() => generateSummary('comprehensive')}
                    disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                  >
                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    Comprehensive
                  </Button>
                  <Button 
                    variant="outline"
                    size="sm"
                    onClick={() => generateSummary('key_points')}
                    disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                  >
                    Key Points
                  </Button>
                  <Button 
                    variant="outline"
                    size="sm"
                    onClick={() => generateSummary('executive')}
                    disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                  >
                    Executive
                  </Button>
                </div>
              </div>
              
              <div className="flex-1 bg-slate-800/50 border border-slate-700 rounded-lg p-6 overflow-y-auto">
                {summary ? (
                  <div className="prose prose-invert max-w-none">
                    <ReactMarkdown 
                      remarkPlugins={[remarkGfm]}
                      rehypePlugins={[rehypeHighlight]}
                    >
                      {summary}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full text-slate-400">
                    <div className="text-center">
                      <BookOpen className="h-16 w-16 mx-auto mb-4" />
                      <p className="text-lg mb-2">Generate Summary</p>
                      <p className="text-sm">Select a summary type to begin</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Flashcards Tab */}
          {activeWorkspaceTab === 'flashcards' && (
            <div className="flex-1 flex flex-col overflow-hidden p-6">
              <div className="flex items-center gap-4 mb-6">
                <h2 className="text-xl font-semibold text-white">🧩 Flashcards</h2>
                <div className="flex gap-2 items-center">
                  <Button 
                    variant="default"
                    size="sm"
                    onClick={() => generateFlashcards(10)}
                    disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                  >
                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    Generate Cards
                  </Button>
                  <select 
                    className="px-3 py-1 bg-slate-800 border border-slate-600 rounded text-white text-sm"
                    onChange={(e) => generateFlashcards(parseInt(e.target.value))}
                    disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                  >
                    <option value="5">5 cards</option>
                    <option value="10">10 cards</option>
                    <option value="15">15 cards</option>
                  </select>
                  {flashcards.length > 0 && (
                    <span className="text-sm text-slate-400">
                      Card {currentFlashcard + 1} of {flashcards.length}
                    </span>
                  )}
                </div>
              </div>
              
              <div className="flex-1 flex items-center justify-center">
                {flashcards.length === 0 ? (
                  <div className="text-center text-slate-400">
                    <Brain className="h-16 w-16 mx-auto mb-4" />
                    <p className="text-lg mb-2">Generate Flashcards</p>
                    <p className="text-sm">Create study cards for better retention</p>
                  </div>
                ) : (
                  <div className="w-full max-w-lg">
                    <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 text-center min-h-[300px] flex flex-col justify-center">
                      <div className="text-lg font-semibold text-white mb-6">
                        {showAnswer ? '💡 Answer' : '❓ Question'}
                      </div>
                      <div className="prose prose-invert prose-lg max-w-none mb-8 text-center">
                        <div className="text-slate-200 leading-relaxed">
                          {showAnswer 
                            ? (flashcards[currentFlashcard]?.back || flashcards[currentFlashcard]?.answer || 'No answer available')
                            : (flashcards[currentFlashcard]?.front || flashcards[currentFlashcard]?.question || 'No question available')}
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        onClick={() => setShowAnswer(!showAnswer)}
                        className="mb-6"
                        size="lg"
                      >
                        {showAnswer ? 'Show Question' : 'Show Answer'}
                      </Button>
                    </div>
                    <div className="flex justify-between mt-4">
                      <Button
                        variant="ghost"
                        onClick={() => {
                          setCurrentFlashcard(Math.max(0, currentFlashcard - 1))
                          setShowAnswer(false)
                        }}
                        disabled={currentFlashcard === 0}
                      >
                        Previous
                      </Button>
                      <Button
                        variant="ghost"
                        onClick={() => {
                          setCurrentFlashcard(Math.min(flashcards.length - 1, currentFlashcard + 1))
                          setShowAnswer(false)
                        }}
                        disabled={currentFlashcard === flashcards.length - 1}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Quiz Tab */}
          {activeWorkspaceTab === 'quiz' && (
            <div className="flex-1 flex flex-col overflow-hidden p-6">
              <div className="flex items-center gap-4 mb-6">
                <h2 className="text-xl font-semibold text-white">📝 Quiz</h2>
                <div className="flex gap-3 items-center">
                  <label className="text-sm text-slate-300">Questions:</label>
                  <select
                    className="px-3 py-1 bg-slate-800 border border-slate-600 rounded text-white text-sm"
                    defaultValue={5}
                    onChange={(e) => setCurrentQuestion(0)}
                    id="numQuestionsSelect"
                  >
                    {[5,10].map(n => (
                      <option key={n} value={n}>{n}</option>
                    ))}
                  </select>
                  <label className="text-sm text-slate-300">Difficulty:</label>
                  <select
                    className="px-3 py-1 bg-slate-800 border border-slate-600 rounded text-white text-sm"
                    defaultValue="mixed"
                    id="difficultySelect"
                  >
                    {['easy','medium','hard','mixed'].map(d => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                  <Button 
                    variant="default"
                    size="sm"
                    onClick={() => {
                      const num = parseInt((document.getElementById('numQuestionsSelect') as HTMLSelectElement).value)
                      const diff = (document.getElementById('difficultySelect') as HTMLSelectElement).value
                      generateQuiz(num, diff)
                    }}
                    disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                  >
                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    Generate Quiz
                  </Button>
                </div>
              </div>
              
              <div className="flex-1 bg-slate-800/50 border border-slate-700 rounded-lg p-6 overflow-y-auto">
                {!quiz ? (
                  <div className="flex items-center justify-center h-full text-slate-400">
                    <div className="text-center">
                      <FileText className="h-16 w-16 mx-auto mb-4" />
                      <p className="text-lg mb-2">Generate Quiz</p>
                      <p className="text-sm">Test your understanding with AI-generated questions</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {!showQuizResults ? (
                      <>
                        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                          <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-white">
                              Question {currentQuestion + 1} of {quiz.questions?.length || 0}
                            </h3>
                          </div>
                          <div className="prose prose-invert max-w-none mb-6">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {String(quiz.questions?.[currentQuestion]?.question || '')}
                            </ReactMarkdown>
                          </div>
                          <div className="space-y-3">
                            {quiz.questions?.[currentQuestion]?.options?.map((option: string, idx: number) => (
                              <button
                                key={idx}
                                onClick={() => setSelectedAnswers(prev => ({ ...prev, [currentQuestion]: option }))}
                                className={`w-full p-4 text-left rounded-lg border transition-colors ${
                                  selectedAnswers[currentQuestion] === option
                                    ? 'bg-blue-900/30 border-blue-600/50 text-blue-200'
                                    : 'bg-slate-800/30 border-slate-600/30 hover:bg-slate-700/30 text-slate-300'
                                }`}
                              >
                                <span className="font-medium">{String.fromCharCode(65 + idx)}. </span>
                                {option}
                              </button>
                            ))}
                          </div>
                        </div>
                        <div className="flex justify-between">
                          <Button
                            variant="ghost"
                            onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                            disabled={currentQuestion === 0}
                          >
                            Previous
                          </Button>
                          {currentQuestion < (quiz.questions?.length || 0) - 1 ? (
                            <Button
                              variant="ghost"
                              onClick={() => setCurrentQuestion(currentQuestion + 1)}
                            >
                              Next
                            </Button>
                          ) : (
                            <Button
                              variant="default"
                              onClick={() => setShowQuizResults(true)}
                            >
                              Show Results
                            </Button>
                          )}
                        </div>
                      </>
                    ) : (
                      <div className="mt-6 bg-slate-800 border border-slate-700 rounded-lg p-6">
                        <h4 className="text-lg font-semibold text-white mb-4">Quiz Results</h4>
                        <div className="space-y-4">
                          {quiz.questions?.map((question: any, qIndex: number) => {
                            const userAnswer = selectedAnswers[qIndex]
                            const correctAnswer = question.correct_answer || question.answer
                            const isCorrect = userAnswer === correctAnswer
                            
                            return (
                              <div key={qIndex} className="bg-slate-900/50 rounded-lg p-4">
                                <div className="flex items-start gap-3 mb-3">
                                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold ${
                                    isCorrect ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                                  }`}>
                                    {isCorrect ? '✓' : '✗'}
                                  </div>
                                  <div className="flex-1">
                                    <p className="text-white font-medium mb-2">{question.question}</p>
                                    <div className="space-y-1 text-sm">
                                      <p className="text-slate-400">Your answer: <span className={isCorrect ? 'text-green-400' : 'text-red-400'}>{userAnswer || 'Not answered'}</span></p>
                                      {!isCorrect && (
                                        <p className="text-slate-400">Correct answer: <span className="text-green-400">{correctAnswer}</span></p>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )
                          })}
                        </div>
                        
                        <div className="mt-6 text-center">
                          <div className="inline-flex items-center gap-4 bg-slate-900/50 rounded-lg p-4">
                            <div className="text-2xl font-bold text-white">
                              {Math.round((Object.values(selectedAnswers).filter((answer, index) => 
                                answer === (quiz.questions?.[index]?.correct_answer || quiz.questions?.[index]?.answer)
                              ).length / (quiz.questions?.length || 1)) * 100)}%
                            </div>
                            <div className="text-slate-400">
                              {Object.values(selectedAnswers).filter((answer, index) => 
                                answer === (quiz.questions?.[index]?.correct_answer || quiz.questions?.[index]?.answer)
                              ).length} out of {quiz.questions?.length} correct
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex justify-center mt-6">
                          <Button
                            variant="outline"
                            onClick={() => {
                              setShowQuizResults(false)
                              setCurrentQuestion(0)
                              setSelectedAnswers({})
                            }}
                          >
                            Take Quiz Again
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Mind Map Tab */}
          {activeWorkspaceTab === 'mindmap' && (
            <div className="flex-1 flex flex-col overflow-hidden p-6">
              <div className="flex items-center gap-4 mb-6">
                <h2 className="text-xl font-semibold text-white">🗺️ Mind Map</h2>
                <Button 
                  variant="default"
                  size="sm"
                  onClick={generateMindMap}
                  disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                >
                  {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                  Generate Mind Map
                </Button>
              </div>

              <div className="flex-1 bg-slate-800/50 border border-slate-700 rounded-lg p-6 overflow-y-auto">
                {mindMap ? (
                  <MermaidChart chart={mindMap} />
                ) : (
                  <div className="flex items-center justify-center h-full text-slate-400">
                    <div className="text-center">
                      <Map className="h-16 w-16 mx-auto mb-4" />
                      <p className="text-lg mb-2">Generate Mind Map</p>
                      <p className="text-sm">Create a visual representation of key concepts</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Export Tab */}
          {activeWorkspaceTab === 'export' && (
            <div className="flex-1 flex flex-col overflow-hidden p-6">
              <h2 className="text-xl font-semibold text-white mb-6">📁 Export Session</h2>
              
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
                <h3 className="font-medium text-white mb-4">Choose what to include</h3>
                <div className="space-y-3 mb-6">
                  {[
                    { key: 'summaries', label: 'Summaries' },
                    { key: 'chat', label: 'Chat History' },
                    { key: 'flashcards', label: 'Flashcards' },
                    { key: 'quizzes', label: 'Quiz Results' },
                    { key: 'mindmap', label: 'Mind Map' },
                  ].map((opt) => (
                    <label key={opt.key} className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={exportSelections[opt.key]}
                        onChange={(e) =>
                          setExportSelections((prev) => ({ ...prev, [opt.key]: e.target.checked }))
                        }
                        className="rounded bg-slate-700 border-slate-600"
                      />
                      <span className="text-slate-300">{opt.label}</span>
                    </label>
                  ))}
                </div>
                <div className="flex justify-end">
                  <Button
                    onClick={handleExportDownload}
                    disabled={loading || !(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0))}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    {loading && !uploadProgress ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}
                    Download ZIP
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Text Selection Actions Popup */}
      {showTextActions && selectedText && (
        <div 
          className="fixed z-50 bg-slate-800/95 backdrop-blur-sm border border-slate-600/50 rounded-lg p-2 shadow-xl"
          style={{ 
            left: Math.max(10, Math.min(window.innerWidth - 320, textActionPosition.x - 160)), 
            top: Math.max(10, textActionPosition.y - 60),
          }}
        >
          <div className="flex gap-1">
            <Button
              size="sm" 
              variant="ghost"
              onClick={() => {
                navigator.clipboard.writeText(selectedText)
                setShowTextActions(false)
              }}
              className="text-xs hover:bg-slate-700"
            >
              <Copy className="h-3 w-3 mr-1" />
              Copy
            </Button>
            <Button
              size="sm" 
              variant="ghost"
              onClick={() => {
                setChatInput(`Explain this: "${selectedText}"`)
                setShowTextActions(false)
                setActiveWorkspaceTab('chat')
              }}
              className="text-xs hover:bg-slate-700"
            >
              <Lightbulb className="h-3 w-3 mr-1" />
              Explain
            </Button>
            <Button 
              size="sm" 
              variant="ghost"
              onClick={() => {
                setChatInput(`Summarize this: "${selectedText}"`)
                setShowTextActions(false)
                setActiveWorkspaceTab('chat')
              }}
              className="text-xs hover:bg-slate-700"
            >
              <FileSearch className="h-3 w-3 mr-1" />
              Summarize
            </Button>
            <Button
              size="sm" 
              variant="ghost"
              onClick={() => {
                setChatInput(`Create a mind map for: "${selectedText}"`)
                setShowTextActions(false)
                setActiveWorkspaceTab('chat')
              }}
              className="text-xs hover:bg-slate-700"
            >
              <Map className="h-3 w-3 mr-1" />
              Mind Map
            </Button>
            <Button
              size="sm" 
              variant="ghost"
              onClick={() => setShowTextActions(false)}
              className="text-xs text-slate-400 hover:bg-slate-700"
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="fixed top-4 right-4 bg-red-900/90 border border-red-500/50 rounded-lg p-4 flex items-center z-50">
          <AlertCircle className="w-5 h-5 text-red-400 mr-3" />
          <span className="text-red-300">{error}</span>
          <button 
            onClick={() => setError(null)}
            className="ml-auto text-red-400 hover:text-red-300 ml-4"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  )
}