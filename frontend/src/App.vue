<template>
  <Layout v-if="session().isLoggedIn">
    <router-view />
  </Layout>
  <Dialogs />
  <Toasts />
</template>

<script setup>
import { sessionStore as session } from '@/stores/session'
import { Dialogs } from '@/utils/dialogs'
import { Toasts } from 'qbs-vue-ui'
import { computed, defineAsyncComponent, onMounted } from 'vue'

const MobileLayout = defineAsyncComponent(() =>
  import('./components/Layouts/MobileLayout.vue')
)
const DesktopLayout = defineAsyncComponent(() =>
  import('./components/Layouts/DesktopLayout.vue')
)
const Layout = computed(() => {
  if (window.innerWidth < 640) {
    return MobileLayout
  } else {
    return DesktopLayout
  }
})
onMounted(async () => {
  const res = await fetch('/api/method/crm.api.branding.get_branding');
  const data = await res.json();

  const title = data.message.title;
  const favicon = data.message.favicon;

  if (title) {
    document.title = title;
  }

  if (favicon) {
    let link = document.querySelector("link[rel~='icon']");
    if (!link) {
      link = document.createElement("link");
      link.rel = "icon";
      document.head.appendChild(link);
    }
    link.href = favicon;
  }
   if (title) {
    let meta = document.querySelector("meta[name='apple-mobile-web-app-title']");
    if (!meta) {
      meta = document.createElement("meta");
      meta.name = "apple-mobile-web-app-title";
      document.head.appendChild(meta);
    }
    meta.content = title;
  }
});

</script>
