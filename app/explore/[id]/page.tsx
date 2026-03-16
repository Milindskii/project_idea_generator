'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from '@/components/Navbar';
import { Sparkles, Send, ArrowLeft } from 'lucide-react';

interface Message {
  id: number;
  role: 'assistant' | 'user';
  text: string;
}

function getSmartReply(userMsg: string, context: { title: string; description: string; tech: string; difficulty: string }): string {
  const msg = userMsg.toLowerCase();

  if (msg.includes('tech') || msg.includes('stack') || msg.includes('language') || msg.includes('framework')) {
    return `For **${context.title}**, the recommended tech stack is: **${context.tech}**. Each tool is chosen to match the ${context.difficulty.toLowerCase()} skill level. Want me to explain why any specific technology was picked?`;
  }
  if (msg.includes('start') || msg.includes('begin') || msg.includes('first step') || msg.includes('how do i')) {
    return `Great question! Here's how to kick off **${context.title}**:\n\n1. **Set up your dev environment** — install the core tools from the stack.\n2. **Build a minimal prototype** — focus on the single most important feature first.\n3. **Test early** — get something running in your browser/device within the first week.\n\nWant a more detailed week-by-week roadmap?`;
  }
  if (msg.includes('roadmap') || msg.includes('plan') || msg.includes('week') || msg.includes('timeline')) {
    return `Here's a realistic roadmap for **${context.title}** at ${context.difficulty} level:\n\n**Week 1–2:** Setup & design. Wireframes, environment, and a "hello world" build.\n**Week 3–5:** Core feature development. Get the main functionality working end-to-end.\n**Week 6–7:** Polish & testing. Fix bugs, add edge case handling, improve UI.\n**Week 8:** Deploy & document. Push to GitHub, write a README, and share it!\n\nNeed help with any specific week?`;
  }
  if (msg.includes('deploy') || msg.includes('hosting') || msg.includes('vercel') || msg.includes('production')) {
    return `For **${context.title}**, I'd recommend deploying on **Vercel** (if it's a web app) or **Railway** for backends. Both have free tiers perfect for student projects. Want a step-by-step deployment checklist?`;
  }
  if (msg.includes('difficult') || msg.includes('hard') || msg.includes('challenge') || msg.includes('stuck')) {
    return `That's totally normal — even senior devs hit walls! For **${context.title}**, the most common challenges are around data integration and state management. Here's my advice: \n\n- Break the problem into the smallest possible unit.\n- Search with very specific terms (e.g., "TensorFlow Lite image classification example").\n- Use GitHub's "Explore" tab for real open-source examples.\n\nWhat exactly are you stuck on? Let's solve it together.`;
  }
  if (msg.includes('similar') || msg.includes('alternative') || msg.includes('other idea')) {
    return `If **${context.title}** isn't the right fit, some close alternatives would be:\n\n- A simpler CRUD version with a REST API to learn the fundamentals first.\n- A data visualization dashboard using mock data before going live.\n- A CLI version of the same concept — great for portfolios too!\n\nWant me to describe any of these in more detail?`;
  }
  if (msg.includes('resource') || msg.includes('learn') || msg.includes('tutorial') || msg.includes('doc')) {
    return `Here are some top resources for **${context.title}** (${context.tech}):\n\n- 📚 **Official Docs** — always the most reliable source.\n- 🎥 **YouTube** — search for "\${context.title} build tutorial".\n- 🧑‍💻 **GitHub** — look at real projects with similar stacks.\n- 💬 **Reddit r/learnprogramming** — great for beginner questions.\n\nAny specific technology you want resources for?`;
  }
  if (msg.includes('thank') || msg.includes('great') || msg.includes('nice') || msg.includes('awesome')) {
    return `You're very welcome! I'm genuinely excited for you to build **${context.title}** — it's a great project. Come back anytime if you hit a wall or need ideas. You've got this! 🚀`;
  }

  return `That's a thoughtful question about **${context.title}**. Based on the ${context.difficulty} level of this project and its focus on ${context.description.split('.')[0].toLowerCase()}, I'd suggest first making sure your foundational setup is solid before diving into the more complex parts. Is there a specific aspect — like the tech stack, the roadmap, or deployment — you'd like me to focus on?`;
}

