# UTI Mutual Fund FAQ Assistant - Frontend

A modern React + TailwindCSS UI for the UTI Mutual Fund FAQ Assistant.

## Setup

```bash
cd frontend
npm install
npm run dev
```

Opens at http://localhost:3000

## Project Structure

- `src/App.jsx` - Main application component
- `src/components/` - Modular components:
  - `Sidebar.jsx` - Info section with warning, welcome, and example questions
  - `ChatWindow.jsx` - Chat message display area
  - `MessageBubble.jsx` - Individual message component with sources
  - `InputBar.jsx` - Fixed input bar at bottom
- `src/index.css` - TailwindCSS setup
- `tailwind.config.js` - TailwindCSS configuration
- `vite.config.js` - Vite configuration with backend proxy

## Features

- Left sidebar with info section, warning banner, welcome text, and example questions
- Right chat area with message bubbles (user right, bot left)
- Fixed bottom input bar with text field and send button
- Auto-scroll to latest message
- Source attribution for bot responses
- Soft colors, rounded cards, subtle shadows
- Responsive design
