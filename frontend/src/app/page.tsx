'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Upload, MessageCircle, BookOpen, Brain, Download, FileText, Youtube, Mic, Send, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import * as api from '@/lib/api'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'

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

export default function KenshoPage() {
  const [activeTab, setActiveTab] = useState('upload')
  const [sessionData, setSessionData] = useState<SessionData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)
  const [summary, setSummary] = useState<string | null>(null)
  const [flashcards, setFlashcards] = useState<any[]>([])
  const [currentFlashcard, setCurrentFlashcard] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)
  const [quiz, setQuiz] = useState<any>(null)
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<{[key: number]: string}>({})
  const [showQuizResults, setShowQuizResults] = useState(false)
  const [textInput, setTextInput] = useState('')
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [showTextModal, setShowTextModal] = useState(false)
  const [showYoutubeModal, setShowYoutubeModal] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const shouldAutoScroll = useRef(true) // Track if we should auto-scroll
  const scrollTimer = useRef<NodeJS.Timeout | null>(null) // Track scrolling timer

  useEffect(() => {
    initializeSession()
  }, [])

  // Handle scroll detection
  useEffect(() => {
    const container = chatContainerRef.current
    if (!container) return

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container
      const isAtBottom = Math.abs(scrollHeight - scrollTop - clientHeight) < 3
      
      // Update auto-scroll preference based on user position
      shouldAutoScroll.current = isAtBottom
      
      // Clear the scroll timer
      if (scrollTimer.current) {
        clearTimeout(scrollTimer.current)
      }
      scrollTimer.current = setTimeout(() => {
        scrollTimer.current = null
      }, 150)
    }

    container.addEventListener('scroll', handleScroll)
    return () => container.removeEventListener('scroll', handleScroll)
  }, [])

     // Handle auto-scroll for new messages
   useEffect(() => {
     if (chatMessages.length === 0) return

     // Always scroll for the first message or if user was at bottom
     const isFirstMessage = chatMessages.length === 1
     
     if (isFirstMessage || (shouldAutoScroll.current && !scrollTimer.current)) {
       // Small delay to ensure DOM is updated
       setTimeout(() => {
         if (chatContainerRef.current) {
           // Scroll the chat container to bottom, not the entire page
           chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
         }
       }, 100)
     }
   }, [chatMessages.length]) // Only trigger on message count change

  const initializeSession = async () => {
    try {
      const result = await api.createSession()
      setSessionData({ ...result.session, id: result.session_id })
      console.log('Session initialized:', result.session)
    } catch (err) {
      setError('Failed to initialize session')
    }
  }

  const handleFileUpload = async (file: File) => {
    if (!sessionData?.id) return
    
    console.log('📄 Starting PDF upload:', file.name, 'Session ID:', sessionData.id)
    setLoading(true)
    setError(null)
    setUploadProgress(0)
    
    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90))
      }, 200)
      
      console.log('📄 Calling API uploadPDF...')
      const result = await api.uploadPDF(file, sessionData.id)
      console.log('📄 Upload result:', result)
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      // Update session data
      console.log('📄 Fetching updated session info...')
      const sessionInfo = await api.getSessionInfo(sessionData.id)
      console.log('📄 Session info after upload:', sessionInfo)
      
      const newSessionData = {
        ...sessionData,
        ...sessionInfo.session,
        pages: sessionInfo.stats.pages,
        chunks: sessionInfo.stats.chunks,
        documents: sessionInfo.session.documents || []
      }
      console.log('📄 Updated session data:', newSessionData)
      console.log('📄 Documents count:', newSessionData.documents?.length)
      console.log('📄 Pages:', newSessionData.pages)
      console.log('📄 Chunks:', newSessionData.chunks)
      
      setSessionData(newSessionData)
      
      setTimeout(() => {
        setUploadProgress(0)
        setActiveTab('summary')
      }, 1000)
    } catch (err) {
      console.error('❌ PDF upload error:', err)
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleTextUpload = async () => {
    if (!textInput.trim() || !sessionData?.id) return
    
    setLoading(true)
    setError(null)
    setUploadProgress(0)
    
    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 20, 90))
      }, 100)
      
      const result = await api.uploadText(textInput, sessionData.id)
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      // Update session data
      const sessionInfo = await api.getSessionInfo(sessionData.id)
      setSessionData(prev => ({
        ...prev,
        ...sessionInfo.session,
        chunks: sessionInfo.stats.chunks,
        documents: sessionInfo.session.documents || []
      }))
      
      setTimeout(() => {
        setUploadProgress(0)
        setShowTextModal(false)
        setTextInput('')
        setActiveTab('summary')
      }, 1000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Text upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleYoutubeUpload = async () => {
    if (!youtubeUrl.trim() || !sessionData?.id) return
    
    console.log('🎥 Starting YouTube upload:', youtubeUrl)
    setLoading(true)
    setError(null)
    setUploadProgress(0)
    
    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 5, 90))
      }, 500)
      
      console.log('🎥 Calling API uploadYouTube...')
      const result = await api.uploadYouTube(youtubeUrl, sessionData.id)
      console.log('🎥 Upload result:', result)
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      // Update session data
      console.log('🎥 Fetching updated session info...')
      const sessionInfo = await api.getSessionInfo(sessionData.id)
      console.log('🎥 Session info after YouTube upload:', sessionInfo)
      
      setSessionData(prev => ({
        ...prev,
        ...sessionInfo.session,
        chunks: sessionInfo.stats.chunks,
        documents: sessionInfo.session.documents || []
      }))
      
      setTimeout(() => {
        setUploadProgress(0)
        setShowYoutubeModal(false)
        setYoutubeUrl('')
        setActiveTab('summary')
      }, 1000)
    } catch (err) {
      console.error('❌ YouTube upload error:', err)
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
      const response = await api.sendChatMessage(chatInput, sessionData.id)
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toLocaleTimeString(),
        sources: response.sources
      }
      setChatMessages(prev => [...prev, assistantMessage])
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

  return (
    <div className="min-h-screen relative">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 kensho-header-glow rounded-full"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 kensho-header-glow rounded-full"></div>
      </div>
      
      {/* Header */}
      <header className="relative overflow-hidden border-b border-white/10 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-6 relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
                <span className="text-3xl">🌌</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold">
                  <span className="kensho-gradient-text">Kensho</span>
                </h1>
                <p className="text-slate-400 text-sm font-medium">
                  AI-Powered Learning Platform
                </p>
              </div>
            </div>
            {sessionData?.id && (
              <div className="flex items-center space-x-3">
                <div className="text-right">
                  <div className="text-sm text-slate-300 font-medium">Session Active</div>
                  <div className="text-xs text-slate-500">Ready for learning</div>
                </div>
                <div className="kensho-status-indicator kensho-status-connected"></div>
              </div>
            )}
          </div>
        </div>
      </header>

      {error && (
        <div className="container mx-auto px-6 py-4">
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 flex items-center">
            <AlertCircle className="w-5 h-5 text-red-400 mr-3" />
            <span className="text-red-300">{error}</span>
            <button 
              onClick={() => setError(null)}
              className="ml-auto text-red-400 hover:text-red-300"
            >
              ×
            </button>
          </div>
        </div>
      )}

      <div className="container mx-auto px-6 py-8 pb-12 kensho-main-container">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 relative">
          {/* Left Sidebar - Upload and Navigation */}
          <div className="lg:col-span-1">
            <div className="kensho-card sticky top-6 p-6">
              <div className="flex items-center justify-center mb-6">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center mr-3">
                  <Upload className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-slate-200">
                  Knowledge Hub
                </h3>
              </div>
              
              {/* Upload Section */}
              <div className="space-y-4 mb-8">
                <div 
                  className="kensho-upload-zone rounded-xl p-8 text-center cursor-pointer"
                  onClick={() => fileInputRef.current?.click()}
                  onDrop={(e) => {
                    e.preventDefault()
                    const files = Array.from(e.dataTransfer.files)
                    const pdfFile = files.find(f => f.type === 'application/pdf')
                    if (pdfFile) handleFileUpload(pdfFile)
                  }}
                  onDragOver={(e) => e.preventDefault()}
                >
                  <div className="relative z-10">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-indigo-500/20 to-purple-600/20 flex items-center justify-center">
                      <Upload className="w-8 h-8 text-indigo-400" />
                    </div>
                    <p className="text-sm text-slate-300 mb-4 font-medium">
                      {uploadProgress > 0 ? `Uploading... ${uploadProgress}%` : 'Drop PDF files here or click to browse'}
                    </p>
                    {uploadProgress > 0 && (
                      <div className="kensho-progress-bar w-full h-2 mb-4">
                        <div 
                          className="kensho-progress-fill h-full rounded-full"
                          style={{ width: `${uploadProgress}%` }}
                        ></div>
                      </div>
                    )}
                    <Button variant="zen" size="sm" className="w-full" disabled={loading}>
                      {loading ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <FileText className="mr-2 h-4 w-4" />
                      )}
                      Upload PDF
                    </Button>
                  </div>
                </div>
                
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
                
                <div className="grid grid-cols-2 gap-3">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full" 
                    disabled={!sessionData?.id || loading}
                    onClick={() => setShowYoutubeModal(true)}
                  >
                    <Youtube className="mr-2 h-4 w-4" />
                    YouTube
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full" 
                    disabled={!sessionData?.id || loading}
                    onClick={() => setShowTextModal(true)}
                  >
                    <FileText className="mr-2 h-4 w-4" />
                    Text
                  </Button>
                </div>
              </div>

              {/* Navigation */}
              <div className="space-y-3">
                <div className="flex items-center mb-4">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center mr-3">
                    <Brain className="w-4 h-4 text-white" />
                  </div>
                  <h4 className="text-sm font-semibold text-slate-200">Learning Modes</h4>
                </div>
                {[
                  { id: 'summary', label: 'Summary', icon: BookOpen },
                  { id: 'chat', label: 'Chat', icon: MessageCircle },
                  { id: 'flashcards', label: 'Flashcards', icon: Brain },
                  { id: 'quiz', label: 'Quiz', icon: FileText },
                  { id: 'export', label: 'Export', icon: Download },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`kensho-nav-item w-full flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                      activeTab === tab.id ? 'active' : ''
                    }`}
                  >
                    <tab.icon className="mr-3 h-4 w-4" />
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Session Info */}
              <div className="mt-8 p-4 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10">
                <div className="flex items-center mb-3">
                  <div className="w-6 h-6 rounded-md bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center mr-2">
                    <CheckCircle className="w-3 h-3 text-white" />
                  </div>
                  <h4 className="text-sm font-semibold text-slate-200">Session Status</h4>
                </div>
                <div className="text-xs space-y-2">
                  {sessionData ? (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Status</span>
                        <div className="flex items-center text-emerald-400">
                          <div className="kensho-status-indicator kensho-status-connected mr-2"></div>
                          <span className="font-medium">Active</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Pages</span>
                        <span className="text-slate-300 font-medium">{sessionData.pages || '0'}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Chunks</span>
                        <span className="text-slate-300 font-medium">{sessionData.chunks || '0'}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Documents</span>
                        <span className="text-slate-300 font-medium">{sessionData.documents?.length || (sessionData.pages && sessionData.pages > 0) ? '1' : '0'}</span>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Status</span>
                      <div className="flex items-center text-slate-500">
                        <div className="kensho-status-indicator kensho-status-disconnected mr-2"></div>
                        <span>No document</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-3">
            <div className="kensho-card min-h-[700px] p-8">
              {activeTab === 'upload' && (
                <div className="text-center py-16">
                  <div className="animate-pulse-glow inline-block p-8 rounded-full bg-gradient-to-r from-indigo-500/10 to-purple-600/10 mb-8">
                    <Upload className="h-20 w-20 text-indigo-400" />
                  </div>
                  <h2 className="text-3xl font-bold text-slate-200 mb-4">
                    Begin Your Learning Journey
                  </h2>
                  <p className="text-slate-400 max-w-lg mx-auto mb-12 text-lg">
                    Upload a document, paste text, or provide a YouTube URL to start your AI-powered learning experience.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                    <div className="kensho-card p-8 text-center hover:scale-105 transition-all cursor-pointer group">
                      <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <FileText className="h-8 w-8 text-blue-400" />
                      </div>
                      <h3 className="font-semibold text-slate-200 mb-3 text-lg">PDF Documents</h3>
                      <p className="text-sm text-slate-400 leading-relaxed">Upload and analyze PDF files with intelligent page-aware citations and context</p>
                    </div>
                    <div className="kensho-card p-8 text-center hover:scale-105 transition-all cursor-pointer group">
                      <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-red-500/20 to-orange-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Youtube className="h-8 w-8 text-red-400" />
                      </div>
                      <h3 className="font-semibold text-slate-200 mb-3 text-lg">YouTube Videos</h3>
                      <p className="text-sm text-slate-400 leading-relaxed">Transcribe and learn from video content with AI-powered insights</p>
                    </div>
                    <div className="kensho-card p-8 text-center hover:scale-105 transition-all cursor-pointer group">
                      <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <FileText className="h-8 w-8 text-green-400" />
                      </div>
                      <h3 className="font-semibold text-slate-200 mb-3 text-lg">Text Input</h3>
                      <p className="text-sm text-slate-400 leading-relaxed">Paste articles, notes, or any text content for instant analysis</p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'summary' && (
                <div>
                  <h2 className="text-2xl font-light text-slate-200 mb-6">📜 Summary Generation</h2>
                  <div className="space-y-6">
                    <div className="flex gap-4 flex-wrap">
                      <Button 
                        variant="default" 
                        onClick={() => generateSummary('comprehensive')}
                        disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                      >
                        {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                        Comprehensive
                      </Button>
                      <Button 
                        variant="outline"
                        onClick={() => generateSummary('key_points')}
                        disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                      >
                        Key Points
                      </Button>
                      <Button 
                        variant="outline"
                        onClick={() => generateSummary('executive')}
                        disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                      >
                        Executive
                      </Button>
                    </div>
                    <div className="kensho-card bg-slate-900/30 min-h-[400px] p-6">
                      {!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) ? (
                        <div className="text-center py-20">
                          <Upload className="h-16 w-16 text-slate-500 mx-auto mb-4" />
                          <p className="text-slate-400 mb-4">Upload a document to generate summaries</p>
                          <div className="flex gap-3 justify-center">
                            <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
                              <FileText className="mr-2 h-4 w-4" />
                              Upload PDF
                            </Button>
                            <Button variant="outline" onClick={() => setShowTextModal(true)}>
                              <FileText className="mr-2 h-4 w-4" />
                              Add Text
                            </Button>
                            <Button variant="outline" onClick={() => setShowYoutubeModal(true)}>
                              <Youtube className="mr-2 h-4 w-4" />
                              YouTube
                            </Button>
                          </div>
                        </div>
                      ) : summary ? (
                        <div className="prose prose-invert max-w-none">
                          <ReactMarkdown 
                            remarkPlugins={[remarkGfm]}
                            rehypePlugins={[rehypeHighlight]}
                          >
                            {summary}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <div className="text-center py-20">
                          <BookOpen className="h-16 w-16 text-blue-400 mx-auto mb-4" />
                          <p className="text-slate-400 mb-4">Select a summary type to begin</p>
                          <p className="text-sm text-slate-500">
                            Document loaded: {sessionData.documents?.length || (sessionData.pages && sessionData.pages > 0 ? 1 : 0)} file(s)
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'chat' && (
                <div>
                  <h2 className="text-2xl font-light text-slate-200 mb-6">💬 Interactive Chat</h2>
                  <div className="space-y-4">
                    <div ref={chatContainerRef} className="kensho-card bg-slate-900/30 min-h-[400px] max-h-[500px] p-6 overflow-y-auto">
                      {!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) ? (
                        <div className="text-center py-20">
                          <MessageCircle className="h-16 w-16 text-slate-500 mx-auto mb-4" />
                          <p className="text-slate-400 mb-4">Upload a document to start chatting</p>
                          <div className="flex gap-3 justify-center">
                            <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
                              <FileText className="mr-2 h-4 w-4" />
                              Upload PDF
                            </Button>
                            <Button variant="outline" onClick={() => setShowTextModal(true)}>
                              <FileText className="mr-2 h-4 w-4" />
                              Add Text
                            </Button>
                            <Button variant="outline" onClick={() => setShowYoutubeModal(true)}>
                              <Youtube className="mr-2 h-4 w-4" />
                              YouTube
                            </Button>
                          </div>
                        </div>
                      ) : chatMessages.length === 0 ? (
                        <div className="text-center py-20">
                          <MessageCircle className="h-16 w-16 text-blue-400 mx-auto mb-4" />
                          <p className="text-slate-400 mb-4">Start a conversation about your uploaded content</p>
                          <p className="text-sm text-slate-500">
                            Ask questions, request explanations, or explore topics
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {chatMessages.map((message, index) => (
                            <div
                              key={index}
                              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                              <div
                                className={`max-w-[80%] p-4 rounded-xl ${
                                  message.role === 'user'
                                    ? 'kensho-chat-message-user'
                                    : 'kensho-chat-message-assistant'
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
                                    <div className="text-xs text-slate-400 mb-2 font-medium">📚 Sources:</div>
                                    <div className="flex flex-wrap gap-2">
                                      {message.sources.map((source, idx) => (
                                        <div key={idx} className="text-xs bg-slate-700/50 px-2 py-1 rounded-md text-slate-300">
                                          {source.page ? `Page ${source.page}` : 'Document'}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                <div className="text-xs text-slate-500 mt-2">
                                  {message.timestamp}
                                </div>
                              </div>
                            </div>
                          ))}
                          <div ref={chatEndRef} />
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        placeholder="Ask a question about your document..."
                        className="kensho-input flex-1 px-4 py-3 rounded-xl text-slate-100 placeholder:text-slate-400 focus:outline-none"
                        onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleChatSubmit())}
                        disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                      />
                      <Button 
                        onClick={handleChatSubmit}
                        disabled={!chatInput.trim() || !(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                      >
                        {loading ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Send className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'flashcards' && (
                <div>
                  <h2 className="text-2xl font-light text-slate-200 mb-6">🧩 Flashcards</h2>
                  <div className="space-y-6">
                    <div className="flex gap-4 flex-wrap items-center">
                      <Button 
                        variant="default"
                        onClick={() => generateFlashcards(10)}
                        disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                      >
                        {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                        Generate Cards
                      </Button>
                      <select 
                        className="px-4 py-2 bg-slate-800/60 border border-slate-600/50 rounded-lg text-slate-100"
                        onChange={(e) => generateFlashcards(parseInt(e.target.value))}
                        disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                      >
                        <option value="5">5 cards</option>
                        <option value="10">10 cards</option>
                        <option value="15">15 cards</option>
                      </select>
                      {flashcards.length > 0 && (
                        <div className="text-sm text-slate-400">
                          Card {currentFlashcard + 1} of {flashcards.length}
                        </div>
                      )}
                    </div>
                    <div className="kensho-card bg-slate-900/30 min-h-[400px] p-6">
                      {!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) ? (
                        <div className="text-center py-20">
                          <Brain className="h-16 w-16 text-slate-500 mx-auto mb-4" />
                          <p className="text-slate-400 mb-4">Upload a document to generate flashcards</p>
                          <div className="flex gap-3 justify-center">
                            <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
                              <FileText className="mr-2 h-4 w-4" />
                              Upload PDF
                            </Button>
                            <Button variant="outline" onClick={() => setShowTextModal(true)}>
                              <FileText className="mr-2 h-4 w-4" />
                              Add Text
                            </Button>
                            <Button variant="outline" onClick={() => setShowYoutubeModal(true)}>
                              <Youtube className="mr-2 h-4 w-4" />
                              YouTube
                            </Button>
                          </div>
                        </div>
                      ) : flashcards.length === 0 ? (
                        <div className="text-center py-20">
                          <Brain className="h-16 w-16 text-blue-400 mx-auto mb-4" />
                          <p className="text-slate-400 mb-4">Generate flashcards based on Bloom's taxonomy levels</p>
                          <p className="text-sm text-slate-500">
                            Create study cards for better retention and understanding
                          </p>
                        </div>
                      ) : (
                        <div className="flex flex-col items-center justify-center h-full">
                          <div className="w-full max-w-lg">
                            <div className="kensho-flashcard rounded-2xl p-10 text-center min-h-[300px] flex flex-col justify-center">
                              <div className="text-xl font-semibold text-slate-200 mb-6">
                                {showAnswer ? '💡 Answer' : '❓ Question'}
                              </div>
                              <div className="prose prose-invert prose-lg max-w-none mb-8 text-center">
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                  {String(showAnswer 
                                    ? flashcards[currentFlashcard]?.answer 
                                    : flashcards[currentFlashcard]?.question)}
                                </ReactMarkdown>
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
                                variant="secondary"
                                onClick={() => {
                                  setCurrentFlashcard(Math.max(0, currentFlashcard - 1))
                                  setShowAnswer(false)
                                }}
                                disabled={currentFlashcard === 0}
                              >
                                Previous
                              </Button>
                              <Button
                                variant="secondary"
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
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'quiz' && (
                <div>
                  <h2 className="text-2xl font-light text-slate-200 mb-6">📝 Quiz</h2>
                  <div className="space-y-6">
                    <div className="flex gap-4 flex-wrap items-center">
                      <Button 
                        variant="default"
                        onClick={() => generateQuiz(5, 'mixed')}
                        disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                      >
                        {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                        Generate Quiz
                      </Button>
                      <select 
                        className="px-4 py-2 bg-slate-800/60 border border-slate-600/50 rounded-lg text-slate-100"
                        onChange={(e) => generateQuiz(5, e.target.value)}
                        disabled={!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) || loading}
                      >
                        <option value="mixed">Mixed</option>
                        <option value="easy">Easy</option>
                        <option value="medium">Medium</option>
                        <option value="hard">Hard</option>
                      </select>
                      {quiz && (
                        <div className="text-sm text-slate-400">
                          Question {currentQuestion + 1} of {quiz.questions?.length || 0}
                        </div>
                      )}
                    </div>
                    <div className="kensho-card bg-slate-900/30 min-h-[400px] p-6">
                      {!(sessionData?.documents?.length || (sessionData?.pages && sessionData.pages > 0)) ? (
                        <div className="text-center py-20">
                          <Brain className="h-16 w-16 text-slate-500 mx-auto mb-4" />
                          <p className="text-slate-400 mb-4">Upload a document to generate quiz questions</p>
                          <div className="flex gap-3 justify-center">
                            <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
                              <FileText className="mr-2 h-4 w-4" />
                              Upload PDF
                            </Button>
                            <Button variant="outline" onClick={() => setShowTextModal(true)}>
                              <FileText className="mr-2 h-4 w-4" />
                              Add Text
                            </Button>
                            <Button variant="outline" onClick={() => setShowYoutubeModal(true)}>
                              <Youtube className="mr-2 h-4 w-4" />
                              YouTube
                            </Button>
                          </div>
                        </div>
                      ) : !quiz ? (
                        <div className="text-center py-20">
                          <Brain className="h-16 w-16 text-blue-400 mx-auto mb-4" />
                          <p className="text-slate-400 mb-4">Generate quiz questions to test your knowledge</p>
                          <p className="text-sm text-slate-500">
                            Create questions with multiple difficulty levels
                          </p>
                        </div>
                      ) : showQuizResults ? (
                        <div className="space-y-6">
                          <h3 className="text-xl font-semibold text-slate-200 text-center">📊 Quiz Results</h3>
                          <div className="grid gap-4">
                            {quiz.questions?.map((question: any, idx: number) => (
                              <div key={idx} className="kensho-card bg-slate-800/30 p-4">
                                <div className="prose prose-invert prose-sm max-w-none mb-3">
                                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                    {`**Question ${idx + 1}:** ${question.question}`}
                                  </ReactMarkdown>
                                </div>
                                <div className="space-y-2">
                                  <div className={`p-2 rounded ${selectedAnswers[idx] === question.correct_answer ? 'bg-green-900/30 border border-green-600/50' : 'bg-red-900/30 border border-red-600/50'}`}>
                                    <span className="text-sm font-medium">Your answer: </span>
                                    <span>{selectedAnswers[idx] || 'Not answered'}</span>
                                  </div>
                                  <div className="p-2 rounded bg-green-900/20 border border-green-600/30">
                                    <span className="text-sm font-medium text-green-400">Correct answer: </span>
                                    <span className="text-green-300">{question.correct_answer}</span>
                                  </div>
                                  {question.explanation && (
                                    <div className="p-2 rounded bg-blue-900/20 border border-blue-600/30">
                                      <span className="text-sm font-medium text-blue-400">Explanation: </span>
                                      <div className="prose prose-invert prose-sm max-w-none mt-1">
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                          {String(question.explanation || '')}
                                        </ReactMarkdown>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-semibold text-slate-200 mb-2">
                              Score: {Object.values(selectedAnswers).filter((answer, idx) => answer === quiz.questions[idx]?.correct_answer).length} / {quiz.questions?.length || 0}
                            </div>
                            <Button
                              variant="outline"
                              onClick={() => {
                                setShowQuizResults(false)
                                setCurrentQuestion(0)
                                setSelectedAnswers({})
                              }}
                            >
                              Retake Quiz
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-6">
                          <div className="text-center">
                            <h3 className="text-xl font-semibold text-slate-200 mb-4">
                              Question {currentQuestion + 1} of {quiz.questions?.length || 0}
                            </h3>
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
                              variant="secondary"
                              onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                              disabled={currentQuestion === 0}
                            >
                              Previous
                            </Button>
                            {currentQuestion < (quiz.questions?.length || 0) - 1 ? (
                              <Button
                                variant="secondary"
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
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'export' && (
                <div>
                  <h2 className="text-2xl font-light text-slate-200 mb-6">📁 Export Session</h2>
                  <div className="space-y-6">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <Button variant="outline" className="h-20 flex-col">
                        <FileText className="h-6 w-6 mb-2" />
                        Markdown
                      </Button>
                      <Button variant="outline" className="h-20 flex-col">
                        <FileText className="h-6 w-6 mb-2" />
                        JSON
                      </Button>
                      <Button variant="outline" className="h-20 flex-col">
                        <FileText className="h-6 w-6 mb-2" />
                        CSV
                      </Button>
                      <Button variant="outline" className="h-20 flex-col">
                        <Download className="h-6 w-6 mb-2" />
                        Bundle
                      </Button>
                    </div>
                    <div className="kensho-card bg-slate-900/30 p-6">
                      <h3 className="font-medium text-slate-200 mb-4">Export Options</h3>
                      <div className="space-y-3">
                        <label className="flex items-center space-x-3">
                          <input type="checkbox" className="rounded" />
                          <span className="text-slate-300">Summaries</span>
                        </label>
                        <label className="flex items-center space-x-3">
                          <input type="checkbox" className="rounded" />
                          <span className="text-slate-300">Chat History</span>
                        </label>
                        <label className="flex items-center space-x-3">
                          <input type="checkbox" className="rounded" />
                          <span className="text-slate-300">Flashcards</span>
                        </label>
                        <label className="flex items-center space-x-3">
                          <input type="checkbox" className="rounded" />
                          <span className="text-slate-300">Quiz Results</span>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Text Input Modal */}
      {showTextModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="kensho-card max-w-2xl w-full p-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-slate-200">Add Text Content</h3>
              <button
                onClick={() => setShowTextModal(false)}
                className="text-slate-400 hover:text-slate-200"
              >
                ×
              </button>
            </div>
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Paste your text content here..."
              className="kensho-input w-full h-64 p-4 rounded-xl resize-none mb-6"
            />
            <div className="flex gap-3 justify-end">
              <Button
                variant="outline"
                onClick={() => setShowTextModal(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleTextUpload}
                disabled={!textInput.trim() || loading}
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

      {/* YouTube Input Modal */}
      {showYoutubeModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="kensho-card max-w-lg w-full p-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-slate-200">Add YouTube Video</h3>
              <button
                onClick={() => setShowYoutubeModal(false)}
                className="text-slate-400 hover:text-slate-200"
              >
                ×
              </button>
            </div>
            <input
              type="url"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              className="kensho-input w-full p-4 rounded-xl mb-6"
            />
            <div className="flex gap-3 justify-end">
              <Button
                variant="outline"
                onClick={() => setShowYoutubeModal(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleYoutubeUpload}
                disabled={!youtubeUrl.trim() || loading}
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

      {/* Footer */}
      <footer className="border-t border-slate-800/50 py-8">
        <div className="container mx-auto px-6 text-center">
          <p className="text-slate-400 text-sm">
            Made with 🧘‍♂️ for mindful learning • Kensho © 2024
          </p>
        </div>
      </footer>
    </div>
  )
}
