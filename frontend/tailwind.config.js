module.exports = {
  presets: [require('qbs-vue-ui/src/utils/tailwind.config')],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/qbs-vue-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
    '../node_modules/qbs-vue-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
  ],
  safelist: [
    { pattern: /!(text|bg)-/, variants: ['hover', 'active'] },
    { pattern: /^grid-cols-/ },
  ],
  theme: {
    extend: {
      colors: {
        primary: '#007bff',
        secondary: '#6c757d',
        success: '#28a745',
        info: '#17a2b8',
        warning: '#ffc107',
        danger: '#dc3545',
        light: '#f8f9fa',
        dark: '#343a40',
        sidebar: '#F3F6F9 !important',
        table_header: '#EDEEF1 !important',
        btn_primary: '#317CF7  !important',
        bg_white: '#FFF !important',
        table_border: '#f0f1f5 !important',
        btn_grey: '#ebecef !important',
      },
    },
  },
  plugins: [],
}
