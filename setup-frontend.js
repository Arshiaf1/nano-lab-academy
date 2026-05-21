#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

// Use process.argv to allow running from any directory
const basePath = process.env.FRONTEND_PATH || 'c:\\Users\\asus\\nano-lab-academy.worktrees\\agents-frontend-dashboard-courses-lessons-pages\\frontend';

// Create directories
const dirs = [
  basePath,
  path.join(basePath, 'app'),
  path.join(basePath, 'components'),
  path.join(basePath, 'lib'),
  path.join(basePath, 'public')
];

dirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`Created: ${dir}`);
  }
});

// Create package.json
const packageJson = {
  "name": "nano-lab-academy-frontend",
  "version": "0.1.0",
  "private": true,
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
};

fs.writeFileSync(path.join(basePath, 'package.json'), JSON.stringify(packageJson, null, 2));
console.log('Created: package.json');

// Create tsconfig.json
const tsconfig = {
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
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
};

fs.writeFileSync(path.join(basePath, 'tsconfig.json'), JSON.stringify(tsconfig, null, 2));
console.log('Created: tsconfig.json');

// Create next.config.js
const nextConfig = `/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === "production",
  },
};

module.exports = nextConfig;
`;

fs.writeFileSync(path.join(basePath, 'next.config.js'), nextConfig);
console.log('Created: next.config.js');

// Create tailwind.config.ts
const tailwindConfig = `import type { Config } from 'tailwindcss'

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
`;

fs.writeFileSync(path.join(basePath, 'tailwind.config.ts'), tailwindConfig);
console.log('Created: tailwind.config.ts');

// Create postcss.config.js
const postcssConfig = `module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
`;

fs.writeFileSync(path.join(basePath, 'postcss.config.js'), postcssConfig);
console.log('Created: postcss.config.js');

// Create .gitignore
const gitignore = `# Dependencies
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
`;

fs.writeFileSync(path.join(basePath, '.gitignore'), gitignore);
console.log('Created: .gitignore');

// Create .env.local
const envLocal = `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
`;

fs.writeFileSync(path.join(basePath, '.env.local'), envLocal);
console.log('Created: .env.local');

// Create .eslintrc.json
const eslintrc = {
  "extends": "next/core-web-vitals"
};

fs.writeFileSync(path.join(basePath, '.eslintrc.json'), JSON.stringify(eslintrc, null, 2));
console.log('Created: .eslintrc.json');

// Create app/globals.css
const globalsCss = `@tailwind base;
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
`;

fs.writeFileSync(path.join(basePath, 'app', 'globals.css'), globalsCss);
console.log('Created: app/globals.css');

// Create app/layout.tsx
const layout = `import type { Metadata } from "next";
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
`;

fs.writeFileSync(path.join(basePath, 'app', 'layout.tsx'), layout);
console.log('Created: app/layout.tsx');

// Create app/page.tsx
const page = `export default function Home() {
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
`;

fs.writeFileSync(path.join(basePath, 'app', 'page.tsx'), page);
console.log('Created: app/page.tsx');

// Create .gitkeep files to preserve empty directories
fs.writeFileSync(path.join(basePath, 'components', '.gitkeep'), '');
console.log('Created: components/.gitkeep');

fs.writeFileSync(path.join(basePath, 'lib', '.gitkeep'), '');
console.log('Created: lib/.gitkeep');

fs.writeFileSync(path.join(basePath, 'public', '.gitkeep'), '');
console.log('Created: public/.gitkeep');

console.log('\n✅ Next.js 14 frontend setup complete!');
