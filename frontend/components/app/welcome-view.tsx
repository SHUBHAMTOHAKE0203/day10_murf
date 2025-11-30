import { Button } from '@/components/livekit/button';

function ShopLogo() {
  return (
    <svg
      width="140"
      height="60"
      viewBox="0 0 140 60"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="mb-6"
    >
      <defs>
        <linearGradient id="shopGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#8B5CF6" />
          <stop offset="100%" stopColor="#EC4899" />
        </linearGradient>
      </defs>
      
      {/* Shopping bag icon */}
      <rect x="35" y="20" width="30" height="35" rx="2" fill="url(#shopGradient)" opacity="0.2"/>
      <path d="M35 25 L35 55 L65 55 L65 25" stroke="url(#shopGradient)" strokeWidth="3" fill="none"/>
      <path d="M40 25 L40 20 C40 15 45 12 50 12 C55 12 60 15 60 20 L60 25" stroke="url(#shopGradient)" strokeWidth="3" fill="none"/>
      
      {/* Text */}
      <text x="75" y="38" fill="url(#shopGradient)" fontSize="20" fontWeight="bold" fontFamily="Arial, sans-serif">
        Sibs Unfiltered SHOP
      </text>
      <text x="75" y="52" fill="#6B7280" fontSize="10" fontFamily="Arial, sans-serif">
        Voice Commerce
      </text>
    </svg>
  );
}

