import { Button } from '@/components/livekit/button';
import { useState } from 'react';

function ImprovLogo() {
  return (
    <svg
      width="160"
      height="70"
      viewBox="0 0 160 70"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="mb-6"
    >
      <defs>
        <linearGradient id="improvGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#F59E0B" />
          <stop offset="100%" stopColor="#EF4444" />
        </linearGradient>
      </defs>
      
      {/* Spotlight icon */}
      <circle cx="40" cy="35" r="20" fill="url(#improvGradient)" opacity="0.2"/>
      <path d="M40 15 L40 55 M25 35 L55 35" stroke="url(#improvGradient)" strokeWidth="3"/>
      <circle cx="40" cy="35" r="18" stroke="url(#improvGradient)" strokeWidth="2.5" fill="none"/>
      
      {/* Text */}
      <text x="70" y="40" fill="url(#improvGradient)" fontSize="24" fontWeight="bold" fontFamily="Arial, sans-serif">
        Improv Spotlight
      </text>
      <text x="70" y="55" fill="#6B7280" fontSize="11" fontFamily="Arial, sans-serif">
        AI Voice Battle
      </text>
    </svg>
  );
}

function SpotlightIcon() {
  return (
    <div className="w-24 h-24 mx-auto mb-6 relative">
      <div className="absolute inset-0 bg-gradient-to-br from-amber-500 to-red-500 rounded-full opacity-20 animate-pulse"></div>
      <div className="absolute inset-2 bg-gradient-to-br from-amber-500 to-red-500 rounded-full opacity-30"></div>
      <svg className="relative w-24 h-24" viewBox="0 0 96 96" fill="none">
        <circle cx="48" cy="48" r="32" stroke="url(#improvGradient)" strokeWidth="3" fill="white"/>
        <path d="M48 20 L48 76 M20 48 L76 48" stroke="url(#improvGradient)" strokeWidth="3.5"/>
        <circle cx="48" cy="48" r="8" fill="url(#improvGradient)"/>
        <path d="M40 30 L48 20 L56 30" stroke="url(#improvGradient)" strokeWidth="2" fill="none"/>
        <path d="M40 66 L48 76 L56 66" stroke="url(#improvGradient)" strokeWidth="2" fill="none"/>
      </svg>
    </div>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  const [playerName, setPlayerName] = useState('');

  const handleStart = () => {
    if (playerName.trim()) {
      // Store player name in sessionStorage so agent can access it
      sessionStorage.setItem('playerName', playerName.trim());
      
      // Pass the name to the parent component which will send it to the agent
      onStartCall();
    }
  };

  return (
    <div ref={ref} className="min-h-screen bg-gradient-to-br from-gray-50 via-amber-50/30 to-red-50/20 flex items-center justify-center p-4">
      <section className="max-w-2xl w-full">
        {/* Trust Badge */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white border-2 border-amber-500/20 shadow-sm">
            <svg className="w-5 h-5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
            <span className="text-gray-700 text-sm font-semibold">AI-Powered Improv</span>
          </div>
        </div>

        {/* Logo */}
        <div className="flex justify-center mb-6">
          <ImprovLogo />
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8 md:p-12 mb-8">
          <div className="text-center mb-8">
            <SpotlightIcon />
            
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4 leading-tight">
              Welcome to
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-amber-600 to-red-600 mt-1">
                Improv Spotlight!
              </span>
            </h1>
            
            <p className="text-lg text-gray-700 font-semibold mb-3">
              Battle the AI Host in 4 Improvised Scenes
            </p>
            
            <p className="text-gray-600 max-w-xl mx-auto leading-relaxed mb-8">
              Step into the spotlight! You'll perform 4 improv scenes with an AI host who will judge your performance, 
              give feedback, and keep the energy high. Ready to show your skills?
            </p>
          </div>

          {/* Join Form */}
          <div className="max-w-md mx-auto space-y-6">
            <div>
              <label htmlFor="playerName" className="block text-sm font-semibold text-gray-700 mb-2">
                Your Name (Contestant)
              </label>
              <input
                id="playerName"
                type="text"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                placeholder="Enter your name..."
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-amber-500 focus:ring focus:ring-amber-200 focus:outline-none text-gray-900 placeholder-gray-400"
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && playerName.trim()) {
                    handleStart();
                  }
                }}
              />
            </div>

            {/* CTA Button */}
            <Button 
              variant="primary" 
              size="lg" 
              onClick={handleStart}
              disabled={!playerName.trim()}
              className="w-full h-14 text-base font-bold bg-gradient-to-r from-amber-600 to-red-600 hover:from-amber-700 hover:to-red-700 disabled:from-gray-400 disabled:to-gray-400 text-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 disabled:cursor-not-allowed"
            >
              <span className="flex items-center justify-center gap-3">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                  <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
                Start Improv Battle
              </span>
            </Button>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200 p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <span className="text-3xl">🎭</span>
            How It Works
          </h2>
          <ol className="space-y-5 text-base text-gray-700">
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-9 h-9 rounded-lg bg-gradient-to-br from-amber-600 to-red-600 text-white font-bold flex items-center justify-center text-sm shadow-md">1</span>
              <span className="pt-1"><strong className="text-gray-900">Enter Your Name</strong> - Type your contestant name above</span>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-9 h-9 rounded-lg bg-gradient-to-br from-amber-600 to-red-600 text-white font-bold flex items-center justify-center text-sm shadow-md">2</span>
              <span className="pt-1"><strong className="text-gray-900">Start the Battle</strong> - Click the button to connect with the AI host</span>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-9 h-9 rounded-lg bg-gradient-to-br from-amber-600 to-red-600 text-white font-bold flex items-center justify-center text-sm shadow-md">3</span>
              <span className="pt-1"><strong className="text-gray-900">Perform Scenes</strong> - The host will give you 4 scenarios. Act them out and say "End scene" when done</span>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-9 h-9 rounded-lg bg-gradient-to-br from-amber-600 to-red-600 text-white font-bold flex items-center justify-center text-sm shadow-md">4</span>
              <span className="pt-1"><strong className="text-gray-900">Get Feedback</strong> - Receive instant reactions and tips after each performance</span>
            </li>
          </ol>
        </div>

        {/* Game Info Notice */}
        <div className="bg-gradient-to-r from-amber-50 to-red-50 border-l-4 border-amber-600 rounded-r-lg p-6 mb-8">
          <div className="flex gap-4">
            <svg className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <h3 className="font-bold text-amber-900 mb-2">Game Format</h3>
              <p className="text-sm text-amber-800 leading-relaxed">
                You'll perform <strong>4 improv scenes</strong>. The AI host will set up each scenario, 
                watch your performance, and give you constructive feedback. Be creative, have fun, 
                and don't be afraid to take risks!
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center space-y-3">
          <p className="text-sm text-gray-600 font-medium">
            Powered by{' '}
            <span className="font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-600 to-red-600">
              Voice AI Technology
            </span>
            {' '}×{' '}
            <span className="font-bold text-gray-700">
              LiveKit & Murf Falcon
            </span>
          </p>
          <p className="text-xs text-gray-500">
            Part of #MurfAIVoiceAgentsChallenge |{' '}
            <a
              target="_blank"
              rel="noopener noreferrer"
              href="https://docs.livekit.io/agents/start/voice-ai/"
              className="text-amber-600 hover:text-amber-700 font-semibold underline underline-offset-2"
            >
              Technical Documentation
            </a>
          </p>
          <div className="flex items-center justify-center gap-3 text-xs text-gray-500 pt-2">
            <span>🎭 AI Improv</span>
            <span>•</span>
            <span>Live Voice Interaction</span>
            <span>•</span>
            <span>#10DaysofAIVoiceAgents</span>
          </div>
          <p className="text-xs text-gray-400 pt-2">
            Day X: Improv Spotlight | Educational Demo Application
          </p>
        </div>
      </section>
    </div>
  );
};