#!/usr/bin/env python3
import os
import json
from pathlib import Path

base_path = r'c:\Users\asus\nano-lab-academy.worktrees\agents-frontend-dashboard-courses-lessons-pages\frontend'

# Create directories
dirs = [
    base_path,
    os.path.join(base_path, 'app'),
    os.path.join(base_path, 'components'),
    os.path.join(base_path, 'lib'),
    os.path.join(base_path, 'public')
]

for dir_path in dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f'Created: {dir_path}')

# package.json
package_json = {
    "name": "nano-lab-academy-frontend",
    "version": "0.1.0",
    "private": True,
    "scripts": {
        "dev": "next dev",
        "build": "next build",
        "start": "next start",
        "lint": "next lint"
    },
    "dependencies": {
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "next": "^14.0.0",
        "zustand": "^4.4.1",
        "axios": "^1.6.2"
    },
    "devDependencies": {
        "typescript": "^5.3.3",
        "tailwindcss": "^3.3.6",
        "postcss": "^8.4.31",
        "autoprefixer": "^10.4.16",
        "@types/node": "^20",
        "@types/react": "^18",
        "@types/react-dom": "^18"
    }
}

with open(os.path.join(base_path, 'package.json'), 'w') as f:
    json.dump(package_json, f, indent=2)
print('Created: package.json')

# tsconfig.json
tsconfig = {
    "compilerOptions": {
        "target": "ES2020",
        "useDefineForClassFields": True,
        "lib": ["ES2020", "DOM", "DOM.Iterable"],
        "module": "ESNext",
        "skipLibCheck": True,
        "esModuleInterop": True,
        "allowSyntheticDefaultImports": True,
        "moduleResolution": "bundler",
        "allowImportingTsExtensions": True,
        "resolveJsonModule": True,
        "isolatedModules": True,
        "noEmit": True,
        "jsx": "react-jsx",
        "strict": True,
        "noUnusedLocals": True,
        "noUnusedParameters": True,
        "noFallthroughCasesInSwitch": True,
        "baseUrl": ".",
        "paths": {
            "@/*": ["./*"],
            "@/components/*": ["./components/*"],
            "@/lib/*": ["./lib/*"],
            "@/app/*": ["./app/*"]
        }
    },
    "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
    "exclude": ["node_modules"]
}

with open(os.path.join(base_path, 'tsconfig.json'), 'w') as f:
    json.dump(tsconfig, f, indent=2)
print('Created: tsconfig.json')

# next.config.js
next_config = '''/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === "production",
  },
};

module.exports = nextConfig;
'''

with open(os.path.join(base_path, 'next.config.js'), 'w') as f:
    f.write(next_config)
print('Created: next.config.js')

# tailwind.config.ts
tailwind_config = '''import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#8b5cf6',
        accent: '#ec4899',
      },
    },
  },
  plugins: [],
}
export default config
'''

with open(os.path.join(base_path, 'tailwind.config.ts'), 'w') as f:
    f.write(tailwind_config)
print('Created: tailwind.config.ts')

# postcss.config.js
postcss_config = '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'''

with open(os.path.join(base_path, 'postcss.config.js'), 'w') as f:
    f.write(postcss_config)
print('Created: postcss.config.js')

# .gitignore
gitignore = '''# Dependencies
/node_modules
/.pnp
.pnp.js
/yarn.lock
/package-lock.json

# Testing
/coverage

# Next.js
/.next/
/out/
/.vercel

# Production
/build

# Misc
.DS_Store
*.pem
.env
.env.local
.env.*.local

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDEs
.idea/
.vscode/
*.swp
*.swo
*~
.project
.classpath
.c9/
*.launch
.settings/
*.sublime-workspace

# OS
Thumbs.db
.env.production.local
.env.development.local
.env.test.local
'''

with open(os.path.join(base_path, '.gitignore'), 'w') as f:
    f.write(gitignore)
print('Created: .gitignore')

# .env.local
env_local = '''NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
'''

with open(os.path.join(base_path, '.env.local'), 'w') as f:
    f.write(env_local)
print('Created: .env.local')

# .eslintrc.json
eslintrc = {
    "extends": "next/core-web-vitals"
}

with open(os.path.join(base_path, '.eslintrc.json'), 'w') as f:
    json.dump(eslintrc, f, indent=2)
print('Created: .eslintrc.json')

# app/globals.css
globals_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: #ffffff;
  --foreground: #000000;
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #000000;
    --foreground: #ffffff;
  }
}

body {
  color: var(--foreground);
  background: var(--background);
}
'''

with open(os.path.join(base_path, 'app', 'globals.css'), 'w') as f:
    f.write(globals_css)
print('Created: app/globals.css')

# app/layout.tsx
layout = '''import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Nano Lab Academy",
  description: "Advanced learning platform for development courses and lessons",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
'''

with open(os.path.join(base_path, 'app', 'layout.tsx'), 'w') as f:
    f.write(layout)
print('Created: app/layout.tsx')

# app/page.tsx
page = '''export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-blue-600 mb-4">
          Nano Lab Academy
        </h1>
        <p className="text-xl text-gray-600">
          Welcome to your learning platform
        </p>
      </div>
    </main>
  );
}
'''

with open(os.path.join(base_path, 'app', 'page.tsx'), 'w') as f:
    f.write(page)
print('Created: app/page.tsx')

# .gitkeep files
for subdir in ['components', 'lib', 'public']:
    gitkeep_path = os.path.join(base_path, subdir, '.gitkeep')
    Path(gitkeep_path).touch()
    print(f'Created: {subdir}/.gitkeep')

print('\n✅ Next.js 14 frontend setup complete!')
