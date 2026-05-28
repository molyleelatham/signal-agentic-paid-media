# Hackathon Demo Script (3 Minutes)

**Theme**: AI-Powered Ad Optimization Platform
**Speaker**: [Your Name]
**Time**: 3 Minutes

---

## [0:00-0:30] The Hook

**[Slide: Marketing Industry Stats]**

"Did you know that global digital marketing spending exceeds **$600 billion** annually? That's over **$1.6 billion every single day**. Yet despite this massive investment, most advertisers struggle with the same fundamental problems: wasted ad spend, poor targeting, and inefficient bid management."

**[Pause for effect]**

"Today, I'm excited to introduce **SIGNAL** - an AI-powered platform that transforms how advertisers optimize their campaigns using intelligent agents and real-time market intelligence."

---

## [0:30-1:00] The Problem

**[Slide: Current Challenges]**

"Here's the reality: Advertisers today face three major challenges. First, **keyword research** is manual and time-consuming. Second, **bid optimization** relies on gut feeling rather than data. And third, **market trends** change faster than teams can react."

"What if we could automate all of this using AI? What if we could not only find trending topics but automatically classify them by commercial intent? What if we could optimize bids in real-time based on market conditions?"

---

## [1:00-1:45] The Solution - SIGNAL Platform

**[Slide: Platform Architecture]**

"Enter SIGNAL. Our platform integrates three powerful technologies:

**First**, we use **Overmind SDK** to orchestrate 5 specialized AI agents - one for bid strategy, one for content generation, one for creative optimization, one for market analysis, and an orchestration agent that coordinates them all.

**Second**, we integrate **Tavily** for real-time web research, discovering trending topics across Reddit, SEO pages, and Google search.

**Third**, we use **DisBERT** - a state-of-the-art classification system that automatically categorizes content into 13 segments, from 'purchasable products' to 'personal reflections', with commercial intent scoring from 10% to 95%."

---

## [1:45-2:30] Live Demo

**[Switch to Live Demo - Market Intelligence Page]**

"Let me show you how it works. I'll search for 'gymshark fitness trends'..."

**[Type query and click Research button]**

"Watch this - in seconds, Tavily researches the web, finds trending topics, and our DisBERT mapper automatically classifies them. See these green segments? These are high-value opportunities - 'purchasable products' with 95% commercial intent. These are the keywords advertisers should bid on."

**[Switch to Signal Terminal Page]**

"Now let's trigger our AI agents. One click to optimize bids, another to generate content, another to analyze the market. Each agent executes independently, tracks tokens used, and provides real-time feedback."

**[Click agent trigger buttons]**

"Our bid optimization agent just calculated optimal bids based on current market conditions. Our content agent generated ad copy tailored to our target audience. All in under 3 seconds."

---

## [2:30-3:00] The Impact

**[Slide: Key Benefits]**

"The impact is significant. Advertisers using SIGNAL can:

- **Reduce wasted spend** by targeting only high-intent keywords
- **Increase ROAS** through data-driven bid optimization
- **Stay ahead of trends** with real-time market intelligence
- **Scale efficiently** with automated agent orchestration

We've built a platform that doesn't just optimize ads - it transforms how advertisers think about marketing. From manual guessing to AI-driven precision."

**[Slide: Thank You]**

"Thank you. SIGNAL - the future of intelligent advertising."

---

## Demo Checklist

### Before Demo
- [ ] Backend running on localhost:8000
- [ ] Frontend running on localhost:5173
- [ ] Market Intelligence page loaded
- [ ] Signal Terminal page loaded
- [ ] Tavily research tested
- [ ] Agent triggers tested

### During Demo
- [ ] Show marketing stats slide (30s)
- [ ] Explain the problem (30s)
- [ ] Show architecture slide (45s)
- [ ] Live demo Tavily research (30s)
- [ ] Show DisBERT segments (15s)
- [ ] Live demo agent triggers (30s)
- [ ] Show benefits slide (30s)

### Key Talking Points
- "$600 billion annual marketing spend"
- "Real-time market intelligence"
- "AI agent orchestration with Overmind"
- "DisBERT classification with commercial intent"
- "Automated bid optimization"
- "3-second agent execution"

### Backup Plans
- If Tavily fails: Mention simulated mode works without API key
- If agents fail: Show logs and error handling
- If frontend slow: Mention it's development build
- If network issues: Have screenshots ready

---

## Slide Outline

### Slide 1: Title
- SIGNAL Platform
- AI-Powered Ad Optimization
- [Your Name]

### Slide 2: The Problem
- $600B+ annual marketing spend
- Manual keyword research
- Gut-based bid decisions
- Slow reaction to trends

### Slide 3: The Solution
- Overmind SDK - Agent Orchestration
- Tavily - Real-time Research
- DisBERT - Content Classification
- FastAPI + React - Tech Stack

### Slide 4: Architecture
- 5 AI Agents
- Reactive Frontend
- Real-time Intelligence
- Trading System

### Slide 5: Live Demo
- Market Intelligence Page
- Tavily Research
- DisBERT Segments
- Agent Triggers

### Slide 6: Key Benefits
- Reduce wasted spend
- Increase ROAS
- Stay ahead of trends
- Scale efficiently

### Slide 7: Thank You
- SIGNAL Platform
- Future of Intelligent Advertising
- Contact/GitHub

---

## Technical Notes for Demo

### Tavily Research Demo
```bash
# Query to use: "gymshark fitness trends"
# Expected: 3 trending topics, DisBERT segments
# Highlight: H (95% intent), J (70% intent), E (60% intent)
```

### Agent Triggers Demo
```bash
# Trigger: Bid Optimize
# Expected: Success response with execution time
# Highlight: < 3 second execution

# Trigger: Content Generate
# Expected: Content brief generation
# Highlight: Token usage tracking

# Trigger: Market Analyze
# Expected: Market analysis results
# Highlight: Comprehensive insights
```

### Performance Metrics
- Tavily research: 2-5 seconds
- Agent execution: 1-3 seconds
- Total demo time: < 30 seconds
- UI response: < 100ms

---

## Audience Engagement

### Questions to Ask
- "How do you currently optimize your ad bids?"
- "How do you discover trending topics?"
- "How much time do you spend on keyword research?"

### Interactive Elements
- Live typing in search bar
- Clicking trigger buttons
- Scrolling through segments
- Hovering over charts

### Key Takeaways
1. Marketing spends $600B+ annually
2. SIGNAL automates optimization with AI
3. Real-time intelligence + agent orchestration
4. Commercial intent classification
5. 3-second agent execution

---

**Good luck with your demo! 🚀**