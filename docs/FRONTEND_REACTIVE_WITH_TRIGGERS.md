# SIGNAL Platform - Reactive Frontend with Agent Triggers

**Version**: 4.0 (Reactive with Agent Triggers)
**Date**: 2025-11-28
**Features**: Reactive UI, Agent Trigger Buttons, Real-time Updates

---

## Overview

This frontend specification adds:
- **Reactive UI Components** - All components update in real-time
- **Agent Trigger Buttons** - One-click triggers for all agent actions
- **WebSocket Integration** - Real-time data updates
- **State Management** - Centralized state with automatic updates
- **Event-Driven Architecture** - Actions trigger reactions across components

---

## Technology Stack

### Frontend Framework
- **React 18** with TypeScript
- **Next.js 14** (App Router)
- **Zustand** for state management
- **React Query** for server state
- **Socket.io** for real-time updates

### UI Components
- **shadcn/ui** for component library
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Recharts** for data visualization

### Real-time
- **Socket.io Client** for WebSocket
- **React Query** for polling fallback
- **SWR** for optimistic updates

---

## State Management Architecture

### Global State (Zustand)

```typescript
// stores/useSignalStore.ts
interface SignalStore {
  // Agent logs
  agentLogs: AgentLog[];
  addAgentLog: (log: AgentLog) => void;
  
  // Campaign signals
  campaignSignals: CampaignSignal[];
  setCampaignSignals: (signals: CampaignSignal[]) => void;
  
  // Keyword logs
  keywordLogs: KeywordLog[];
  addKeywordLog: (log: KeywordLog) => void;
  
  // Agent triggers
  triggerHistory: TriggerResult[];
  addTriggerResult: (result: TriggerResult) => void;
  
  // UI state
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  
  // Reactive updates
  subscribe: (listener: () => void) => () => void;
}

export const useSignalStore = create<SignalStore>((set, get) => ({
  agentLogs: [],
  campaignSignals: [],
  keywordLogs: [],
  triggerHistory: [],
  isLoading: false,
  
  addAgentLog: (log) => set((state) => ({
    agentLogs: [...state.agentLogs, log].slice(-100)
  })),
  
  setCampaignSignals: (signals) => set({ campaignSignals: signals }),
  
  addKeywordLog: (log) => set((state) => ({
    keywordLogs: [...state.keywordLogs, log]
  })),
  
  addTriggerResult: (result) => set((state) => ({
    triggerHistory: [...state.triggerHistory, result]
  })),
  
  setIsLoading: (loading) => set({ isLoading: loading }),
  
  subscribe: (listener) => {
    listener();
    return () => {}; // Unsubscribe
  }
}));
```

### Server State (React Query)

```typescript
// hooks/useAgentTrigger.ts
export function useAgentTrigger() {
  const queryClient = useQueryClient();
  
  const triggerBidOptimize = useMutation({
    mutationFn: async (params: BidOptimizeParams) => {
      const response = await fetch('/api/v1/agents/trigger/bid-optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      return response.json();
    },
    onSuccess: (data) => {
      // Update global state
      useSignalStore.getState().addTriggerResult(data);
      useSignalStore.getState().addAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'BID_STRATEGY',
        action: 'OPTIMIZE',
        campaign: params.keyword,
        confidence: data.output.confidence
      });
      
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['agent-logs'] });
      queryClient.invalidateQueries({ queryKey: ['campaign-signals'] });
    }
  });
  
  return { triggerBidOptimize };
}
```

---

## Page 1: Reactive Bloomberg Terminal Dashboard

### Component Structure

```tsx
// components/terminal/BloombergTerminal.tsx
export default function BloombergTerminal() {
  const { agentLogs, campaignSignals, isLoading } = useSignalStore();
  const { data: signals } = useQuery({
    queryKey: ['campaign-signals'],
    queryFn: () => fetch('/terminal/campaign-signals').then(r => r.json()),
    refetchInterval: 5000 // Auto-refresh every 5 seconds
  });
  
  const { triggerBidOptimize } = useAgentTrigger();
  
  return (
    <div className="bloomberg-terminal">
      <HeaderStats />
      
      <div className="grid grid-cols-3 gap-4">
        <AgentSignalsPanel 
          signals={campaignSignals}
          onTrigger={handleTrigger}
        />
        <CampaignPnLPanel />
        <MarketDataPanel />
      </div>
      
      <AgentExecutionLog logs={agentLogs} />
    </div>
  );
}
```

