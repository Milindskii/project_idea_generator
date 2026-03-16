'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface UserInputs {
  domain: string;
  skillLevel: string;
  timeframe: string;
  goal: string;
  ideaDescription: string;
}

interface UserInputContextType {
  inputs: UserInputs;
  setInputs: React.Dispatch<React.SetStateAction<UserInputs>>;
  updateInput: (key: keyof UserInputs, value: string) => void;
}

const UserInputContext = createContext<UserInputContextType | undefined>(undefined);

export function UserInputProvider({ children }: { children: ReactNode }) {
  const [inputs, setInputs] = useState<UserInputs>({
    domain: '',
    skillLevel: '',
    timeframe: '',
    goal: '',
    ideaDescription: '',
  });

  const updateInput = (key: keyof UserInputs, value: string) => {
    setInputs((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <UserInputContext.Provider value={{ inputs, setInputs, updateInput }}>
      {children}
    </UserInputContext.Provider>
  );
}

export function useUserInputs() {
  const context = useContext(UserInputContext);
  if (context === undefined) {
    throw new Error('useUserInputs must be used within a UserInputProvider');
  }
  return context;
}
