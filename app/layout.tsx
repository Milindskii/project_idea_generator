import type { Metadata } from "next";
import { Playfair_Display, DM_Sans } from "next/font/google";
import "./globals.css";
import { UserInputProvider } from "@/context/UserInputContext";

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
});

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
});

export const metadata: Metadata = {
  title: "IdeaSpark | AI Project Idea Generator",
  description: "Turn your curiosity into a project with AI-tailored ideas for students.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${playfair.variable} ${dmSans.variable} font-sans antialiased bg-[#F5F0E8] text-[#2C2C2C]`}
      >
        <UserInputProvider>
          {children}
        </UserInputProvider>
      </body>
    </html>
  );
}
