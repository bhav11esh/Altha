# Medical AI Frontend

React-based frontend for Medical AI, a HIPAA-compliant healthcare assistant powered by CrewAI.

## Features

- **Chat Interface**: Real-time communication with medical AI
- **PHI Detection & Anonymization**: Automatic detection and protection of Protected Health Information
- **Multi-Agent Reasoning**: Visualize reasoning from Diagnostic, Evidence, Pharmacology, and Risk Assessment agents
- **Conversation Management**: Organize conversations by date with sidebar navigation
- **Audit Logging**: Complete audit trail of all actions
- **Dark/Light Theme**: Toggle between themes
- **Mobile Responsive**: Works on desktop, tablet, and mobile
- **File Upload**: Support for PDF, images, and CSV files
- **Context Display**: View previous conversation turns

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **UI Icons**: Lucide React
- **Date Formatting**: date-fns
- **Styling**: CSS with CSS Custom Properties

## Setup

### Prerequisites

- Node.js 16+
- Backend running on `http://localhost:8000`

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

Production build will be in the `dist` directory.

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── components/
│   ├── ChatInterface.jsx       # Main chat UI
│   ├── PHIDetectionModal.jsx   # PHI warning and anonymization
│   ├── ContextDisplay.jsx      # Previous conversation context
│   ├── AgentReasoningDisplay.jsx # Multi-agent reasoning pills
│   ├── AuditLogViewer.jsx      # Audit log explorer
│   ├── ModelSelector.jsx       # Model selection dropdown
│   └── MessageBubble.jsx       # Individual message component
├── App.jsx                     # Main app component
├── main.jsx                    # Entry point
└── index.css                   # Global styles
```

## Key Components

### ChatInterface
Handles message sending, file uploads, PHI detection, and conversation context display.

### PHIDetectionModal
Displays detected PHI items (names, emails, IDs, etc.) with an anonymized preview. Users can choose to anonymize before submission.

### AgentReasoningDisplay
Shows reasoning from multi-agent system in color-coded pills:
- Purple: Diagnostic Agent
- Blue: Evidence Agent
- Green: Pharmacology Agent
- Red: Risk Assessment Agent

### AuditLogViewer
Expandable log entries showing timestamps and action details:
- Message sent
- PHI detected
- Data anonymized
- Model changed

## API Integration

The frontend connects to the backend at `http://localhost:8000` (configurable via `VITE_API_URL`).

### Key Endpoints

- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /conversations` - Create conversation
- `GET /conversations` - List conversations
- `POST /chat` - Send message
- `POST /phi/detect` - Detect PHI
- `POST /phi/anonymize` - Anonymize message
- `GET /audit-logs` - Get audit logs

## Styling

The app uses CSS Custom Properties for theming:

```css
:root {
  --color-bg: #ffffff;
  --color-text: #111827;
  --color-blue: #2563eb;
  /* ... more colors */
}

[data-theme='dark'] {
  /* Dark theme overrides */
}
```

## Authentication

Token-based authentication with JWT:
- Token stored in `localStorage`
- Sent in `Authorization: Bearer <token>` header
- Auto-logout on auth failure

## Mobile Optimization

- Responsive sidebar (collapsible on mobile)
- Touch-friendly buttons and inputs
- Optimized chat display for small screens
- Mobile-first CSS approach

## Performance

- Code splitting via Vite
- Lazy component loading
- Optimized re-renders with React hooks
- Efficient scrolling for message lists

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari 14+, Chrome Mobile)

## Deployment

### Docker

```bash
docker build -t medical-ai-frontend .
docker run -p 5173:5173 -e VITE_API_URL=http://localhost:8000 medical-ai-frontend
```

### Static Hosting

Build and serve the `dist` folder:

```bash
npm run build
# Serve dist folder with any static host (Vercel, Netlify, S3, etc.)
```

## Contributing

1. Follow the component structure pattern
2. Use Tailwind utility classes for styling (via CSS Custom Properties fallback)
3. Keep components focused and reusable
4. Add PropTypes for documentation

## License

MIT
