/**
 * API service functions for Kensho frontend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (
  typeof window !== 'undefined' && window.location.hostname !== 'localhost' 
    ? '/api' 
    : 'http://localhost:8000'
)

export interface SessionData {
  id: string
  created_at: string
  documents: any[]
  chat_history: any[]
  summaries: any[]
  flashcards: any[]
  quizzes: any[]
  vector_store_path?: string
}

export interface SessionStats {
  documents: number
  pages: number
  chunks: number
  chat_messages: number
  summaries: number
  flashcards: number
  quizzes: number
}

export interface ChatResponse {
  response: string
  sources: any[]
  confidence?: number
  chat_history: any[]
}

// Session management
export async function createSession(): Promise<{ session_id: string; session: SessionData }> {
  const response = await fetch(`${API_BASE_URL}/sessions/new`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  
  if (!response.ok) {
    throw new Error('Failed to create session')
  }
  
  return response.json()
}

export async function getSessionInfo(sessionId: string): Promise<{ session: SessionData; stats: SessionStats }> {
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}`)
  
  if (!response.ok) {
    throw new Error('Failed to get session info')
  }
  
  return response.json()
}

// File upload
export async function uploadPDF(file: File, sessionId?: string): Promise<any> {
  console.log('🌐 Making PDF upload request to:', `${API_BASE_URL}/upload/pdf`)
  console.log('🌐 File details:', { name: file.name, size: file.size, type: file.type })
  console.log('🌐 Session ID:', sessionId)
  
  const formData = new FormData()
  formData.append('file', file)
  if (sessionId) {
    formData.append('session_id', sessionId)
  }
  
  const response = await fetch(`${API_BASE_URL}/upload/pdf`, {
    method: 'POST',
    body: formData,
  })
  
  console.log('🌐 PDF Response status:', response.status, response.statusText)
  
  if (!response.ok) {
    let errorMessage = 'Failed to upload PDF'
    try {
      const errorData = await response.json()
      console.error('🌐 PDF Error response:', errorData)
      errorMessage = errorData.detail || errorMessage
    } catch (e) {
      console.error('🌐 Could not parse PDF error response:', e)
    }
    throw new Error(errorMessage)
  }
  
  const result = await response.json()
  console.log('🌐 PDF Success response:', result)
  return result
}

export async function uploadText(text: string, sessionId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/upload/text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      session_id: sessionId,
    }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to process text')
  }
  
  return response.json()
}

export async function uploadYouTube(url: string, sessionId: string): Promise<any> {
  console.log('🌐 Making YouTube upload request to:', `${API_BASE_URL}/upload/youtube`)
  console.log('🌐 Request body:', { url, session_id: sessionId })
  
  const response = await fetch(`${API_BASE_URL}/upload/youtube`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      url,
      session_id: sessionId,
    }),
  })
  
  console.log('🌐 Response status:', response.status, response.statusText)
  
  if (!response.ok) {
    let errorMessage = 'Failed to process YouTube video'
    try {
      const errorData = await response.json()
      console.error('🌐 Error response:', errorData)
      errorMessage = errorData.detail || errorMessage
    } catch (e) {
      console.error('🌐 Could not parse error response:', e)
    }
    throw new Error(errorMessage)
  }
  
  const result = await response.json()
  console.log('🌐 Success response:', result)
  return result
}

// Chat
export async function sendChatMessage(message: string, sessionId: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to send chat message')
  }
  
  return response.json()
}

// Summary generation
export async function generateSummary(
  sessionId: string,
  summaryType: string = 'comprehensive',
  maxLength: number = 500
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/summary`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      summary_type: summaryType,
      max_length: maxLength,
    }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to generate summary')
  }
  
  return response.json()
}

// Flashcards
export async function generateFlashcards(sessionId: string, numCards: number = 10): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/flashcards`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      num_cards: numCards,
    }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to generate flashcards')
  }
  
  return response.json()
}

// Quiz
export async function generateQuiz(
  sessionId: string,
  numQuestions: number = 5,
  difficulty: string = 'mixed'
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/quiz`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      num_questions: numQuestions,
      difficulty,
    }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to generate quiz')
  }
  
  return response.json()
}

// Export
export async function exportSession(sessionId: string, exportOptions: string[]): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/export`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      export_options: exportOptions,
    }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to export session')
  }
  
  return response.blob()
}

// Health check
export async function healthCheck(): Promise<{ status: string; timestamp: string }> {
  const response = await fetch(`${API_BASE_URL}/health`)
  
  if (!response.ok) {
    throw new Error('API server is not responding')
  }
  
  return response.json()
} 