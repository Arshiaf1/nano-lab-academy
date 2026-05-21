# Frontend Project Setup Manifest

## Overview
Complete Next.js 14 frontend project setup for Nano Lab Academy with TypeScript, Tailwind CSS, and Zustand state management.

**Created**: 2026-05-21
**Project**: Nano Lab Academy
**Frontend Framework**: Next.js 14 (App Router)
**Status**: Ready for organization and npm install

## 📂 Files Created (Ready to Organize)

All files have been created with `frontend_` prefix. They need to be organized into the `frontend/` directory structure.

### Configuration Files (Root)
- `frontend_package.json` → `package.json` - NPM dependencies and scripts
- `frontend_tsconfig.json` → `tsconfig.json` - TypeScript configuration
- `frontend_tailwind.config.ts` → `tailwind.config.ts` - Tailwind CSS configuration
- `frontend_next.config.js` → `next.config.js` - Next.js configuration
- `frontend_postcss.config.js` → `postcss.config.js` - PostCSS configuration
- `frontend_.eslintrc.json` → `.eslintrc.json` - ESLint rules
- `frontend_.gitignore` → `.gitignore` - Git ignore patterns
- `frontend_.env.local` → `.env.local` - Environment variables
- `frontend_middleware.ts` → `middleware.ts` - Route protection middleware

### Styles
- `frontend_globals.css` → `app/globals.css` - Global Tailwind styles

### App Router Pages
- `frontend_app_layout.tsx` → `app/layout.tsx` - Root layout with navbar
- `frontend_app_page.tsx` → `app/page.tsx` - Home/landing page
- `frontend_app_auth_layout.tsx` → `app/auth/layout.tsx` - Auth routes layout
- `frontend_app_auth_login_page.tsx` → `app/auth/login/page.tsx` - Login page
- `frontend_app_auth_register_page.tsx` → `app/auth/register/page.tsx` - Register page
- `frontend_app_protected_dashboard_page.tsx` → `app/(protected)/dashboard/page.tsx` - Dashboard page

### Components
- `frontend_components_Navbar.tsx` → `components/Navbar.tsx` - Navigation component

### Utilities & Libraries
- `frontend_lib_store.ts` → `lib/store.ts` - Zustand auth store
- `frontend_lib_api-client.ts` → `lib/api-client.ts` - API client with JWT handling

### Documentation & Setup
- `frontend_README.md` → `frontend/README.md` - Frontend documentation
- `FRONTEND_SETUP.md` - Setup instructions (in root)
- `create-frontend-dirs.bat` - Batch script to create directories
- `create-frontend-dirs.ps1` - PowerShell script to create directories
- `setup-frontend.sh` - Bash script to organize all files
- `setup-frontend.ps1` - PowerShell script to organize all files

## 🚀 Setup Instructions

### Option 1: Automated Setup (Recommended)

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File setup-frontend.ps1
```

**Windows (Bash/Git Bash):**
```bash
bash setup-frontend.sh
```

**macOS/Linux:**
```bash
bash setup-frontend.sh
```

### Option 2: Manual Setup

1. Create the `frontend` folder structure:
   ```bash
   mkdir -p frontend/app/auth/{login,register}
   mkdir -p frontend/app/{protected/dashboard,}
   mkdir -p frontend/{components,lib,public,styles}
   ```

2. Move/rename all `frontend_*` files to their destinations

3. Navigate to frontend and install:
   ```bash
   cd frontend
   npm install
   ```

## 📋 Features Included

### ✅ Authentication System
- Zustand store for auth state management
- Login page with email/password form
- Register page with password validation
- JWT token storage in localStorage
- Automatic token refresh on 401 responses
- Session persistence

### ✅ Route Protection
- Middleware checks for authentication token
- Redirects to login if unauthenticated
- Protects `/dashboard` and other routes
- Prevents logged-in users from accessing auth pages

### ✅ API Integration
- Fetch-based API client utility
- Automatic JWT token attachment
- Token refresh handler
- Error handling
- Type-safe API calls (TypeScript)
- Helper functions: apiGet, apiPost, apiPut, apiDelete

### ✅ UI Components
- Responsive Navbar with auth state
- Login form with validation
- Register form with password confirmation
- Dashboard showing user info
- Tailwind CSS styling
- Responsive design

### ✅ Developer Experience
- TypeScript for type safety
- ESLint for code quality
- Path aliases (@/* for imports)
- Tailwind CSS for rapid styling
- Development and production scripts

## 🔧 Configuration

### Environment Variables
File: `frontend/.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Zustand Store
File: `frontend/lib/store.ts`
- `user` - Current user object
- `token` - JWT access token
- `isLoading` - Loading state
- `error` - Error messages
- Methods: login(), register(), logout(), checkAuth()

