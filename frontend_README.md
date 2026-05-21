# 🎓 Nano Lab Academy Frontend

A modern Next.js 14 frontend for the Nano Lab Academy platform with TypeScript, Tailwind CSS, and Zustand state management.

## 📋 Features

- **Next.js 14 App Router** - Modern React framework
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Zustand** - Lightweight state management
- **JWT Authentication** - Secure API communication
- **Route Protection** - Middleware-based route guarding
- **API Client** - Fetch wrapper with token management and refresh logic
- **Responsive Design** - Mobile-first UI

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. **Navigate to the project root:**
   ```bash
   cd nano-lab-academy
   ```

2. **Create the frontend folder and initialize the project:**
   
   **Option A: Using provided scripts (Windows)**
   ```bash
   # Run the batch script to create directories
   create-frontend-dirs.bat
   
   # Or using PowerShell
   powershell -ExecutionPolicy Bypass -File create-frontend-dirs.ps1
   ```
   
   **Option B: Manual setup**
   ```bash
   mkdir frontend
   cd frontend
   ```

3. **Copy frontend files from root to `frontend` folder:**
   - Rename `frontend_*.json` → `*.json`
   - Rename `frontend_*.ts` → `*.ts`
   - Rename `frontend_*.tsx` → `*.tsx`
   - Rename `frontend_*.css` → `*.css`
   - Rename `frontend_*.js` → `*.js`
   - Rename `frontend_.env.local` → `.env.local`
   - Rename `frontend_.gitignore` → `.gitignore`
   - Rename `frontend_.eslintrc.json` → `.eslintrc.json`
   
   Or use the provided setup script in VS Code or terminal.

4. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

5. **Verify environment configuration:**
   ```bash
   cat .env.local
   ```
   Should show: `NEXT_PUBLIC_API_URL=http://localhost:8000/api`

6. **Start the development server:**
   ```bash
   npm run dev
   ```

Visit `http://localhost:3000` in your browser.

## 📁 Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── (protected)/              # Protected routes group
│   │   └── dashboard/
│   │       └── page.tsx          # Dashboard page
│   ├── auth/                     # Authentication routes
│   │   ├── login/
│   │   │   └── page.tsx          # Login page
│   │   ├── register/
│   │   │   └── page.tsx          # Register page
│   │   └── layout.tsx            # Auth layout
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Home page
│   └── globals.css               # Global styles
├── components/                   # Reusable components
│   └── Navbar.tsx               # Navigation component
├── lib/                         # Utilities and helpers
│   ├── api-client.ts            # Fetch wrapper with JWT handling
│   └── store.ts                 # Zustand auth store
├── public/                      # Static assets
├── middleware.ts                # Next.js middleware for route protection
├── package.json                 # Dependencies
├── tsconfig.json               # TypeScript config
├── tailwind.config.ts          # Tailwind CSS config
├── next.config.js              # Next.js config
├── postcss.config.js           # PostCSS config
├── .eslintrc.json              # ESLint config
├── .env.local                  # Environment variables
└── .gitignore                  # Git ignore rules
```

## 🔐 Authentication Flow

### Login/Register
1. User submits email and password on `/auth/login` or `/auth/register`
2. API client sends credentials to backend (`/api/auth/login` or `/api/auth/register`)
3. Backend returns `access_token` and user data
4. Token and user are stored in localStorage
5. Zustand store is updated
6. User is redirected to `/dashboard`

### Protected Routes
- **Middleware** (`middleware.ts`) checks for token on every request
- If no token and route is protected → redirect to `/auth/login`
- If token exists and user tries to access `/auth/login` → redirect to `/dashboard`

### Token Refresh
- API client detects 401 responses
- Automatically attempts token refresh via `/api/auth/refresh`
- Retries original request with new token
- If refresh fails, user is logged out

## 📚 Key Files Explanation

### `lib/store.ts`
Zustand store managing auth state:
- `user` - Current user object
- `token` - JWT access token
- `isLoading` - Loading state for async operations
- `error` - Error messages
- Methods: `login()`, `register()`, `logout()`, `checkAuth()`

### `lib/api-client.ts`
Fetch wrapper providing:
- `apiCall()` - Base function with token attachment and refresh logic
- `apiGet()` - Shorthand for GET requests
- `apiPost()` - Shorthand for POST requests
- `apiPut()` - Shorthand for PUT requests
- `apiDelete()` - Shorthand for DELETE requests

All functions automatically:
- Attach `Authorization: Bearer <token>` header
- Handle token refresh on 401
- Parse JSON responses

### `middleware.ts`
Next.js middleware for route protection:
- Checks if token exists in cookies
- Redirects unauthenticated users to `/auth/login`
- Prevents logged-in users from accessing auth pages

Note: Middleware works with cookies. To use localStorage-based tokens, move auth checks to component level using `useEffect`.

### `components/Navbar.tsx`
Navigation component showing:
- Logo and site name
- User email (if logged in)
- Links to Dashboard and Logout (if logged in)
- Links to Login and Register (if not logged in)

Uses `'use client'` directive for client-side interactivity.

## 🔧 Customization

### Change API URL
Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://your-api-url/api
```

### Add More Routes
1. Create folder in `app/` directory
2. Add `page.tsx` or `layout.tsx`
3. Add to `middleware.ts` if protection needed

### Customize Authentication
Edit `lib/store.ts` to:
- Add role-based checks
- Implement logout on API errors
- Add persistence strategies (httpOnly cookies, etc.)

## 🚀 Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Run ESLint
npm run lint
```

## 🔌 API Integration

Backend should provide these endpoints:

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Get access token
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Invalidate token (optional)

### Response Format
```json
{
  "access_token": "eyJhbGc...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "learner"
  }
}
```

## 📦 Dependencies

- **react** ^18.3.1 - UI library
- **react-dom** ^18.3.1 - React DOM rendering
- **next** ^14.1.0 - React framework
- **zustand** ^4.4.7 - State management
- **tailwindcss** ^3.4.1 - CSS framework
- **typescript** ^5.3.3 - Type safety

See `package.json` for full list.

## 🧪 Testing

To test the authentication flow:

1. **Start backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test flow:**
   - Visit `http://localhost:3000`
   - Click "Register" and create an account
   - Login with credentials
   - Access `/dashboard`
   - Click "Logout"

## 🐛 Troubleshooting

### Issue: "NEXT_PUBLIC_API_URL is not defined"
**Solution:** Ensure `.env.local` exists in the `frontend` folder with the correct value.

### Issue: "Cannot find module '@/lib/store'"
**Solution:** Verify that:
- `tsconfig.json` has path mapping: `"@/*": ["./*"]`
- Files are in correct locations

### Issue: Middleware not protecting routes
**Solution:** Check that:
- `middleware.ts` is in the root of `app/` directory
- Route patterns match expected paths
- Cookies are being set correctly (or use localStorage instead)

### Issue: 401 errors after login
**Solution:** Backend may not support token refresh. Remove the refresh logic in `lib/api-client.ts` or implement it on the backend.

## 📖 Additional Resources

- [Next.js 14 Documentation](https://nextjs.org/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Zustand Documentation](https://github.com/pmndrs/zustand)

## 📝 Notes

- **Token Storage**: Currently using `localStorage` for simplicity. For production, consider httpOnly cookies with backend cooperation.
- **Environment Variables**: `NEXT_PUBLIC_*` variables are exposed to the browser. Don't store secrets in them.
- **CORS**: If API is on different domain/port, ensure backend has proper CORS headers.
- **Authentication**: Uses JWT tokens. Ensure backend validates tokens on protected endpoints.

---

**Built for Nano Lab Academy** 🧪
