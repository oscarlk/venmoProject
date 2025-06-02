// contexts/AuthContext.jsx - Create this new file
import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const signInWithGoogle = async () => {
    try {
      // Open Google OAuth popup to Flask backend
      const popup = window.open(
        'http://localhost:8000/auth/signin/google',
        'google-signin',
        'width=500,height=600,scrollbars=yes,resizable=yes'
      )
      
      // Listen for messages from popup
      const handleMessage = (event) => {
        // Only accept messages from our backend
        if (event.origin !== 'http://localhost:8000') return
        
        if (event.data.type === 'success') {
          popup.close()
          checkAuthStatus() // Refresh auth status
          window.removeEventListener('message', handleMessage)
        } else if (event.data.type === 'error') {
          popup.close()
          alert('Sign in failed: ' + (event.data.message || 'Unknown error'))
          window.removeEventListener('message', handleMessage)
        }
      }
      
      window.addEventListener('message', handleMessage)
      
      // Check if popup was closed manually
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed)
          window.removeEventListener('message', handleMessage)
        }
      }, 1000)
      
    } catch (error) {
      console.error('Sign in failed:', error)
    }
  }

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/auth/session', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setUser(data.user)
      } else {
        setUser(null)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const signOut = async () => {
    try {
      await fetch('http://localhost:8000/auth/signout', { 
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      setUser(null)
    } catch (error) {
      console.error('Sign out failed:', error)
      setUser(null)
    }
  }

  useEffect(() => {
    checkAuthStatus()
  }, [])

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      signInWithGoogle,
      signOut
    }}>
      {children}
    </AuthContext.Provider>
  )
}