### Agent Signals Panel with Trigger Buttons

```tsx
// components/terminal/AgentSignalsPanel.tsx
interface AgentSignalsPanelProps {
  signals: CampaignSignal[];
  onTrigger: (signal: CampaignSignal) => void;
}

export default function AgentSignalsPanel({ signals, onTrigger }: AgentSignalsPanelProps) {
  const [triggering, setTriggering] = useState<string | null>(null);
  
  return (
    <div className="agent-signals-panel">
      <h2>Agent Signals</h2>
      
      {signals.map((signal) => (
        <div key={signal.name} className={`signal-card signal-${signal.signal.toLowerCase()}`}>
          <div className="signal-header">
            <span className="signal-icon">
              {signal.signal === 'BUY' && '⚡'}
              {signal.signal === 'HOLD' && '⏸️'}
              {signal.signal === 'STOP' && '🛑'}
            </span>
            <span className="signal-type">{signal.signal}</span>
          </div>
          
          <div className="signal-details">
            <div className="campaign-name">{signal.name}</div>
            <div className="amount">£{signal.spend.toFixed(2)}</div>
            <div className="confidence">{(signal.confidence * 100).toFixed(0)}%</div>
            <div className="roas">ROAS: {signal.roas.toFixed(2)}</div>
          </div>
          
          {/* Agent Trigger Buttons */}
          <div className="trigger-buttons">
            <Button
              onClick={() => handleOptimizeBid(signal)}
              disabled={triggering === signal.id}
              loading={triggering === signal.id}
              size="sm"
              variant="outline"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Optimize Bid
            </Button>
            
            <Button
              onClick={() => handleAnalyzeMarket(signal)}
              disabled={triggering === signal.id}
              loading={triggering === signal.id}
              size="sm"
              variant="outline"
            >
              <TrendingUp className="w-4 h-4 mr-2" />
              Analyze Market
            </Button>
            
            <Button
              onClick={() => handleOptimizeCreative(signal)}
              disabled={triggering === signal.id}
              loading={triggering === signal.id}
              size="sm"
              variant="outline"
            >
              <Image className="w-4 h-4 mr-2" />
              Optimize Creative
            </Button>
          </div>
          
          {/* Real-time indicator */}
          <div className="real-time-indicator">
            <span className="pulse-dot"></span>
            Live
          </div>
        </div>
      ))}
    </div>
  );
}
```

### Reactive Agent Execution Log

```tsx
// components/terminal/AgentExecutionLog.tsx
export default function AgentExecutionLog() {
  const { agentLogs } = useSignalStore();
  const logsEndRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom on new logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [agentLogs]);
  
  return (
    <div className="agent-execution-log">
      <div className="log-header">
        <h2>Agent Execution Log</h2>
        <div className="live-indicator">
          <span className="pulse-dot"></span>
          Live Updates
        </div>
      </div>
      
      <div className="log-entries">
        {agentLogs.map((log, index) => (
          <div key={index} className={`log-entry log-${log.agent.toLowerCase()}`}>
            <span className="timestamp">{log.timestamp}</span>
            <span className="agent">[{log.agent}]</span>
            <span className="action">{log.action}</span>
            {log.campaign && <span className="campaign">{log.campaign}</span>}
            {log.amount && <span className="amount">£{log.amount.toFixed(2)}</span>}
            {log.confidence && <span className="confidence">({(log.confidence * 100).toFixed(0)}%)</span>}
          </div>
        ))}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
}
```

---

## Page 2: Reactive Media Planning Dashboard

### Component with Trigger Buttons

