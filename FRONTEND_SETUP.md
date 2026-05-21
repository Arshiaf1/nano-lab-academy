# FRONTEND SETUP INSTRUCTIONS

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager

## Quick Setup

### Option 1: Automated Setup (Recommended)
1. Run the batch/PowerShell script to create directories:
   - Windows CMD: `create-frontend-dirs.bat`
   - Windows PowerShell: `powershell -ExecutionPolicy Bypass -File create-frontend-dirs.ps1`

2. Copy all frontend-specific files from this directory to the `frontend` folder

3. Navigate into the frontend folder and install dependencies:
   ```bash
   cd frontend
   npm install
   ```

### Option 2: Manual Setup
1. Manually create the frontend directory structure:
   ```
   frontend/
   ├── app/
   │   ├── auth/
   │   │   ├── login/
   │   │   └── register/
   │   ├── (protected)/
   │   ├── layout.tsx
   │   ├── page.tsx
   │   └── globals.css
   ├── components/
   ├── lib/
   ├── public/
   ├── styles/
   ├── middleware.ts
   ├── next.config.js
   ├── tailwind.config.ts
   ├── tsconfig.json
   ├── package.json
   └── .env.local
   ```

2. Copy all provided files into their respective locations

3. Run `npm install` in the frontend directory

### Option 3: Using create-next-app (Standard Way)
```bash
npx create-next-app@latest frontend --typescript --tailwind --app --eslint --import-alias --no-git
cd frontend
npm install
```

## Environment Configuration
After setup, create `.env.local` in the frontend folder with:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Running the Project
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Project Structure Created
- **app/**: Next.js 14 App Router
- **components/**: Reusable React components
- **lib/**: Utilities (API client, store, etc.)
- **public/**: Static assets
- **styles/**: Global styles
- **middleware.ts**: Route protection middleware
