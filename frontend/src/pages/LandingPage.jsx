import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Timeline, ConfigProvider, theme, Collapse } from 'antd';
import { 
  ClockCircleOutlined, 
  CheckCircleOutlined, 
  SyncOutlined,
  UserOutlined,
  ShoppingOutlined
} from '@ant-design/icons';
import { 
  Menu, X, ChevronDown, ShoppingCart, 
  Truck, Zap, BarChart3, Users, 
  Linkedin, Github, Mail, ArrowRight, 
  Package, Heart, CreditCard, Globe
} from 'lucide-react';

// --- Components ---

const Navbar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [solutionsOpen, setSolutionsOpen] = useState(false);

  // Smooth scroll to section
  const scrollTo = (id) => {
    const element = document.getElementById(id);
    if (element) element.scrollIntoView({ behavior: 'smooth' });
    setMobileMenuOpen(false);
  };

  return (
    <header className="absolute inset-x-0 top-0 z-50">
      <nav className="flex items-center justify-between p-6 lg:px-8" aria-label="Global">
        <div className="flex lg:flex-1">
          <Link to="/" className="-m-1.5 p-1.5 flex items-center gap-2">
            <span className="sr-only">Weeb</span>
            {/* Charm Font applied here */}
            <span className="text-white font-bold text-3xl tracking-tight" style={{ fontFamily: '"Charm", cursive' }}>Weeb</span>
          </Link>
        </div>
        
        {/* Mobile Menu Button */}
        <div className="flex lg:hidden">
          <button
            type="button"
            className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-200 hover:text-white"
            onClick={() => setMobileMenuOpen(true)}
          >
            <span className="sr-only">Open main menu</span>
            <Menu className="h-6 w-6" />
          </button>
        </div>

        {/* Desktop Menu */}
        <div className="hidden lg:flex lg:gap-x-12 items-center">
          
          {/* Solutions Dropdown */}
          <div className="relative group">
            <button 
              className="inline-flex items-center gap-x-1 text-sm font-semibold leading-6 text-white outline-none group-hover:text-blue-400 transition-colors"
              onClick={() => scrollTo('business-solutions')}
            >
              <span>Solutions</span>
              <ChevronDown className="h-4 w-4 text-gray-400 group-hover:text-blue-400 transition-colors" />
            </button>
            
            {/* Hover Card / Popover */}
            
          </div>

          <button onClick={() => scrollTo('features')} className="text-sm font-semibold leading-6 text-white hover:text-blue-300 transition-colors">Features</button>
          <button onClick={() => scrollTo('how-it-works')} className="text-sm font-semibold leading-6 text-white hover:text-blue-300 transition-colors">How it Works</button>
          <button onClick={() => scrollTo('faq')} className="text-sm font-semibold leading-6 text-white hover:text-blue-300 transition-colors">FAQ</button>
        </div>

        <div className="hidden lg:flex lg:flex-1 lg:justify-end gap-4">
          <button onClick={() => scrollTo('book-demo')} className="rounded-full bg-blue-600 px-6 py-2 text-sm font-semibold text-white shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:bg-blue-500 hover:shadow-[0_0_30px_rgba(37,99,235,0.5)] transition-all">
            Book a Demo
          </button>
        </div>
      </nav>

      {/* Mobile Menu Dialog */}
      <div className={`lg:hidden fixed inset-0 z-50 bg-gray-900/95 backdrop-blur-xl transition-transform duration-300 ${mobileMenuOpen ? 'translate-x-0' : 'translate-x-full'}`}>
          <div className="flex items-center justify-between p-6">
            <span className="text-white font-bold text-3xl" style={{ fontFamily: '"Charm", cursive' }}>Weeb</span>
            <button
              type="button"
              className="-m-2.5 rounded-md p-2.5 text-gray-200"
              onClick={() => setMobileMenuOpen(false)}
            >
              <span className="sr-only">Close menu</span>
              <X className="h-6 w-6" />
            </button>
          </div>
          <div className="mt-6 flow-root px-6">
            <div className="-my-6 divide-y divide-white/10">
              <div className="space-y-2 py-6">
                <button onClick={() => scrollTo('features')} className="-mx-3 block w-full text-left rounded-lg px-3 py-2 text-base font-semibold leading-7 text-white hover:bg-white/5">Features</button>
                <button onClick={() => scrollTo('business-solutions')} className="-mx-3 block w-full text-left rounded-lg px-3 py-2 text-base font-semibold leading-7 text-white hover:bg-white/5">Solutions</button>
                <button onClick={() => scrollTo('faq')} className="-mx-3 block w-full text-left rounded-lg px-3 py-2 text-base font-semibold leading-7 text-white hover:bg-white/5">FAQ</button>
              </div>
              <div className="py-6">
                <button onClick={() => scrollTo('book-demo')} className="-mx-3 block w-full text-center rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-white bg-blue-600 hover:bg-blue-500">Book Demo</button>
              </div>
            </div>
          </div>
      </div>
    </header>
  );
};