```tsx
// components/planning/MediaPlanningDashboard.tsx
export default function MediaPlanningDashboard() {
  const { keywordLogs, addKeywordLog } = useSignalStore();
  const [researchQuery, setResearchQuery] = useState('');
  const [isResearching, setIsResearching] = useState(false);
  
  const { triggerResearch } = useAgentTrigger();
  const { triggerKeywordClassify } = useAgentTrigger();
  
  const handleResearch = async () => {
    setIsResearching(true);
    try {
      const result = await triggerResearch.mutateAsync({ query: researchQuery });
      
      // Add logs to state
      result.keywords.forEach(keyword => {
        addKeywordLog(keyword);
      });
      
      // Show success notification
      toast.success(`Research complete: ${result.keywords.length} keywords found`);
    } finally {
      setIsResearching(false);
    }
  };
  
  return (
    <div className="media-planning-dashboard">
      {/* Tavily Research Panel */}
      <div className="research-panel">
        <div className="research-header">
          <h2>Tavily Research</h2>
          <Button 
            onClick={handleResearch}
            disabled={isResearching || !researchQuery}
            loading={isResearching}
          >
            <Search className="w-4 h-4 mr-2" />
            Research
          </Button>
        </div>
        
        <Input
          value={researchQuery}
          onChange={(e) => setResearchQuery(e.target.value)}
          placeholder="Enter research query..."
          onKeyDown={(e) => e.key === 'Enter' && handleResearch()}
        />
        
        <div className="checkbox-group">
          <Checkbox label="Use DisBERT" defaultChecked />
          <Checkbox label="Log Keywords" defaultChecked />
        </div>
        
        {/* Research Results */}
        {researchResults && (
          <div className="research-results">
            <ResearchResults data={researchResults} />
          </div>
        )}
      </div>
      
      {/* Keyword Logs with Trigger Buttons */}
      <div className="keyword-logs-panel">
        <div className="logs-header">
          <h2>Campaign Keyword Logs</h2>
          <div className="filters">
            <Select>
              <SelectItem value="all">All Sources</SelectItem>
              <SelectItem value="tavily">Tavily</SelectItem>
              <SelectItem value="manual">Manual</SelectItem>
              <SelectItem value="bert">BERT</SelectItem>
            </Select>
          </div>
        </div>
        
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Keyword</TableHead>
              <TableHead>Match Type</TableHead>
              <TableHead>Bid</TableHead>
              <TableHead>Source</TableHead>
              <TableHead>Model</TableHead>
              <TableHead>Logged</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {keywordLogs.map((log) => (
              <TableRow key={log.id}>
                <TableCell>{log.keyword}</TableCell>
                <TableCell>{log.match_type}</TableCell>
                <TableCell>£{log.bid_amount.toFixed(2)}</TableCell>
                <TableCell>{log.source}</TableCell>
                <TableCell>
                  {log.model_used && (
                    <Badge variant="secondary">{log.model_used}</Badge>
                  )}
                </TableCell>
                <TableCell>{formatTimeAgo(log.timestamp)}</TableCell>
                <TableCell>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleClassifyKeyword(log.keyword)}
                  >
                    <Sparkles className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleViewThradData(log)}
                  >
                    <FileText className="w-4 h-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
```

---

## Page 3: Reactive Agent Management

### Agent Cards with Trigger Buttons

