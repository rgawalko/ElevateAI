# 🎨 Elevate AI Frontend

React + TypeScript frontend for the Elevate AI productivity and wellness application.

## 🏗️ Project Structure

```
frontend/
├── src/                    # Source code
│   ├── components/         # Reusable React components
│   ├── pages/             # Page components
│   ├── services/          # API services and data fetching
│   ├── hooks/             # Custom React hooks
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── styles/            # Global styles and themes
│   ├── assets/            # Static assets (images, icons)
│   ├── App.tsx            # Main App component
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global CSS styles
├── public/                # Public static files
├── dist/                  # Build output directory
├── node_modules/          # Dependencies
├── index.html             # HTML template
├── package.json           # Project dependencies and scripts
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
└── eslint.config.js       # ESLint configuration
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm run dev
```
The application will be available at `http://localhost:5173`

### Build
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 🛠️ Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS v4** - Utility-first CSS framework (latest version)
- **@tailwindcss/postcss** - PostCSS plugin for Tailwind v4
- **Lucide React** - Icon library
- **ESLint** - Code linting
- **PostCSS** - CSS processing

## 📱 Features

- **Dashboard** - Overview of productivity metrics
- **Activity Tracking** - Log and monitor daily activities
- **AI Schedule Generation** - Intelligent schedule optimization
- **Goal Management** - Set and track personal goals
- **Insights** - AI-powered productivity insights
- **Responsive Design** - Works on desktop and mobile
- **Dark/Light Mode** - Theme switching support

## 🔗 Backend Integration

The frontend communicates with the FastAPI backend at:
- **Development**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

## 📝 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## 🎨 Styling

The project uses Tailwind CSS v4 for styling with:
- **CSS-based configuration** - Configuration is now in `src/index.css` using `@theme`
- **Custom color palette** - Primary, secondary, success, warning, and danger colors
- **Responsive design utilities** - Mobile-first responsive design
- **Component-based styling** - Utility classes for component styling
- **Dark mode support** - Built-in dark mode capabilities
- **Custom font family** - Inter font for modern typography

### Tailwind CSS v4 Changes
- Configuration moved from `tailwind.config.js` to CSS using `@theme` directive
- Uses `@tailwindcss/postcss` plugin instead of direct `tailwindcss` plugin
- Import statement changed to `@import "tailwindcss"` in CSS

## 📦 Key Dependencies

- `react` - React library
- `react-dom` - React DOM rendering
- `typescript` - TypeScript support
- `vite` - Build tool
- `tailwindcss` - CSS framework
- `lucide-react` - Icons
- `@types/*` - TypeScript definitions

## 🔧 Configuration Files

- `vite.config.ts` - Vite build configuration
- `tsconfig.json` - TypeScript compiler options
- `tailwind.config.js` - Tailwind CSS customization
- `postcss.config.js` - PostCSS plugins
- `eslint.config.js` - ESLint rules

## 🚀 Deployment

The frontend can be deployed to any static hosting service:
- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront

Build the project and deploy the `dist/` folder.

## 🤝 Development Guidelines

1. **Components** - Create reusable components in `src/components/`
2. **Pages** - Page-level components in `src/pages/`
3. **Types** - Define TypeScript interfaces in `src/types/`
4. **Services** - API calls in `src/services/`
5. **Hooks** - Custom hooks in `src/hooks/`
6. **Utils** - Helper functions in `src/utils/`

## 📄 License

This project is part of the Elevate AI application.
