'use client';

import React, { useEffect, useRef, ReactNode } from 'react';
import Lenis from 'lenis';
import './ScrollStack.css';

interface ScrollStackProps {
  children: ReactNode;
  useWindowScroll?: boolean;
}

interface ScrollStackItemProps {
  children: ReactNode;
  index: number;
  totalItems: number;
}

export function ScrollStackItem({ children, index, totalItems }: ScrollStackItemProps) {
  const itemRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = itemRef.current;
    if (!el) return;

    const handleScroll = () => {
      const rect = el.getBoundingClientRect();
      const progress = Math.max(0, Math.min(1, (window.innerHeight - rect.top) / window.innerHeight));
      const scale = 1 - (totalItems - index - 1) * 0.03 * (1 - progress);
      const offsetY = (index * 20) * (1 - Math.min(progress * 1.5, 1));
      el.style.transform = `translateY(${-offsetY}px) scale(${scale})`;
      el.style.zIndex = String(index + 1);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, [index, totalItems]);

  return (
    <div ref={itemRef} className="scroll-stack-item" style={{ transformOrigin: 'top center', transition: 'transform 0.1s linear' }}>
      {children}
    </div>
  );
}

export function ScrollStack({ children, useWindowScroll = true }: ScrollStackProps) {
  const lenisRef = useRef<Lenis | null>(null);

  useEffect(() => {
    if (!useWindowScroll) return;

    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    });

    lenisRef.current = lenis;

    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }

    requestAnimationFrame(raf);

    return () => {
      lenis.destroy();
    };
  }, [useWindowScroll]);

  const childArray = React.Children.toArray(children);

  return (
    <div className="scroll-stack-container">
      {childArray.map((child, i) => (
        <ScrollStackItem key={i} index={i} totalItems={childArray.length}>
          {child}
        </ScrollStackItem>
      ))}
    </div>
  );
}
