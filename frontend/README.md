# Frontend - UTI Mutual Fund Factual Chatbot

React + Vite + TailwindCSS frontend for the UTI Mutual Fund chatbot.

> For complete project documentation, see [main README](../README.md)

## Quick Start

```bash
npm install
npm run dev
```

Runs on `http://localhost:3001`

## Component Structure

```
src/
├── components/
│   ├── Sidebar.jsx        # Left panel with suggestions
│   ├── ChatWindow.jsx     # Message display area
│   ├── MessageBubble.jsx  # Individual messages
│   └── InputBar.jsx       # Bottom input field
├── App.jsx               # Main app component
└── index.css             # TailwindCSS styles
```

## Features

✅ **Mobile-First Design**
- Fixed headers on mobile
- Auto-opening sidebar on first visit
- Responsive layout

✅ **User Experience**
- Suggested questions in sidebar
- Source attribution for responses
- Auto-scroll to latest message
- Loading states

✅ **Modern UI**
- TailwindCSS styling
- Gradient accents
- Rounded cards with shadows
- Paper plane send button

## Environment Variables

**Development (.env):**
```
VITE_API_URL=http://localhost:5000
```

**Production (.env.production):**
```
VITE_API_URL=https://mutualfundchatbot-production.up.railway.app
```

## Build for Production

```bash
npm run build
```

Output in `dist/` directory.

## Deployment

Auto-deploys to Vercel on push to main branch.
