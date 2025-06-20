import { createApp } from "vue";
import App from "./App.vue";
import * as Sentry from "@sentry/vue";
import FightingDesign from "fighting-design";
import "fighting-design/dist/index.css";
import { QuillEditor } from "@vueup/vue-quill";
import "@vueup/vue-quill/dist/vue-quill.snow.css";
import { install as MonacoPlugin } from "@guolao/vue-monaco-editor";

const app = createApp(App);
app.component("QuillEditor", QuillEditor);
app.use(MonacoPlugin, {
  paths: {
    vs: "https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs",
  },
});

Sentry.init({
  app,
  dsn: "https://14a4e2b4f7bff41bda1507ccc0c2601b@o4507525750521856.ingest.us.sentry.io/4508335554101248",
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration({ maskAllText: false, blockAllMedia: false }),
  ],
  // Tracing
  tracesSampleRate: 1.0, //  Capture 100% of the transactions
  // Set 'tracePropagationTargets' to control for which URLs distributed tracing should be enabled
  tracePropagationTargets: [
    "localhost",
    /^https:\/\/yourserver\.io\/api/,
    "124.221.67.43",
  ],
  // Session Replay
  replaysSessionSampleRate: 0.3, // This sets the sample rate at 10%. You may want to change it to 100% while in development and then sample at a lower rate in production.
  replaysOnErrorSampleRate: 1.0, // If you're not already sampling the entire session, change the sample rate to 100% when sampling sessions where errors occur.
});

app.use(FightingDesign);
app.mount("#app");