const Hero = () => {
  return (
    <div className="relative isolate pt-14">
      {/* Blue Background Blob */}
      <div className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80" aria-hidden="true">
        <div className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-blue-600 to-cyan-400 opacity-20 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]" style={{ clipPath: 'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)' }} />
      </div>

      <div className="py-24 sm:py-32 lg:pb-40 relative">
        {/* Mask Gradient for bottom blend */}
        <div className="absolute inset-0 pointer-events-none z-20" style={{ background: 'linear-gradient(to bottom, transparent 60%, #030712 100%)' }} />
        
        <div className="mx-auto max-w-7xl px-6 lg:px-8 relative z-10">
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="text-4xl font-bold tracking-tight text-white sm:text-7xl bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-100 to-blue-300 drop-shadow-sm">
              The AI Agent That Runs Your Support, Sales & Ops
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-300">
              Weeb doesn’t just answer questions. It understands users, executes backend actions, updates systems, and escalates smartly.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              {/* Redirects to actual demo app */}
              <Link to="/demo" className="rounded-full bg-blue-600 px-8 py-3.5 text-sm font-semibold text-white shadow-[0_0_20px_rgba(37,99,235,0.4)] hover:bg-blue-500 hover:shadow-[0_0_35px_rgba(37,99,235,0.6)] hover:scale-105 transition-all">
                See Weeb in Action
              </Link>
              <button onClick={() => document.getElementById('book-demo').scrollIntoView({ behavior: 'smooth'})} className="text-sm font-semibold leading-6 text-white flex items-center gap-1 group">
                Book a Demo <span aria-hidden="true" className="group-hover:translate-x-1 transition-transform">→</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Bottom Background Blob */}
      <div className="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]" aria-hidden="true">
        <div className="relative left-[calc(50%+3rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 bg-gradient-to-tr from-blue-600 to-cyan-500 opacity-20 sm:left-[calc(50%+36rem)] sm:w-[72.1875rem]" style={{ clipPath: 'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)' }} />
      </div>
    </div>
  );
};
const FeaturesBento = () => {
  return (
    <div id="features" className="bg-gray-950 py-24 sm:py-32">
      <div className="mx-auto max-w-2xl px-6 lg:max-w-7xl lg:px-8">
        <h2 className="text-center text-base font-semibold leading-7 text-blue-400">Beyond Chatbots</h2>
        <p className="mx-auto mt-2 max-w-lg text-center text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Everything an Agent Should Be
        </p>
        
        <div className="mt-10 grid grid-cols-1 gap-4 sm:mt-16 lg:grid-cols-3 lg:grid-rows-2">
          
          {/* Card 1: Action Engine (Vertical Left Anchor) */}
          <div className="relative lg:row-span-2 group">
            <div className="absolute inset-px rounded-lg bg-white/5 backdrop-blur-sm lg:rounded-l-[2rem] border border-white/10 hover:border-blue-500/50 transition-colors"></div>
            <div className="relative flex h-full flex-col overflow-hidden rounded-[calc(var(--radius-lg)+1px)] lg:rounded-l-[calc(2rem+1px)]">
              <div className="px-8 pt-8 pb-3 sm:px-10 sm:pt-10 sm:pb-0">
                <p className="mt-2 text-lg font-medium tracking-tight text-white">Conversational Action Engine</p>
                <p className="mt-2 max-w-lg text-sm leading-6 text-gray-400">
                  Not just chat — real actions. Add to cart, create orders, and request refunds directly from the conversation.
                </p>
              </div>
              <div className="relative min-h-[30rem] w-full grow [container-type:inline-size] max-lg:mx-auto max-lg:max-w-sm">
                <div className="absolute inset-x-10 top-10 bottom-0 overflow-hidden rounded-t-[12cqw] border-x-[3cqw] border-t-[3cqw] border-gray-700 bg-gray-900 shadow-2xl">
                    <img className="size-full object-cover object-top opacity-90" src="https://ui.shadcn.com/placeholder.svg" alt="Chat Interface" />
                    <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent"></div>
                </div>
              </div>
            </div>
            <div className="pointer-events-none absolute inset-px rounded-lg shadow-sm ring-1 ring-white/10 lg:rounded-l-[2rem]"></div>
          </div>

          {/* Card 2: Inventory Aware (Top Middle) */}
          <div className="relative group">
            <div className="absolute inset-px rounded-lg bg-white/5 backdrop-blur-sm border border-white/10 hover:border-blue-500/50 transition-colors"></div>
            <div className="relative flex h-full flex-col overflow-hidden rounded-[calc(var(--radius-lg)+1px)]">
              <div className="px-8 pt-8 sm:px-10 sm:pt-10">
                <div className="flex items-center gap-3 mb-2">
                    <Package className="text-blue-400 h-6 w-6" />
                    <p className="text-lg font-medium tracking-tight text-white">Inventory-Aware by Design</p>
                </div>
                <p className="mt-2 max-w-lg text-sm leading-6 text-gray-400">
                  Weeb never guesses. It checks live inventory across stores and warehouses before responding.
                </p>
                <p className="mt-4 text-xs font-mono text-blue-300 bg-blue-900/20 w-fit px-2 py-1 rounded">
                   "If it can’t ship, Weeb won’t sell it."
                </p>
              </div>
            </div>
            <div className="pointer-events-none absolute inset-px rounded-lg shadow-sm ring-1 ring-white/10"></div>
          </div>

          {/* Card 3: Full Backend Control (Top Right) */}
          <div className="relative group lg:col-start-3 lg:row-start-1">
            <div className="absolute inset-px rounded-lg bg-white/5 backdrop-blur-sm lg:rounded-tr-[2rem] border border-white/10 hover:border-blue-500/50 transition-colors"></div>
            <div className="relative flex h-full flex-col overflow-hidden rounded-[calc(var(--radius-lg)+1px)] lg:rounded-tr-[calc(2rem+1px)]">
              <div className="px-8 pt-8 sm:px-10 sm:pt-10">
                 <div className="flex items-center gap-3 mb-2">
                    <Zap className="text-yellow-400 h-6 w-6" />
                    <p className="text-lg font-medium tracking-tight text-white">Not a Chatbot. An Operator.</p>
                </div>
                <p className="mt-2 max-w-lg text-sm leading-6 text-gray-400">
                  Weeb doesn’t just talk — it acts. It can place orders, track deliveries, and resolve complaints inside your backend.
                </p>
              </div>
            </div>
            <div className="pointer-events-none absolute inset-px rounded-lg shadow-sm ring-1 ring-white/10 lg:rounded-tr-[2rem]"></div>
          </div>

          {/* Card 4: Memory (Bottom Middle) */}
          <div className="relative group lg:col-start-2 lg:row-start-2">
            <div className="absolute inset-px rounded-lg bg-white/5 backdrop-blur-sm border border-white/10 hover:border-blue-500/50 transition-colors"></div>
            <div className="relative flex h-full flex-col overflow-hidden rounded-[calc(var(--radius-lg)+1px)]">
              <div className="px-8 pt-8 sm:px-10 sm:pt-10">
                <p className="mt-2 text-lg font-medium tracking-tight text-white">Memory & Personalization</p>
                <p className="mt-2 max-w-lg text-sm leading-6 text-gray-400">
                  Weeb remembers your size, style, and returns. No generic lists.
                </p>
              </div>
              <div className="relative min-h-[10rem] w-full grow px-8 pt-4 pb-0">
                 <div className="w-full bg-gray-900/50 rounded-t-xl border border-white/5 p-3 space-y-2">
                    <div className="flex justify-end"><div className="bg-blue-600/20 text-blue-200 text-[10px] px-2 py-1 rounded-lg rounded-tr-none">Dress for summer wedding?</div></div>
                    <div className="flex justify-start"><div className="bg-gray-700/50 text-gray-200 text-[10px] px-2 py-1 rounded-lg rounded-tl-none">Found a Red Silk Midi in Size M (based on last order).</div></div>
                 </div>
              </div>
            </div>
            <div className="pointer-events-none absolute inset-px rounded-lg shadow-sm ring-1 ring-white/10"></div>
          </div>

          {/* Card 5: Safe Escalation (Bottom Right) */}
          <div className="relative group lg:col-start-3 lg:row-start-2">
            <div className="absolute inset-px rounded-lg bg-white/5 backdrop-blur-sm lg:rounded-br-[2rem] border border-white/10 hover:border-blue-500/50 transition-colors"></div>
            <div className="relative flex h-full flex-col overflow-hidden rounded-[calc(var(--radius-lg)+1px)] lg:rounded-br-[calc(2rem+1px)]">
              <div className="px-8 pt-8 sm:px-10 sm:pt-10">
                <div className="flex items-center gap-3 mb-2">
                    <UserOutlined className="text-red-400 text-xl" />
                    <p className="text-lg font-medium tracking-tight text-white">AI First. Humans When Needed.</p>
                </div>
                <p className="mt-2 max-w-lg text-sm leading-6 text-gray-400">
                  Low confidence? Weeb hands off to a human with full context. No repeated explanations.
                </p>
                <div className="mt-4 flex items-center gap-2">
                    <span className="inline-flex items-center gap-1 rounded-md bg-green-500/10 px-2 py-1 text-xs font-medium text-green-400 ring-1 ring-inset ring-green-500/20">
                        Confidence Score
                    </span>
                    <span className="text-xs text-gray-500">→</span>
                    <span className="inline-flex items-center gap-1 rounded-md bg-red-500/10 px-2 py-1 text-xs font-medium text-red-400 ring-1 ring-inset ring-red-500/20">
                        Auto-Handoff
                    </span>
                </div>
              </div>
            </div>
            <div className="pointer-events-none absolute inset-px rounded-lg shadow-sm ring-1 ring-white/10 lg:rounded-br-[2rem]"></div>
          </div>

        </div>
      </div>
    </div>
  );
};

