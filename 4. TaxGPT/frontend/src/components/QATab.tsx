import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Loader, AlertCircle, Key } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { useQA } from '../hooks/useQA'
import { useChatStore } from '../store/chatStore'
import { useApiKeyStore } from '../store/apiKeyStore'

interface QATabProps {
  onOpenSettings?: () => void
}

export function QATab({ onOpenSettings }: QATabProps) {
  const [question, setQuestion] = useState('')
  const { mutate, isPending, error } = useQA()
  const { history: chatHistory, clearHistory } = useChatStore()
  const { provider, geminiKey, anthropicKey, openaiKey, openrouterKey, ollamaUrl } = useApiKeyStore()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const apiKey =
    provider === 'gemini' ? geminiKey :
    provider === 'anthropic' ? anthropicKey :
    provider === 'openai' ? openaiKey :
    provider === 'openrouter' ? openrouterKey :
    provider === 'ollama' ? ollamaUrl : ''

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatHistory])

  const MIN_CHARS = 10

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (question.trim().length < MIN_CHARS || !apiKey) return

    mutate(
      {
        question: question.trim(),
        chat_history: chatHistory,
        language: 'en',
      }
    )
    setQuestion('')
  }

  if (!apiKey) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-col items-center justify-center min-h-96 rounded-2xl border border-amber-500/20 bg-amber-500/5 backdrop-blur-2xl text-center p-8"
      >
        <AlertCircle className="h-12 w-12 text-amber-400 mb-4" />
        <h3 className="text-xl font-bold text-white mb-2">API Key Required</h3>
        <p className="text-gray-400 text-sm mb-6">
          Configure at least one AI provider to use the assistant
        </p>
        {onOpenSettings && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onOpenSettings}
            className="flex items-center gap-2 rounded-lg px-6 py-3 text-sm font-semibold text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:shadow-lg hover:shadow-indigo-500/30 transition-all"
          >
            <Key className="h-4 w-4" />
            Configure Providers
          </motion.button>
        )}
      </motion.div>
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-180px)] rounded-2xl border border-white/8 bg-[#0d1117]/70 backdrop-blur-2xl overflow-hidden">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        <AnimatePresence>
          {chatHistory.length === 0 ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center h-full text-center"
            >
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-indigo-500/20 bg-indigo-500/10 mb-4">
                <span className="text-3xl">💡</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Ask TaxGPT</h3>
              <p className="text-gray-500 text-sm max-w-xs">
                Get instant answers about the new Income Tax Act 2025. Ask about sections, deductions, forms, and more.
              </p>
            </motion.div>
          ) : (
            chatHistory.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="space-y-3"
              >
                {/* User message */}
                <div className="flex justify-end">
                  <div className="max-w-xs lg:max-w-md bg-indigo-600 text-white rounded-2xl rounded-tr-sm p-4 shadow-lg">
                    <p className="text-sm">{msg.question}</p>
                  </div>
                </div>

                {/* Assistant message */}
                <div className="flex justify-start">
                  <div className="max-w-xs lg:max-w-2xl bg-white/8 border border-white/10 text-gray-100 rounded-2xl rounded-tl-sm p-4">
                    <ReactMarkdown
                      components={{
                        a: ({ href, children }) => (
                          <a
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-indigo-400 hover:text-indigo-300 underline underline-offset-2 transition-colors"
                          >
                            {children}
                          </a>
                        ),
                        p: ({ children }) => <p className="text-sm mb-2 last:mb-0">{children}</p>,
                        ul: ({ children }) => <ul className="text-sm list-disc list-inside space-y-1 mb-2">{children}</ul>,
                        ol: ({ children }) => <ol className="text-sm list-decimal list-inside space-y-1 mb-2">{children}</ol>,
                        li: ({ children }) => <li className="text-sm">{children}</li>,
                        strong: ({ children }) => <strong className="text-white font-semibold">{children}</strong>,
                        h3: ({ children }) => <h3 className="text-sm font-bold text-white mt-3 mb-1">{children}</h3>,
                        h4: ({ children }) => <h4 className="text-sm font-semibold text-gray-200 mt-2 mb-1">{children}</h4>,
                        table: ({ children }) => (
                          <div className="overflow-x-auto my-2">
                            <table className="text-xs border-collapse w-full">{children}</table>
                          </div>
                        ),
                        th: ({ children }) => <th className="border border-white/20 px-2 py-1 text-left font-semibold bg-white/10">{children}</th>,
                        td: ({ children }) => <td className="border border-white/10 px-2 py-1">{children}</td>,
                        blockquote: ({ children }) => <blockquote className="border-l-2 border-indigo-500 pl-3 text-gray-400 italic my-2">{children}</blockquote>,
                        hr: () => <hr className="border-white/10 my-3" />,
                      }}
                    >
                      {msg.answer}
                    </ReactMarkdown>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>

        {isPending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-2 items-center text-gray-400"
          >
            <Loader className="h-4 w-4 animate-spin" />
            <span className="text-sm">Thinking...</span>
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg p-3 text-sm"
          >
            Error: {error.message}
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-white/8 bg-[#0d1117]/50 p-4">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask about sections, deductions, forms..."
              disabled={isPending}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-indigo-500/50 disabled:opacity-50"
            />
            {question.length > 0 && question.length < MIN_CHARS && (
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-amber-400">
                {MIN_CHARS - question.length} more chars
              </span>
            )}
          </div>
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.97 }}
            type="submit"
            disabled={question.trim().length < MIN_CHARS || isPending}
            className="flex items-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold text-white bg-gradient-to-r from-indigo-600 to-violet-600 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-indigo-500/30 transition-all"
          >
            {isPending ? <Loader className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            {isPending ? 'Sending' : 'Send'}
          </motion.button>
        </form>

        {chatHistory.length > 0 && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            onClick={clearHistory}
            className="mt-3 w-full text-xs text-gray-500 hover:text-gray-300 transition-colors"
          >
            Clear conversation
          </motion.button>
        )}
      </div>
    </div>
  )
}