export default function ExplorePage() {
  const params = useSearchParams();
  const router = useRouter();
  const title = params.get('title') ?? 'Your Project';
  const description = params.get('description') ?? '';
  const tech = params.get('tech') ?? '';
  const difficulty = params.get('difficulty') ?? 'Intermediate';

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      role: 'assistant',
      text: `Welcome! I'm your IdeaSpark guide for **${title}**. 🎯\n\nThis is a **${difficulty}** level project that ${description.split('.')[0].toLowerCase()}. I'm here to help you break it down, plan your roadmap, understand the tech stack, and get unstuck whenever you need it.\n\nWhat would you like to explore first? You can ask me about the tech stack, where to start, a weekly roadmap, or anything else about this project.`,
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const sendMessage = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed || isTyping) return;

    const userMsg: Message = { id: Date.now(), role: 'user', text: trimmed };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    const delay = 900 + Math.random() * 600;
    setTimeout(() => {
      const reply = getSmartReply(trimmed, { title, description, tech, difficulty });
      setMessages((prev) => [...prev, { id: Date.now() + 1, role: 'assistant', text: reply }]);
      setIsTyping(false);
    }, delay);
  }, [input, isTyping, title, description, tech, difficulty]);

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const suggestions = ['Where do I start?', 'Give me a weekly roadmap', 'Explain the tech stack', 'How do I deploy this?'];

  return (
    <div className="min-h-screen flex flex-col bg-paper">
      <Navbar />

      <main className="flex-grow max-w-3xl mx-auto w-full px-6 pt-12 pb-8 flex flex-col">
        {/* Back + Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <Link
            href="/results"
            className="inline-flex items-center gap-2 text-sm text-primary/40 hover:text-primary transition-colors mb-6"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Results
          </Link>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-accent/10 p-2 rounded-lg">
              <Sparkles className="w-5 h-5 text-accent" />
            </div>
            <span className="text-xs font-bold uppercase tracking-widest text-primary/40">AI Project Guide</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-serif text-primary leading-tight">{title}</h1>
          <p className="text-primary/50 text-sm mt-1 font-medium">{difficulty} · {tech}</p>
        </motion.div>

        {/* Chat area */}
        <div className="flex-grow overflow-y-auto space-y-5 mb-6 pr-1" style={{ maxHeight: 'calc(100vh - 380px)' }}>
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="bg-accent/10 p-1.5 rounded-full self-end mb-1 mr-2 flex-shrink-0">
                    <Sparkles className="w-3.5 h-3.5 text-accent" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-2xl px-5 py-4 text-sm leading-relaxed whitespace-pre-line ${
                    msg.role === 'user'
                      ? 'bg-primary text-white rounded-br-sm font-medium'
                      : 'bg-white border border-black/5 text-primary rounded-bl-sm shadow-sm'
                  }`}
                  dangerouslySetInnerHTML={{
                    __html: msg.text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'),
                  }}
                />
              </motion.div>
            ))}

            {isTyping && (
              <motion.div key="typing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-end gap-2">
                <div className="bg-accent/10 p-1.5 rounded-full mb-1">
                  <Sparkles className="w-3.5 h-3.5 text-accent" />
                </div>
                <div className="bg-white border border-black/5 rounded-2xl rounded-bl-sm px-5 py-4 shadow-sm flex gap-1.5 items-center">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      className="w-2 h-2 rounded-full bg-primary/30"
                      animate={{ y: [0, -5, 0] }}
                      transition={{ duration: 0.7, repeat: Infinity, delay: i * 0.15 }}
                    />
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={bottomRef} />
        </div>

        {/* Quick suggestions */}
        {messages.length <= 2 && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-wrap gap-2 mb-4">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => { setInput(s); }}
                className="text-xs px-3 py-2 rounded-full border border-black/10 text-primary/60 hover:border-accent/50 hover:text-accent transition-all bg-white/60"
              >
                {s}
              </button>
            ))}
          </motion.div>
        )}

        {/* Input */}
        <div className="flex gap-3 items-end bg-white border border-black/10 rounded-2xl p-3 shadow-sm focus-within:border-accent/40 transition-colors">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask anything about this project…"
            rows={1}
            className="flex-grow resize-none text-sm text-primary placeholder-primary/30 bg-transparent outline-none leading-relaxed max-h-32 font-sans"
            style={{ fieldSizing: 'content' } as React.CSSProperties}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isTyping}
            className="bg-accent text-white p-2.5 rounded-xl flex-shrink-0 hover:bg-accent/90 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-center text-xs text-primary/25 mt-3 font-medium">Press Enter to send · Shift+Enter for new line</p>
      </main>
    </div>
  );
}
