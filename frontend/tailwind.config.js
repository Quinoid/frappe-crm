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
        primary: '#000',
        secondary: '#6c757d',
        primary_text: '#AC6BDF',
        success: '#28a745',
        info: '#17a2b8',
        warning: '#ffc107',
        danger: '#dc3545',
        light: '#f8f9fa',
        dark: '#343a40',
        // sidebar: '#191919 !important',
        sidebar:
          'linear-gradient(180deg, rgba(220, 227, 254, 0.09) 0%, rgba(228, 197, 245, 0.09) 100%), #FFF !important',
        sidebar_hover: '#FFF !important',
        sidebar_active: '#FFF !important',
        sidebar_icon_color: '#999696 !important',
        table_header: '#EAE9FD !important',
        btn_primary: '#000  !important',
        table_row_hover: 'rgba(238, 238, 238, 0.3) !important',
        bg_white: '#FFF !important',
        table_border: '#F1EEF9 !important',
        btn_grey: '#ebecef !important',
        icon_color: '##909090 !important',
      },
    },
  },
  plugins: [],
}
