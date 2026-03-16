'use client';

import Link from 'next/link';
import { Sparkles } from 'lucide-react';

export default function Navbar() {
  return (
    <div className="fixed top-6 left-0 right-0 z-50 px-6">
      <nav className="max-w-fit mx-auto bg-white/70 backdrop-blur-xl border border-black/5 px-6 py-3 rounded-full shadow-sm flex items-center gap-8">
        <Link href="/" className="group">
          <div className="bg-primary p-2 rounded-full group-hover:rotate-12 transition-transform">
            <Sparkles className="w-4 h-4 text-accent" />
          </div>
        </Link>
        
        <div className="flex items-center gap-6 font-sans text-sm font-medium text-primary/70">
          <Link href="/#how-it-works" className="hover:text-primary transition-colors">Process</Link>
          <Link href="/#who-is-it-for" className="hover:text-primary transition-colors">For Students</Link>
          <div className="w-px h-4 bg-black/10" />
          <Link href="/questions" className="text-accent hover:text-accent/80 transition-colors font-bold">Start Building</Link>
        </div>
      </nav>
    </div>
  );
}