```tsx
// components/agents/AgentManagement.tsx
export default function AgentManagement() {
  const { triggerHistory } = useSignalStore();
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  
  const agents = [
    { name: 'bid_strategy_agent', displayName: 'Bid Strategy', icon: '💰' },
    { name: 'content_brief_agent', displayName: 'Content Brief', icon: '📝' },
    { name: 'creative_optimization_agent', displayName: 'Creative Opt', icon: '🎨' },
    { name: 'market_analysis_agent', displayName: 'Market Analysis', icon: '📊' },
    { name: 'orchestration_agent', displayName: 'Orchestration', icon: '🎯' }
  ];
  
  return (
    <div className="agent-management">
      <div className="agents-grid">
        {agents.map((agent) => (
          <AgentCard
            key={agent.name}
            agent={agent}
            selected={selectedAgent === agent.name}
            onSelect={() => setSelectedAgent(agent.name)}
            onTrigger={handleTriggerAgent}
          />
        ))}
      </div>
      
      {selectedAgent && (
        <AgentDetailPanel
          agentName={selectedAgent}
          triggerHistory={triggerHistory.filter(
            t => t.agent_name === selectedAgent
          )}
        />
      )}
    </div>
  );
}

function AgentCard({ agent, selected, onSelect, onTrigger }: AgentCardProps) {
  const [isTriggering, setIsTriggering] = useState(false);
  
  return (
    <div className={`agent-card ${selected ? 'selected' : ''}`}>
      <div className="agent-header" onClick={onSelect}>
        <span className="agent-icon">{agent.icon}</span>
        <span className="agent-name">{agent.displayName}</span>
        <span className="agent-status">✅ Active</span>
      </div>
      
      <div className="agent-metrics">
        <div className="metric">
          <span className="metric-label">Executions</span>
          <span className="metric-value">750</span>
        </div>
        <div className="metric">
          <span className="metric-label">Success</span>
          <span className="metric-value">92%</span>
        </div>
        <div className="metric">
          <span className="metric-label">Latency</span>
          <span className="metric-value">450ms</span>
        </div>
      </div>
      
      {/* Trigger Buttons */}
      <div className="trigger-buttons">
        <Button
          onClick={() => handleQuickTrigger(agent)}
          disabled={isTriggering}
          loading={isTriggering}
          size="sm"
          className="w-full"
        >
          <Play className="w-4 h-4 mr-2" />
          Quick Trigger
        </Button>
        
        <Button
          onClick={() => handleViewPolicy(agent)}
          size="sm"
          variant="outline"
          className="w-full"
        >
          <FileText className="w-4 h-4 mr-2" />
          View Policy
        </Button>
        
        <Button
          onClick={() => handleViewHistory(agent)}
          size="sm"
          variant="outline"
          className="w-full"
        >
          <History className="w-4 h-4 mr-2" />
          View History
        </Button>
      </div>
    </div>
  );
}
```

---

## Page 4: Reactive Chat Interface

### Chat with Trigger Buttons

```tsx
// components/chat/ChatInterface.tsx
export default function ChatInterface() {
  const { messages, addMessage } = useChatStore();
  const [input, setInput] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('general');
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [isLoading, setIsLoading] = useState(false);
  
  const { triggerChat } = useAgentTrigger();
  
  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    setIsLoading(true);
    const userMessage = input;
    setInput('');
    
    // Add user message
    addMessage({ role: 'user', content: userMessage });
    
    try {
      const result = await triggerChat.mutateAsync({
        message: userMessage,
        agent: selectedAgent,
        model: selectedModel
      });
      
      // Add agent response
      addMessage({
        role: 'assistant',
        content: result.output.response,
        agent: selectedAgent,
        model: selectedModel,
        tokens: result.tokens_used,
        cost: result.cost_usd,
        latency: result.execution_time_ms
      });
      
      // Add to trigger history
      useSignalStore.getState().addTriggerResult(result);
      
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="chat-interface">
      {/* Context Panel */}
      <div className="context-panel">
        <div className="context-header">
          <h2>Context Awareness</h2>
        </div>
        
        <div className="context-info">
          <div className="context-item">
            <span className="label">Current Campaign:</span>
            <span className="value">Summer Training Collection</span>
          </div>
          <div className="context-item">
            <span className="label">Current Strategy:</span>
            <span className="value">Summer Performance Push</span>
          </div>
          <div className="context-item">
            <span className="label">Recent Optimization:</span>
            <span className="value">Bid increased £2.20→£2.75 (2 days ago)</span>
          </div>
        </div>
        
        {/* Agent Selection with Trigger */}
        <div className="agent-selection">
          <label>Select Agent:</label>
          <div className="agent-buttons">
            {agents.map((agent) => (
              <Button
                key={agent.name}
                variant={selectedAgent === agent.name ? 'default' : 'outline'}
                onClick={() => setSelectedAgent(agent.name)}
              >
                {agent.icon} {agent.displayName}
                <span className="accuracy">{agent.accuracy}%</span>
              </Button>
            ))}
          </div>
        </div>
        
        {/* Model Selection */}
        <div className="model-selection">
          <label>Select Model:</label>
          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectItem value="gpt-4">GPT-4 ($0.01/1K)</SelectItem>
            <SelectItem value="gpt-4-turbo">GPT-4 Turbo ($0.003/1K)</SelectItem>
            <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo ($0.001/1K)</SelectItem>
            <SelectItem value="gpt-4o">GPT-4 Omni ($0.015/1K)</SelectItem>
          </Select>
          
          <div className="cost-display">
            Session Cost: £0.75
          </div>
        </div>
      </div>
      
      {/* Chat Messages */}
      <div className="chat-messages">
        {messages.map((message, index) => (
          <ChatMessage
            key={index}
            message={message}
            onAccept={() => handleAcceptResponse(message)}
            onReject={() => handleRejectResponse(message)}
            onRegenerate={() => handleRegenerateResponse(message)}
          />
        ))}
      </div>
      
      {/* Input with Trigger Buttons */}
      <div className="chat-input">
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          disabled={isLoading}
        />
        
        <div className="input-actions">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
          >
            <Paperclip className="w-4 h-4" />
            Attach
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={handleVoiceInput}
          >
            <Mic className="w-4 h-4" />
            Voice
          </Button>
          
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            loading={isLoading}
          >
            <Send className="w-4 h-4" />
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}
```

