# Frontend - Job Recommendation SaaS

Next.js React frontend for the job recommendation platform with Tailwind CSS and shadcn/ui components.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local

# Run development server
npm run dev
```

Application will be available at `http://localhost:3000`

## 📁 Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   ├── dashboard/          # Dashboard page
│   ├── jobs/               # Job browse page
│   ├── applications/       # Application tracker
│   ├── analytics/          # Analytics dashboard
│   ├── settings/           # Settings page
│   ├── login/              # Login page
│   └── globals.css         # Global styles
├── components/
│   ├── Navbar.tsx          # Navigation bar
│   ├── JobCard.tsx         # Job card component
│   ├── JobList.tsx         # Job list with pagination
│   ├── JobModal.tsx        # Job detail modal
│   └── FilterPanel.tsx     # Job filters
├── lib/
│   ├── api.ts              # API client (axios)
│   ├── store.ts            # State management (Zustand)
│   └── utils.ts            # Utility functions
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 🔧 Configuration

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## 📦 Tech Stack

- **Framework**: Next.js 15 + React 19
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Server State**: React Query (@tanstack/react-query)
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Notifications**: React Hot Toast

## 🎨 Pages

| Page | Purpose |
|------|---------|
| `/` | Landing page |
| `/login` | Authentication |
| `/dashboard` | Overview and pipeline control |
| `/jobs` | Browse and search jobs |
| `/applications` | Track saved/applied jobs |
| `/analytics` | Job market insights |
| `/settings` | User preferences |

## 🧩 Components

### Core Components
- **Navbar** - Top navigation with user menu
- **JobCard** - Individual job card with status
- **JobList** - Paginated job listing with filters
- **JobModal** - Job detail modal with actions
- **FilterPanel** - Sidebar with category/location/type/source filters

## 🔌 API Integration

All API calls go through `/lib/api.ts` which wraps the backend endpoints:

- **jobsAPI** - Job search and detail
- **applicationsAPI** - Saved/applied job tracking
- **pipelineAPI** - Job collection pipeline
- **statsAPI** - Analytics data

## 🎯 State Management

**Zustand Stores in `/lib/store.ts`:**
- **useAuthStore** - User authentication state
- **useFilterStore** - Job filter state
- **useUIStore** - UI state (sidebar, modals)

## 📝 Development

### Add a new page
```bash
mkdir -p app/your-page
touch app/your-page/page.tsx
```

### Add a new component
```bash
touch components/YourComponent.tsx
```

### Build
```bash
npm run build
npm start
```

## 🚀 Deployment

### Vercel (Recommended)
```bash
vercel deploy
```

### Docker
```bash
docker build -f Dockerfile.frontend -t jobfrontend .
docker run -p 3000:3000 jobfrontend
```

## 🔐 Authentication

Currently set up for Supabase Auth integration. Once connected:
1. Users sign in via Supabase
2. JWT token stored in localStorage
3. Token sent in `Authorization: Bearer` header for API requests

## 📱 Responsive Design

All pages are built with mobile-first responsive design:
- Mobile: 320px+
- Tablet: 768px+
- Desktop: 1024px+

## 🛠️ Environment Variables

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key |

## 📚 More Info

- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Zustand Docs](https://zustand-demo.vercel.app/)
- [React Query Docs](https://tanstack.com/query/latest)
