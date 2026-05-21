#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const basePath = 'frontend';

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
};

fs.writeFileSync(path.join(basePath, 'package.json'), JSON.stringify(packageJson, null, 2));

// Create tsconfig.json
const tsconfig = {
  "compilerOptions": {
    "target": "es2017",
    "lib": ["es2017", "dom", "dom.iterable"],
    "jsx": "preserve",
    "module": "esnext",
    "moduleResolution": "bundler",
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "plugins": [{"name": "next"}],
    "paths": {"@/*": ["./*"]}
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
};

fs.writeFileSync(path.join(basePath, 'tsconfig.json'), JSON.stringify(tsconfig, null, 2));

// Create next.config.js
const nextConfig = `/** @type {import('next').NextConfig} */
const nextConfig = { reactStrictMode: true }
module.exports = nextConfig
`;

fs.writeFileSync(path.join(basePath, 'next.config.js'), nextConfig);

// Create tailwind.config.ts
const tailwindConfig = `import type { Config } from 'tailwindcss'
const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}', './components/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: { extend: {} },
  plugins: []
}
export default config
`;

fs.writeFileSync(path.join(basePath, 'tailwind.config.ts'), tailwindConfig);

// Create postcss.config.js
const postcssConfig = `module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } }
`;

fs.writeFileSync(path.join(basePath, 'postcss.config.js'), postcssConfig);

// Create .gitignore
const gitignore = `/node_modules
/.next
/out
/build
.env*.local
.DS_Store
`;

fs.writeFileSync(path.join(basePath, '.gitignore'), gitignore);

// Create .env.local
const envLocal = `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
`;

fs.writeFileSync(path.join(basePath, '.env.local'), envLocal);

// Create app/globals.css
const globalsCss = `@tailwind base;
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
`;

fs.writeFileSync(path.join(basePath, 'app', 'globals.css'), globalsCss);

// Create app/layout.tsx
const layout = `import type { Metadata } from "next";
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
`;

fs.writeFileSync(path.join(basePath, 'app', 'layout.tsx'), layout);

// Create app/page.tsx
const page = `export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold">Nano Lab Academy</h1>
      <p className="text-gray-600 mt-2">Frontend loading...</p>
    </main>
  );
}
`;

fs.writeFileSync(path.join(basePath, 'app', 'page.tsx'), page);

// Create .gitkeep files
fs.writeFileSync(path.join(basePath, 'components', '.gitkeep'), '');
fs.writeFileSync(path.join(basePath, 'lib', '.gitkeep'), '');
fs.writeFileSync(path.join(basePath, 'public', '.gitkeep'), '');

console.log('✓ Frontend setup complete');