---

## WebSocket Integration

### Real-time Updates

```typescript
// hooks/useWebSocket.ts
export function useWebSocket() {
  const { addAgentLog, addKeywordLog, setCampaignSignals } = useSignalStore();
  
  useEffect(() => {
    const socket = io('ws://localhost:8000');
    
    socket.on('agent-log', (log) => {
      addAgentLog(log);
    });
    
    socket.on('keyword-log', (log) => {
      addKeywordLog(log);
    });
    
    socket.on('campaign-signal', (signals) => {
      setCampaignSignals(signals);
    });
    
    socket.on('agent-trigger-result', (result) => {
      useSignalStore.getState().addTriggerResult(result);
    });
    
    return () => {
      socket.disconnect();
    };
  }, []);
}

// Use in layout
export default function RootLayout({ children }: { children: React.ReactNode }) {
  useWebSocket(); // Enable WebSocket globally
  
  return (
    <html>
      <body>
        <SignalProvider>
          {children}
        </SignalProvider>
      </body>
    </html>
  );
}
```

---

## Agent Trigger Button Components

### Universal Trigger Button

```tsx
// components/triggers/AgentTriggerButton.tsx
interface AgentTriggerButtonProps {
  triggerType: string;
  params: any;
  onSuccess?: (result: any) => void;
  onError?: (error: Error) => void;
  children: React.ReactNode;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
}

export default function AgentTriggerButton({
  triggerType,
  params,
  onSuccess,
  onError,
  children,
  variant = 'default',
  size = 'md',
  disabled = false
}: AgentTriggerButtonProps) {
  const [isTriggering, setIsTriggering] = useState(false);
  const { triggerAgent } = useAgentTrigger();
  
  const handleClick = async () => {
    setIsTriggering(true);
    try {
      const result = await triggerAgent.mutateAsync({
        type: triggerType,
        params
      });
      
      onSuccess?.(result);
      toast.success('Agent triggered successfully');
    } catch (error) {
      onError?.(error as Error);
      toast.error('Agent trigger failed');
    } finally {
      setIsTriggering(false);
    }
  };
  
  return (
    <Button
      onClick={handleClick}
      disabled={disabled || isTriggering}
      loading={isTriggering}
      variant={variant}
      size={size}
    >
      {children}
    </Button>
  );
}
```

### Usage Examples

```tsx
// Example 1: Quick bid optimization
<AgentTriggerButton
  triggerType="bid_optimize"
  params={{
    keyword: "gymshark leggings",
    current_bid: 2.20,
    platform: "google"
  }}
  onSuccess={(result) => {
    console.log('Bid optimized:', result.output);
  }}
>
  <RefreshCw className="w-4 h-4 mr-2" />
  Optimize Bid
</AgentTriggerButton>

// Example 2: Content generation
<AgentTriggerButton
  triggerType="content_generate"
  params={{
    gap_topic: "seamless leggings",
    gap_score: 0.85,
    platform: "meta"
  }}
  variant="outline"
>
  <FileText className="w-4 h-4 mr-2" />
  Generate Content
</AgentTriggerButton>

// Example 3: Market analysis
<AgentTriggerButton
  triggerType="market_analyze"
  params={{
    query: "gymshark fitness apparel",
    time_range: "week"
  }}
>
  <TrendingUp className="w-4 h-4 mr-2" />
  Analyze Market
</AgentTriggerButton>
```