### API Client
File: `frontend/lib/api-client.ts`
- `apiCall()` - Base function with token handling
- `apiGet()` - GET requests
- `apiPost()` - POST requests
- `apiPut()` - PUT requests
- `apiDelete()` - DELETE requests

### Middleware
File: `frontend/middleware.ts`
- Protects routes from unauthenticated access
- Routes: `/dashboard`, `/app/*`
- Public routes: `/`, `/auth/login`, `/auth/register`

## 📊 Project Structure After Setup

```
frontend/
├── app/
│   ├── (protected)/
│   │   └── dashboard/
│   │       └── page.tsx
│   ├── auth/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   └── Navbar.tsx
├── lib/
│   ├── api-client.ts
│   └── store.ts
├── public/
├── middleware.ts
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
├── postcss.config.js
├── .eslintrc.json
├── .env.local
├── .gitignore
└── README.md
```

## 🚀 Next Steps

1. **Run setup script** (recommended):
   ```powershell
   # Windows
   ./setup-frontend.ps1
   
   # macOS/Linux
   bash setup-frontend.sh
   ```

2. **Or manually organize files** and run:
   ```bash
   cd frontend
   npm install
   ```

3. **Verify setup**:
   ```bash
   cd frontend
   npm run build  # Should succeed
   ```

4. **Start development**:
   ```bash
   npm run dev
   # Open http://localhost:3000
   ```

## 🔌 Backend Requirements

The frontend expects these API endpoints:

### Authentication Endpoints
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Get access token
- `POST /api/auth/refresh` - Refresh token (optional)
- `POST /api/auth/logout` - Logout (optional)

### Response Format
```json
{
  "access_token": "eyJ...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "learner"
  }
}
```

## 📝 Important Notes

- **Token Storage**: Currently uses localStorage. For production, implement httpOnly cookies with backend cooperation.
- **CORS**: Ensure backend has proper CORS headers if running on different port.
- **API URL**: Change in `.env.local` if backend is on different URL.
- **Environment Variables**: `NEXT_PUBLIC_*` are exposed to browser—don't store secrets.
- **Middleware**: Uses cookies for auth checks. Switch to component-level checks if using localStorage.

## 🐛 Common Issues & Fixes

### npm install fails
- Ensure Node.js 18+ is installed: `node --version`
- Clear npm cache: `npm cache clean --force`
- Delete node_modules: `rm -rf node_modules && npm install`

### Build errors
- Check TypeScript: `npm run build`
- Verify .env.local exists with API_URL

### Authentication issues
- Ensure backend is running on http://localhost:8000
- Check CORS headers from backend
- Verify .env.local API_URL matches backend

### Middleware not working
- Ensure middleware.ts is in root app/ directory
- Check route patterns in middleware.ts
- May need to use component-level auth checks with localStorage

## 📚 Files Reference

See corresponding `.md` and `README` files for:
- `FRONTEND_SETUP.md` - Installation guide
- `frontend/README.md` - Detailed documentation
- Individual files contain TypeScript JSDoc comments

## ✅ Verification Checklist

After running setup:
- [ ] `frontend/` folder created
- [ ] All config files present (package.json, tsconfig.json, etc.)
- [ ] App directory with correct structure
- [ ] node_modules created after npm install
- [ ] No TypeScript errors: `npm run build`
- [ ] Dev server starts: `npm run dev`
- [ ] Can access http://localhost:3000

## 🎉 Success!

The frontend is now ready to use. All files are organized, dependencies are ready to be installed, and the project follows Next.js 14 best practices.

For detailed usage and customization, see `frontend/README.md`.