const ProblemSolutionTimeline = () => {
    // Timeline Items Data
    const items = [
        {
            children: (
                <div className="mb-8">
                    <h4 className="text-white font-bold text-lg">1. User Tracking & Intent</h4>
                    <p className="text-gray-400 text-sm">Weeb observes behavior (clicks, filters) and identifies user intent from natural language.</p>
                </div>
            ),
            color: 'gray',
            icon: <UserOutlined />
        },
        {
            children: (
                <div className="mb-8">
                    <h4 className="text-blue-400 font-bold text-lg">2. Recommendation Engine</h4>
                    <p className="text-gray-400 text-sm">"Based on your search for weddings, here are red dresses in Size M available now."</p>
                </div>
            ),
            color: 'blue',
            icon: <ShoppingOutlined />
        },
        {
            children: (
                <div className="mb-8">
                    <h4 className="text-green-400 font-bold text-lg">3. Frictionless Action</h4>
                    <p className="text-gray-400 text-sm">User says "Add it". Weeb adds to cart, applies the best offer, and generates the checkout link.</p>
                </div>
            ),
            color: 'green',
            icon: <CheckCircleOutlined />
        },
        {
            children: (
                <div>
                    <h4 className="text-purple-400 font-bold text-lg">4. Post-Purchase Support</h4>
                    <p className="text-gray-400 text-sm">"Where is my order?" Weeb tracks delivery instantly via API. No tickets needed.</p>
                </div>
            ),
            color: 'purple',
            icon: <Truck size={14} />
        }
    ];

    return (
        <div id="how-it-works" className="relative isolate overflow-hidden bg-gray-900 px-6 py-24 sm:py-32 lg:overflow-visible lg:px-0">
            <div className="absolute inset-0 -z-10 overflow-hidden">
                <svg aria-hidden="true" className="absolute top-0 left-[max(50%,25rem)] h-[64rem] w-[128rem] -translate-x-1/2 stroke-gray-800 [mask-image:radial-gradient(64rem_64rem_at_top,white,transparent)]">
                    <defs>
                        <pattern id="grid-pattern" width="200" height="200" x="50%" y="-1" patternUnits="userSpaceOnUse">
                            <path d="M100 200V.5M.5 .5H200" fill="none" />
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" strokeWidth="0" fill="url(#grid-pattern)" />
                </svg>
            </div>
            
            <div className="mx-auto grid max-w-2xl grid-cols-1 gap-x-8 gap-y-16 lg:mx-0 lg:max-w-none lg:grid-cols-2 lg:items-start lg:gap-y-10">
                {/* Left Side: The Problem */}
                <div className="lg:col-span-2 lg:col-start-1 lg:row-start-1 lg:mx-auto lg:grid lg:w-full lg:max-w-7xl lg:grid-cols-2 lg:gap-x-8 lg:px-8">
                    <div className="lg:pr-4">
                        <div className="lg:max-w-lg">
                            <p className="text-base font-semibold leading-7 text-blue-400">The Problem</p>
                            <h1 className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">Support is Fragmented</h1>
                            <p className="mt-6 text-xl leading-8 text-gray-300">
                                Customers bounce between product pages, cart, support tickets, and email tracking. 
                                Support teams drown in "Where is my order?" queries.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Right Side: The Solution (Timeline) - Sticky */}
                <div className="-mt-12 -ml-12 p-12 lg:sticky lg:top-4 lg:col-start-2 lg:row-span-2 lg:row-start-1 lg:overflow-hidden">
                    <div className="bg-gray-800/40 backdrop-blur-xl rounded-2xl p-8 border border-white/10 shadow-2xl">
                        <h3 className="text-2xl font-bold text-white mb-8 border-b border-white/10 pb-4">How Weeb Solves It</h3>
                        <ConfigProvider
                            theme={{
                                algorithm: theme.darkAlgorithm,
                                token: { colorBgBase: 'transparent' }
                            }}
                        >
                            <Timeline items={items} />
                        </ConfigProvider>
                    </div>
                </div>

                {/* Left Side: Detailed Explanation */}
                <div className="lg:col-span-2 lg:col-start-1 lg:row-start-2 lg:mx-auto lg:grid lg:w-full lg:max-w-7xl lg:grid-cols-2 lg:gap-x-8 lg:px-8">
                    <div className="lg:pr-4">
                        <div className="max-w-xl text-base leading-7 text-gray-400 lg:max-w-lg">
                            <p>
                                Traditional chatbots just wait for questions. Weeb acts as a proactive sales and support agent.
                                By integrating directly with your inventory and order database, Weeb turns a support conversation into a sales opportunity.
                            </p>
                            <ul role="list" className="mt-8 space-y-8 text-gray-400">
                                <li className="flex gap-x-3">
                                    <ShoppingOutlined className="mt-1 h-5 w-5 flex-none text-blue-400" />
                                    <span><strong className="font-semibold text-white">Higher Conversion.</strong> Recommendations are based on real-time behavior, not static rules.</span>
                                </li>
                                <li className="flex gap-x-3">
                                    <Truck className="mt-1 h-5 w-5 flex-none text-blue-400" />
                                    <span><strong className="font-semibold text-white">Zero "Where is my order?" tickets.</strong> Proactive updates mean customers never have to ask twice.</span>
                                </li>
                                <li className="flex gap-x-3">
                                    <SyncOutlined className="mt-1 h-5 w-5 flex-none text-blue-400" />
                                    <span><strong className="font-semibold text-white">Instant Refunds.</strong> Automated eligibility checks allow for instant resolution without human delay.</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const BusinessSolutions = () => {
    const industries = [
        {
            title: "E-Commerce & D2C",
            problem: "High cart abandonment, overloaded support.",
            solution: "Acts as a shopping assistant. Recommends products, applies offers, handles refunds.",
            icon: ShoppingCart,
            color: "text-blue-400",
            bg: "bg-blue-400/10"
        },
        {
            title: "Marketplaces",
            problem: "Multiple sellers, complex support logic.",
            solution: "Tracks seller-specific orders. Automates dispute handling per seller policy.",
            icon: Globe,
            color: "text-purple-400",
            bg: "bg-purple-400/10"
        },
        {
            title: "Food Delivery",
            problem: "Late orders, wrong items, angry calls.",
            solution: "Live tracking explanation. Instant coupons for delays. Auto-complaint creation.",
            icon: Package,
            color: "text-orange-400",
            bg: "bg-orange-400/10"
        },
        {
            title: "Healthcare",
            problem: "Patients lost in booking & rescheduling.",
            solution: "Chat-based scheduling. Auto-reminders. Sensitive handoff to staff.",
            icon: Heart,
            color: "text-red-400",
            bg: "bg-red-400/10"
        },
        {
            title: "Fintech",
            problem: "Confusing transaction failures.",
            solution: "Explains failures in plain English. Tracks disputes. Compliance logged.",
            icon: CreditCard,
            color: "text-green-400",
            bg: "bg-green-400/10"
        },
        {
            title: "SaaS",
            problem: "Churn due to feature confusion.",
            solution: "Interactive onboarding. Feature explanation. Automated subscription management.",
            icon: Zap,
            color: "text-yellow-400",
            bg: "bg-yellow-400/10"
        }
    ];

    return (
        <div id="business-solutions" className="py-24 bg-gray-950">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">
                <div className="mx-auto max-w-2xl text-center mb-16">
                    <h2 className="text-base font-semibold leading-7 text-blue-400">Industries</h2>
                    <p className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">Business Applications</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {industries.map((ind, idx) => (
                        <div key={idx} className="bg-white/5 border border-white/5 rounded-2xl p-8 hover:bg-white/10 hover:border-blue-500/30 transition-all group">
                            <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-6 ${ind.bg}`}>
                                <ind.icon className={`h-6 w-6 ${ind.color}`} />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-2">{ind.title}</h3>
                            <p className="text-sm text-gray-500 mb-4 font-mono">Problem: {ind.problem}</p>
                            <p className="text-gray-300 leading-relaxed">{ind.solution}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

const FAQ = () => {
    const items = [
        { key: '1', label: 'What exactly is Weeb?', children: 'Weeb is an AI support agent, not a chatbot. It can talk to users and take real actions like adding items to cart, tracking deliveries, creating complaints, and escalating issues to humans when needed.' },
        { key: '2', label: 'Is it safe to let AI perform actions?', children: 'Yes. Weeb is built with guardrails. Every action is validated, illegal transitions are blocked, and low-confidence actions trigger human handoff. All actions are logged.' },
        { key: '3', label: 'Does Weeb support voice?', children: 'Yes. Weeb works with browser voice input and text-to-speech, so users can talk naturally instead of typing.' },
        { key: '4', label: 'Can Weeb integrate with my backend?', children: 'Absolutely. If your system has APIs (REST/GraphQL), Weeb can use them as tools. No need to rewrite your stack.' },
        { key: '5', label: 'What happens if Weeb fails?', children: 'It immediately escalates to a human agent with full context: conversation history, actions already taken, and confidence scores.' },
    ];

    return (
        <div id="faq" className="py-24 bg-transparent backdrop-blur-2xl">
            <div className="mx-auto max-w-4xl px-6">
                <h2 className="text-3xl font-bold text-white text-center mb-12">Frequently Asked Questions</h2>
                <ConfigProvider
                    theme={{
                        algorithm: theme.darkAlgorithm,
                        token: {
                            colorBgContainer: 'transparent',
                            colorBorder: '#374151', 
                            fontSize: 16
                        }
                    }}
                >
                    <Collapse items={items} bordered={false} size="large" />
                </ConfigProvider>
            </div>
        </div>
    )
}

const CallToAction = () => {
  return (
    <div id="book-demo" className="bg-gray-950 relative overflow-hidden">
        {/* Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-900/20 blur-[120px] rounded-full pointer-events-none"></div>

      <div className="mx-auto max-w-7xl py-24 sm:px-6 sm:py-32 lg:px-8 relative z-10">
        <div className="relative isolate overflow-hidden bg-gray-900/80 backdrop-blur-md px-6 pt-16 shadow-2xl sm:rounded-3xl sm:px-16 md:pt-24 lg:flex lg:gap-x-20 lg:px-24 lg:pt-0 ring-1 ring-white/10">
          
          <div className="mx-auto max-w-md text-center lg:mx-0 lg:flex-auto lg:py-32 lg:text-left">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Stop answering the same questions.<br />
              Start letting Weeb handle them.
            </h2>
            <p className="mt-6 text-lg leading-8 text-gray-300">
              Deploy a production-grade AI agent that integrates with your inventory, orders, and support systems in minutes.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6 lg:justify-start">
              <button className="rounded-md bg-white px-3.5 py-2.5 text-sm font-semibold text-gray-900 shadow-sm hover:bg-gray-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white">
                Book a Live Demo
              </button>
              <Link to="/demo" className="text-sm font-semibold leading-6 text-white hover:text-blue-300 flex items-center gap-1">
                Try the App <ArrowRight size={14} />
              </Link>
            </div>
          </div>
          
          <div className="relative mt-16 h-80 lg:mt-8">
            <img 
                className="absolute top-0 left-0 w-[57rem] max-w-none rounded-md bg-white/5 ring-1 ring-white/10 drop-shadow-2xl" 
                src="https://ui.shadcn.com/placeholder.svg" // Replace with App screenshot
                alt="App screenshot" 
                width={1824} 
                height={1080} 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

const Footer = () => {
    return (
        <footer className="bg-gray-950 py-12 border-t border-white/5">
            <div className="mx-auto max-w-7xl px-6 flex flex-col md:flex-row justify-between items-center gap-6">
                <div className="text-center md:text-left">
                    <span className="text-white font-bold text-2xl block mb-2" style={{ fontFamily: '"Charm", cursive' }}>Weeb</span>
                    <p className="text-sm text-gray-500">
                        &copy; 2026 Weeb AI Inc. All rights reserved.<br/>
                        "Your Always-On AI Support Agent"
                    </p>
                </div>
                <div className="flex gap-6">
                    <a href="https://www.linkedin.com/in/ayushpathak23" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-blue-400 transition-colors">
                        <Linkedin size={24} />
                    </a>
                    <a href="mailto:officialayushp123@gmail.com" className="text-gray-400 hover:text-blue-400 transition-colors">
                        <Mail size={24} />
                    </a>
                    <a href="#" className="text-gray-400 hover:text-white transition-colors">
                        <Github size={24} />
                    </a>
                </div>
            </div>
        </footer>
    )
}

// --- Main Page Component ---

export default function LandingPage() {
  return (
    <div className="bg-gray-950 min-h-screen font-sans selection:bg-blue-500/30">
      <Navbar />
      <Hero />
      <FeaturesBento />
      <ProblemSolutionTimeline />
      <BusinessSolutions />
      <FAQ />
      <CallToAction />
      <Footer />
    </div>
  );
}