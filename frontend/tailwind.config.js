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
        primary: '#E76458',
        secondary: '#6c757d',
        success: '#28a745',
        info: '#17a2b8',
        warning: '#ffc107',
        danger: '#dc3545',
        light: '#f8f9fa',
        dark: '#343a40',
        sidebar: '#191919 !important',
        sidebar_hover: '#E75A44 !important',
        sidebar_active: '#E75A44 !important',
        sidebar_icon_color: '#999696 !important',
        table_header: '#E8EEFD !important',
        btn_primary: '#E76458  !important',
        table_row_hover: 'rgba(229, 237, 255, 0.22) !important',
        bg_white: '#FFF !important',
        table_border: '#DBE5FA !important',
        btn_grey: '#ebecef !important',
      },
    },
  },
  plugins: [],
}