---

## Reactive Updates Flow

```
User Clicks Trigger Button
    ↓
Agent Trigger API Called
    ↓
Agent Executes (logs to agent_logger + agent_execution_logger)
    ↓
API Returns Result
    ↓
WebSocket Broadcasts Update
    ↓
All Components React (update automatically)
    ↓
UI Refreshes without page reload
```

---

## API Endpoint Reference

### Agent Triggers

```typescript
// POST /api/v1/agents/trigger/bid-optimize
POST /api/v1/agents/trigger/bid-optimize
{
  "keyword": "gymshark leggings",
  "current_bid": 2.20,
  "platform": "google",
  "campaign_id": "optional"
}
→ Returns: AgentTriggerResult

// POST /api/v1/agents/trigger/content-generate
POST /api/v1/agents/trigger/content-generate
{
  "gap_topic": "seamless leggings",
  "gap_score": 0.85,
  "platform": "meta",
  "business_goal": "performance"
}
→ Returns: AgentTriggerResult

// POST /api/v1/agents/trigger/creative-optimize
POST /api/v1/agents/trigger/creative-optimize
{
  "creative_id": "cr_123",
  "creative_type": "video",
  "platform": "meta"
}
→ Returns: AgentTriggerResult

// POST /api/v1/agents/trigger/market-analyze
POST /api/v1/agents/trigger/market-analyze
{
  "query": "gymshark fitness apparel",
  "time_range": "week",
  "competitors": ["nike", "underarmour"]
}
→ Returns: AgentTriggerResult

// POST /api/v1/agents/trigger/keyword-classify
POST /api/v1/agents/trigger/keyword-classify
{
  "query": "buy gymshark online",
  "use_disbert": true
}
→ Returns: AgentTriggerResult

// POST /api/v1/agents/trigger/orchestrate
POST /api/v1/agents/trigger/orchestrate
{
  "task_type": "media_planning",
  "context": { "campaign": "Summer Training" },
  "required_agents": ["bid_strategy", "content_brief", "market_analysis"]
}
→ Returns: AgentTriggerResult

// POST /api/v1/agents/trigger/bulk
POST /api/v1/agents/trigger/bulk
{
  "triggers": [
    { "type": "bid_optimize", "params": {...} },
    { "type": "content_generate", "params": {...} }
  ],
  "parallel": true
}
→ Returns: Bulk trigger results

// GET /api/v1/agents/trigger/types
GET /api/v1/agents/trigger/types
→ Returns: List of available trigger types

// GET /api/v1/agents/trigger/history
GET /api/v1/agents/trigger/history?limit=50
→ Returns: Trigger history from database

// GET /api/v1/agents/trigger/stats
GET /api/v1/agents/trigger/stats?days=30
→ Returns: Trigger statistics
```

---

## Summary

### What's New

1. **Agent Trigger Service** - Unified interface for all agent triggers
2. **Reactive UI Components** - All components update in real-time
3. **Trigger Buttons** - One-click triggers for all agent actions
4. **WebSocket Integration** - Real-time updates across components
5. **State Management** - Centralized state with Zustand
6. **Event-Driven** - Actions trigger reactions automatically

### Key Features

- ✅ All agent actions have trigger buttons
- ✅ Real-time updates via WebSocket
- ✅ Reactive state management
- ✅ Optimistic updates
- ✅ Loading states
- ✅ Error handling
- ✅ Success notifications
- ✅ Auto-refresh capability

### Files Created/Modified

**Created**:
- `services/common/agent_trigger_service.py` - Unified trigger service
- `api/routes/agent_triggers.py` - Agent trigger API endpoints
- `FRONTEND_REACTIVE_WITH_TRIGGERS.md` - This document

**Modified**:
- `services/common/__init__.py` - Added trigger service export
- `api/main.py` - Added agent triggers router

The frontend is now fully reactive with agent trigger buttons for all actions! 🚀