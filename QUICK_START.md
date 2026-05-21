# 🚀 Frontend Setup Quick Start Guide

## The Fastest Way to Get Started

### 1️⃣ Run One Command (Choose Your OS)

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File setup-frontend.ps1
```

**Windows (CMD):**
```cmd
create-frontend-dirs.bat
```

**macOS/Linux (Bash):**
```bash
bash setup-frontend.sh
```

### 2️⃣ Start Development Server
```bash
cd frontend
npm run dev
```

### 3️⃣ Open Browser
Visit: **http://localhost:3000**

---

## 📋 What Gets Created

✅ **Next.js 14 App Router** - Modern React framework  
✅ **TypeScript** - Full type safety  
✅ **Tailwind CSS** - Utility-first styling  
✅ **Zustand Store** - Auth state management  
✅ **JWT Authentication** - Secure login/register  
✅ **Route Protection** - Middleware guards  
✅ **API Client** - Smart fetch wrapper  
✅ **Responsive UI** - Mobile-first design  

---

## 🔧 Project Structure

```
frontend/
├── app/                              # Next.js App Router
│   ├── (protected)/dashboard/        # Protected routes
│   ├── auth/login/register/          # Auth pages
│   ├── layout.tsx                    # Root layout
│   └── page.tsx                      # Home page
├── components/Navbar.tsx             # Navigation
├── lib/
│   ├── store.ts                      # Zustand auth store
│   └── api-client.ts                 # API wrapper
├── middleware.ts                     # Route protection
└── [config files]
```

---

## 🔑 Key Features

### Login/Register
- Email/password forms
- Form validation
- Error handling
- Redirect on success

### Authentication
- JWT tokens in localStorage
- Automatic token refresh on 401
- Session persistence on page reload
- Automatic logout on refresh failure

### Protected Routes
- `/dashboard` - User dashboard (requires auth)
- `/auth/login` - Login page (public)
- `/auth/register` - Register page (public)
- `/` - Home page (public)

### API Integration
```typescript
// Automatic token attachment and refresh
import { apiGet, apiPost } from '@/lib/api-client';

const data = await apiGet('/courses');
const user = await apiPost('/auth/login', { email, password });
```

---

## 🌍 Environment

Create `.env.local` after setup (or script does it):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## 🎯 Common Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

---

## 🔗 Backend Integration

### Expected Endpoints

```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh      (optional)
```

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

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| npm install fails | Update Node.js to 18+ |
| Build errors | Check `.env.local` exists |
| 401 on login | Ensure backend is running |
| Can't find modules | Run `npm install` again |
| Middleware not working | Restart dev server |

---

## 📚 Full Documentation

- **Detailed Setup**: See `FRONTEND_SETUP.md`
- **Project Overview**: See `frontend/README.md`
- **Complete Manifest**: See `FRONTEND_MANIFEST.md`
- **Technical Details**: See individual `.tsx` files with comments

---

## ✨ What's Included

### Components
- **Navbar** - Navigation with auth state
- **LoginForm** - Email/password login
- **RegisterForm** - Email/password/name registration
- **Dashboard** - Protected user dashboard

### Utilities
- **Zustand Store** - Global auth state
- **API Client** - Fetch wrapper with JWT
- **Middleware** - Route protection

### Styling
- **Tailwind CSS** - Full utility CSS framework
- **Responsive Design** - Mobile-first layout
- **Dark Mode Ready** - Can extend easily

---

## 🎓 Learning Resources

- [Next.js 14 Docs](https://nextjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Guide](https://tailwindcss.com/docs)
- [Zustand Docs](https://github.com/pmndrs/zustand)

---

## 🎉 Ready to Go!

After running the setup script:
1. Dev server runs at **http://localhost:3000**
2. Try logging in (requires backend)
3. Check `/dashboard` after login
4. Explore the code and customize!

---

**Questions?** Check the detailed README files or look at the source code - it's fully commented!
