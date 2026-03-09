import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// Detectar modo producción
const isProduction = process.env.NODE_ENV === 'production'

export default defineConfig({
  base: '/assets/hermes/hermes/',
  
  // ============================================
  // PLUGINS
  // ============================================
  plugins: [
    vue(),
    // PWA: descomenta si necesitas PWA
    // VitePWA({ ... })
  ].filter(Boolean),
  
  // ============================================
  // RESOLVE ALIASES
  // ============================================
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  
  // ============================================
  // BUILD CONFIGURATION (PRODUCCIÓN)
  // ============================================
  build: {
    outDir: resolve(__dirname, '../hermes/public/hermes'),
    emptyOutDir: true,
    target: 'esnext',
    minify: 'terser',
    sourcemap: false,
    
    rollupOptions: {
      input: resolve(__dirname, 'index.html'),
      output: {
        // Nombres estables - versión manejada en API
        entryFileNames: 'assets/[name].js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name].[ext]',
        
        // Separar vendor para mejor caché
        manualChunks: {
          'vendor': ['vue', 'vue-router']
        }
      }
    },
    
    // Assets < 4KB se inlinan
    assetsInlineLimit: 4096,
    
    // Opciones de minificación
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info']
      },
      format: { comments: false }
    },
    
    cssCodeSplit: true,
    cssMinify: true
  },
  
  // ============================================
  // HTML MINIFICATION
  // ============================================
  html: {
    minify: isProduction ? {
      collapseWhitespace: true,
      removeComments: true,
      removeRedundantAttributes: true,
      removeEmptyAttributes: true,
      minifyJS: true,
      minifyCSS: true
    } : false
  },
  
  // ============================================
  // DEV SERVER (DESARROLLO)
  // ============================================
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/assets': { target: 'http://localhost:8000', changeOrigin: true }
    }
  },
  
  // ============================================
  // OPTIMIZACIONES
  // ============================================
  optimizeDeps: {
    include: ['vue', 'vue-router']
  },
  cacheDir: resolve(__dirname, 'node_modules/.vite')
})