function ShoppingIcon() {
  return (
    <div className="w-20 h-20 mx-auto mb-6 relative">
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full opacity-20 animate-pulse"></div>
      <div className="absolute inset-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full opacity-30"></div>
      <svg className="relative w-20 h-20" viewBox="0 0 80 80" fill="none">
        <circle cx="40" cy="40" r="28" stroke="url(#shopGradient)" strokeWidth="3" fill="white"/>
        <path d="M30 35 L30 50 C30 52 32 54 34 54 L46 54 C48 54 50 52 50 50 L50 35" stroke="url(#shopGradient)" strokeWidth="2.5" fill="none"/>
        <path d="M32 35 L32 30 C32 26 35 23 40 23 C45 23 48 26 48 30 L48 35" stroke="url(#shopGradient)" strokeWidth="2.5" fill="none"/>
        <circle cx="35" cy="42" r="1.5" fill="url(#shopGradient)"/>
        <circle cx="45" cy="42" r="1.5" fill="url(#shopGradient)"/>
      </svg>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 hover:shadow-md transition-all duration-300 hover:border-purple-500/30">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-xl shadow-sm">
          {icon}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-gray-900 text-base mb-2">{title}</h3>
          <p className="text-sm text-gray-600 leading-relaxed">{description}</p>
        </div>
      </div>
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
  return (
    <div ref={ref} className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50/30 to-pink-50/20 flex items-center justify-center p-4">
      <section className="max-w-5xl w-full">
        {/* Trust Badge */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white border-2 border-purple-500/20 shadow-sm">
            <svg className="w-5 h-5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 1a1 1 0 000 2h1.22l.305 1.222a.997.997 0 00.01.042l1.358 5.43-.893.892C3.74 11.846 4.632 14 6.414 14H15a1 1 0 000-2H6.414l1-1H14a1 1 0 00.894-.553l3-6A1 1 0 0017 3H6.28l-.31-1.243A1 1 0 005 1H3zM16 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM6.5 18a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"/>
            </svg>
            <span className="text-gray-700 text-sm font-semibold">AI-Powered Shopping</span>
          </div>
        </div>

        {/* Shop Logo */}
        <div className="flex justify-center mb-6">
          <ShopLogo />
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8 md:p-12 mb-8">
          <div className="text-center mb-8">
            <ShoppingIcon />
            
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4 leading-tight">
              XYZ Shop
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 mt-1">
                SHOP ANYTHING, SPEND MONEY, BECAUSE YOU LIVE ONLY ONECE!!!!
              </span>
            </h1>
            
            <p className="text-xl text-gray-700 font-semibold mb-3">
              Shop Smarter with Voice Commerce
            </p>
            
            <p className="text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Browse our curated collection, discover perfect products, and complete your purchase—all through natural conversation. 
              Shopping has never been this effortless.
            </p>
          </div>

          {/* Feature Grid */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <FeatureCard
              icon="🛍️"
              title="Voice Browsing"
              description="Explore our catalog naturally by describing what you're looking for—colors, sizes, categories, and more"
            />
            <FeatureCard
              icon="🎯"
              title="Smart Recommendations"
              description="Get personalized product suggestions based on your preferences and shopping conversation"
            />
            <FeatureCard
              icon="⚡"
              title="Instant Ordering"
              description="Place orders seamlessly through voice commands with real-time confirmation and tracking"
            />
          </div>

          {/* CTA Button */}
          <div className="flex justify-center">
            <Button 
              variant="primary" 
              size="lg" 
              onClick={onStartCall}
              className="w-full md:w-auto px-10 h-14 text-base font-bold bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-300"
            >
              <span className="flex items-center justify-center gap-3">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                  <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
                {startButtonText}
              </span>
            </Button>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200 p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <span className="text-3xl">🛒</span>
            How Voice Shopping Works
          </h2>
          <ol className="space-y-5 text-base text-gray-700">
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-9 h-9 rounded-lg bg-gradient-to-br from-purple-600 to-pink-600 text-white font-bold flex items-center justify-center text-sm shadow-md">1</span>
              <span className="pt-1"><strong className="text-gray-900">Start Shopping</strong> - Click the button above to activate your voice shopping assistant</span>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-9 h-9 rounded-lg bg-gradient-to-br from-purple-600 to-pink-600 text-white font-bold flex items-center justify-center text-sm shadow-md">2</span>
              <span className="pt-1"><strong className="text-gray-900">Browse Products</strong> - Ask about categories, colors, sizes, or describe what you're looking for</span>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-9 h-9 rounded-lg bg-gradient-to-br from-purple-600 to-pink-600 text-white font-bold flex items-center justify-center text-sm shadow-md">3</span>
              <span className="pt-1"><strong className="text-gray-900">Get Recommendations</strong> - Receive personalized suggestions with prices and details</span>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-9 h-9 rounded-lg bg-gradient-to-br from-purple-600 to-pink-600 text-white font-bold flex items-center justify-center text-sm shadow-md">4</span>
              <span className="pt-1"><strong className="text-gray-900">Complete Purchase</strong> - Place your order by voice and receive instant confirmation with order details</span>
            </li>
          </ol>
        </div>

        {/* Shopping Notice */}
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 border-l-4 border-purple-600 rounded-r-lg p-6 mb-8">
          <div className="flex gap-4">
            <svg className="w-6 h-6 text-purple-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <h3 className="font-bold text-purple-900 mb-2">Shopping Experience Note</h3>
              <p className="text-sm text-purple-800 leading-relaxed">
                This is a demonstration of <strong>Agentic Commerce Protocol (ACP)</strong> voice shopping. 
                Browse our catalog, place orders, and experience the future of conversational commerce. All transactions are simulated for demo purposes.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center space-y-3">
          <p className="text-sm text-gray-600 font-medium">
            Powered by{' '}
            <span className="font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
              Voice AI Commerce
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
              className="text-purple-600 hover:text-purple-700 font-semibold underline underline-offset-2"
            >
              Technical Documentation
            </a>
          </p>
          <div className="flex items-center justify-center gap-3 text-xs text-gray-500 pt-2">
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 1a1 1 0 000 2h1.22l.305 1.222a.997.997 0 00.01.042l1.358 5.43-.893.892C3.74 11.846 4.632 14 6.414 14H15a1 1 0 000-2H6.414l1-1H14a1 1 0 00.894-.553l3-6A1 1 0 0017 3H6.28l-.31-1.243A1 1 0 005 1H3zM16 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM6.5 18a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"/>
              </svg>
              ACP-Inspired
            </span>
            <span>•</span>
            <span>Demo Environment</span>
            <span>•</span>
            <span>#10DaysofAIVoiceAgents</span>
          </div>
          <p className="text-xs text-gray-400 pt-2">
            Day 9: E-commerce Voice Agent | Demo Application for Educational Purposes
          </p>
        </div>
      </section>
    </div>
  );
};