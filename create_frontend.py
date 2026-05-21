#!/usr/bin/env python3
import os
import json
from pathlib import Path

base_path = r'frontend'

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
        "typescript": "^5.3.3",
        "tailwindcss": "^3.3.6",
        "postcss": "^8.4.31",
        "autoprefixer": "^10.4.16",
        "zustand": "^4.4.1",
        "axios": "^1.6.2"
    },
    "devDependencies": {
        "@types/node": "^20.10.0",
        "@types/react": "^18.2.37",
        "@types/react-dom": "^18.2.15"
    }
}

with open(os.path.join(base_path, 'package.json'), 'w') as f:
    json.dump(package_json, f, indent=2)

# tsconfig.json
tsconfig = {
    "compilerOptions": {
        "target": "es2017",
        "lib": ["es2017", "dom", "dom.iterable"],
        "jsx": "preserve",
        "module": "esnext",
        "moduleResolution": "bundler",
        "allowJs": True,
        "skipLibCheck": True,
        "strict": True,
        "forceConsistentCasingInFileNames": True,
        "noEmit": True,
        "esModuleInterop": True,
        "resolveJsonModule": True,
        "isolatedModules": True,
        "plugins": [{"name": "next"}],
        "paths": {"@/*": ["./*"]}
    },
    "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
    "exclude": ["node_modules"]
}

with open(os.path.join(base_path, 'tsconfig.json'), 'w') as f:
    json.dump(tsconfig, f, indent=2)

# next.config.js
next_config = '''/** @type {import('next').NextConfig} */
const nextConfig = { reactStrictMode: true }
module.exports = nextConfig
'''

with open(os.path.join(base_path, 'next.config.js'), 'w') as f:
    f.write(next_config)

# tailwind.config.ts
tailwind_config = '''import type { Config } from 'tailwindcss'
const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}', './components/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: { extend: {} },
  plugins: []
}
export default config
'''

with open(os.path.join(base_path, 'tailwind.config.ts'), 'w') as f:
    f.write(tailwind_config)

# postcss.config.js
postcss_config = '''module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } }
'''

with open(os.path.join(base_path, 'postcss.config.js'), 'w') as f:
    f.write(postcss_config)

# .gitignore
gitignore = '''/node_modules
/.next
/out
/build
.env*.local
.DS_Store
'''

with open(os.path.join(base_path, '.gitignore'), 'w') as f:
    f.write(gitignore)

# .env.local
env_local = '''NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
'''

with open(os.path.join(base_path, '.env.local'), 'w') as f:
    f.write(env_local)

# app/globals.css
globals_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

html {
  scroll-behavior: smooth;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
}
'''

with open(os.path.join(base_path, 'app', 'globals.css'), 'w') as f:
    f.write(globals_css)

# app/layout.tsx
layout = '''import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Nano Lab Academy",
  description: "Learn laboratory science the practical way",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900">
        {children}
      </body>
    </html>
  );
}
'''

with open(os.path.join(base_path, 'app', 'layout.tsx'), 'w') as f:
    f.write(layout)

# app/page.tsx
page = '''export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold">Nano Lab Academy</h1>
      <p className="text-gray-600 mt-2">Frontend loading...</p>
    </main>
  );
}
'''

with open(os.path.join(base_path, 'app', 'page.tsx'), 'w') as f:
    f.write(page)

# .gitkeep files
for subdir in ['components', 'lib', 'public']:
    gitkeep_path = os.path.join(base_path, subdir, '.gitkeep')
    Path(gitkeep_path).touch()

print('✓ Frontend setup complete')
