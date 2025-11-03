# Customer Support Copilot - Frontend

Modern, responsive dashboard for customer support agents and managers built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

### Agent Dashboard
- 📊 Real-time ticket overview and statistics
- 🎫 My Tickets view with filtering and search
- 🤖 AI-suggested replies integration
- ✅ Quick actions (reply, resolve, escalate)
- 📈 Personal performance metrics

### Manager Dashboard
- 👥 Team overview with agent utilization
- 📊 Ticket volume forecasting (LSTM predictions)
- 🎯 Staffing recommendations
- 📋 Agent management interface
- 📈 Real-time analytics and insights

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query (@tanstack/react-query)
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Icons**: Lucide React
- **UI Components**: Custom components with Tailwind

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000`

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment variables:**
   Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── app/                    # Next.js 14 App Router
│   ├── agent/             # Agent dashboard pages
│   ├── manager/           # Manager dashboard pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page (redirects to /agent)
│   ├── providers.tsx      # React Query provider
│   └── globals.css        # Global styles
├── components/
│   ├── ui/                # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── Badge.tsx
│   └── Sidebar.tsx        # Navigation sidebar
├── lib/
│   └── api.ts             # API client & endpoints
├── types/
│   └── index.ts           # TypeScript type definitions
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

## Available Scripts

- `npm run dev` - Start development server (http://localhost:3000)
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## API Integration

The frontend connects to the backend API running on port 8000. All API calls are managed through:

- **`lib/api.ts`** - Axios client with typed endpoints
- **React Query** - Caching, revalidation, and state management

### API Modules:

```typescript
import { ticketsApi, agentsApi, forecastingApi } from '@/lib/api';

// Tickets
const tickets = await ticketsApi.getAll();
const ticket = await ticketsApi.getById('TKT-001');
await ticketsApi.assign('TKT-001', { auto_assign: true });

// Agents
const agents = await agentsApi.getAll();
const stats = await agentsApi.getStats();

// Forecasting
const forecast = await forecastingApi.getDaily(7);
const staffing = await forecastingApi.getStaffing();
```

## Component Usage

### Card Component
```typescript
import { Card, CardHeader } from '@/components/ui/Card';

<Card>
  <CardHeader title="My Tickets" subtitle="5 active tickets" />
  {/* Content */}
</Card>
```

### Button Component
```typescript
import { Button } from '@/components/ui/Button';

<Button variant="primary" size="md">
  Assign Ticket
</Button>
```

### Badge Component
```typescript
import { Badge } from '@/components/ui/Badge';

<Badge variant="danger">HIGH</Badge>
<Badge variant="success">RESOLVED</Badge>
```

## Development

### Adding a New Page

1. Create file in `app/` directory:
   ```typescript
   // app/my-page/page.tsx
   export default function MyPage() {
     return <div>My Page Content</div>;
   }
   ```

2. Add route to sidebar navigation in `components/Sidebar.tsx`

### Adding a New API Endpoint

1. Update `lib/api.ts`:
   ```typescript
   export const myApi = {
     getData: async (): Promise<MyType> => {
       const response = await api.get('/api/my-endpoint');
       return response.data;
     },
   };
   ```

2. Use with React Query:
   ```typescript
   const { data } = useQuery({
     queryKey: ['my-data'],
     queryFn: myApi.getData,
   });
   ```

## Troubleshooting

### Backend Connection Issues

If you see API errors:
1. Ensure backend is running: `python backend/main.py`
2. Check backend is on port 8000
3. Verify CORS is configured in backend
4. Check `.env.local` has correct `NEXT_PUBLIC_API_URL`

### TypeScript Errors

All import errors will resolve after running `npm install`. The project uses strict TypeScript for better type safety.

### Styling Issues

If Tailwind classes aren't working:
1. Restart dev server: `npm run dev`
2. Check `tailwind.config.js` content paths
3. Ensure `globals.css` imports are correct

## Deployment

### Build for Production

```bash
npm run build
npm run start
```

### Deploy to Vercel

```bash
vercel deploy
```

Or connect your GitHub repository to Vercel for automatic deployments.

### Deploy to Netlify

```bash
netlify deploy --prod
```

## Environment Variables

Create `.env.local` for local development:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Analytics
NEXT_PUBLIC_GA_ID=your-ga-id
```

For production, set these in your hosting platform (Vercel, Netlify, etc.)

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit: `git commit -m "Add my feature"`
3. Push branch: `git push origin feature/my-feature`
4. Create Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
- Check backend is running on port 8000
- Review browser console for errors
- Check Network tab for API call failures
- Ensure all environment variables are set

## Next Steps

- [ ] Add authentication/login
- [ ] Implement real-time WebSocket updates
- [ ] Add dark mode toggle
- [ ] Build ticket detail view
- [ ] Create reply interface
- [ ] Add file upload support
- [ ] Implement search and filters
- [ ] Add unit tests
- [ ] Add E2E tests with Playwright
- [ ] Performance optimization

---

**Note:** This is a development preview. The TypeScript errors shown are expected and will resolve after running `npm install`.
