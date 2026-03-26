import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  build: {
    // Forza Vite a sputare i file nella cartella di Flask
    outDir: '../src/poc/static/vue-assets',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        'test-integration': resolve(__dirname, 'src/main-test.js'),
        'dt-editor': resolve(__dirname, 'src/main-editor.js')
      },
      output: {
        entryFileNames: `[name].js`,
        chunkFileNames: `[name].js`,
        assetFileNames: `[name].[ext]`
      }
    }
  }
})