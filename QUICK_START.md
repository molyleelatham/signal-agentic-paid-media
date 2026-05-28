# SIGNAL Platform - Quick Start Guide

**Last Updated**: 2025-11-28

---

## 🚀 Quick Start

### 1. Start Backend
```bash
cd /Users/molyleelatham/Documents/adtech-hackathon
python3 -m api.main
```
Backend runs on: http://localhost:8000

### 2. Start Frontend
```bash
cd /Users/molyleelatham/Documents/adtech-hackathon/frontend
npm run dev
```
Frontend runs on: http://localhost:5173

### 3. Access the Application
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🎯 Key Features

### Agent Triggers
- ⚡ Bid Optimization
- 📝 Content Generation
- 🎨 Creative Optimization
- 📊 Market Analysis
- 🔤 Keyword Classification (DisBERT)
- 🔍 Tavily Research

### Market Intelligence
- Trending topics with Tavily research
- DisBERT segment classification (A-M)
- Keyword classification
- Volume charts and analytics

### DisBERT Classifications
- **H** - Purchasable Products (HIGH VALUE)
- **J** - Relationships/Personal (HIGHEST PRIORITY)
- **E** - General Guidance (HIGH PRIORITY)
- Plus 8 other classifications (A-G, K-L)

---

## 📝 Common Tasks

### Test Tavily Research
1. Go to Market Intelligence page
2. Enter query: "gymshark fitness trends"
3. Click "🔍 Research"
4. View trending topics and DisBERT segments

### Test Agent Triggers
1. Go to Signal Terminal page
2. Click trigger buttons:
   - ⚡ Optimize Bid
   - 📊 Analyze
   - 🎨 Creative
3. View execution metrics

### Test Keyword Classification
1. Go to Market Intelligence page
2. Select a trending topic
3. Click "Classify with DisBERT"
4. View classification result

---

## 🔧 API Endpoints

### Agent Triggers
```
POST /api/v1/agents/trigger/bid-optimize
POST /api/v1/agents/trigger/content-generate
POST /api/v1/agents/trigger/creative-optimize
POST /api/v1/agents/trigger/market-analyze
POST /api/v1/agents/trigger/keyword-classify
POST /api/v1/agents/trigger/orchestrate
POST /api/v1/agents/trigger/tavily-research
```

### Agent Status
```
GET /api/v1/agents/status
GET /api/v1/agents/trigger-types
```

### Health Check
```
GET /health
```

---

## 📊 Data Models

### DisBERT Segment
```typescript
{
  classification: "H",  // A-M
  classification_name: "purchasable_products",
  tavily_fields: ["google_keywords"],
  mapped_data: {...},
  commercial_intent: 0.95,
  ingestion_priority: 9,
  should_use_as_keywords: true
}
```

### Trending Topic
```typescript
{
  id: "tavily_0_1234567890",
  kw: "Gymshark Seamless Leggings Trend",
  growth: 45,
  vol: "150",
  intensity: "high",
  src: ["T"],
  spark: [10, 15, 12, 18, 22, 28, 25, 30, 35, 40, 45, 50],
  detail: {...}
}
```

---

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is in use
- Verify Python 3.14+ is installed
- Check environment variables in .env

### Frontend won't start
- Check if port 5173 is in use
- Run `npm install` if dependencies missing
- Check Node.js version (18+)

### Tavily research fails
- API key not required (simulated mode enabled)
- Check backend logs for errors
- Verify endpoint is reachable

### Agent triggers fail
- Check agent registration status
- Verify Overmind API key (optional)
- Check agent service logs

---

## 📚 Documentation

### Main Documents
- `PROJECT_SUMMARY.md` - Complete project overview
- `TAVILY_RESEARCH_TRIGGER.md` - Tavily integration
- `TAVILY_TO_DISBERT_MAPPING.md` - DisBERT mapping
- `DISBERT_SEGMENTS_FRONTEND.md` - Frontend implementation
- `FRONTEND_TRIGGERS_IMPLEMENTATION.md` - Frontend triggers

### API Documentation
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## 🔑 Configuration

### Environment Variables
```bash
# Required for production
DATABASE_URL=postgresql://...

# Optional (simulated mode works without these)
OVERMIND_API_KEY=...
TAVILY_API_KEY=...
THRAD_API_KEY=...
CURSOR_API_KEY=...
```

### Frontend Configuration
```bash
# frontend/.env
VITE_API_URL=http://localhost:8000
```

---

## 🎨 UI Features

### Market Intelligence Page
- Section A: Trending topics with Tavily research
- Section B: Detail panel with charts
- Section C: AI queries and suggestions
- DisBERT segments panel (after research)

### Signal Terminal Page
- Agent signal cards
- Trigger buttons with loading states
- Execution metrics display
- Agent status indicators

---

## 📈 Performance

### Expected Response Times
- Agent triggers: 1-3 seconds
- Tavily research: 2-5 seconds
- API health check: < 100ms
- Keyword classification: 1-2 seconds

### Resource Usage
- Backend: ~100-200 MB RAM
- Frontend: ~50-100 MB RAM
- Database: ~50-100 MB (demo data)

---

## 🆘 Getting Help

### Check Logs
- Backend logs: Terminal output
- Frontend logs: Browser console
- Agent logs: Check agent service files

### Common Issues
1. **404 Not Found**: Check router is included in main.py
2. **Import Error**: Check all dependencies installed
3. **Database Error**: Check DATABASE_URL configuration
4. **CORS Error**: Check CORS middleware configuration

---

## ✅ Checklist

### Before Running
- [ ] Python 3.14+ installed
- [ ] Node.js 18+ installed
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Environment variables configured (optional)

### After Setup
- [ ] Backend starts successfully
- [ ] Frontend starts successfully
- [ ] Health check returns 200 OK
- [ ] Can access API docs
- [ ] Can access frontend

### Testing
- [ ] Tavily research works
- [ ] Agent triggers work
- [ ] DisBERT classification works
- [ ] Frontend displays correctly
- [ ] No console errors

---

## 🎯 Next Steps

1. **Explore Features**: Try all agent triggers
2. **Test Research**: Use Tavily research for different queries
3. **View Segments**: Check DisBERT segment classifications
4. **Monitor Performance**: Track execution metrics
5. **Customize**: Modify configuration for your needs

---

**Happy Hacking! 🚀**