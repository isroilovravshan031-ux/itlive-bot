import {
  defineRailway,
  github,
  preserve,
  project,
  service,
  volume,
} from "railway/iac";

// Optional: use this in a dedicated project after reviewing `railway config plan`.
// All secrets stay in Railway Variables; preserve() never embeds them in source.
export default defineRailway(() => {
  const region = "asia-southeast1-eqsg3a";
  const data = volume("itlive-data", { region, sizeMB: 1024 });
  const app = service("itlive-bot", {
    source: github("isroilovravshan031-ux/itlive-bot", { branch: "main" }),
    start: "python run.py",
    healthcheck: "/healthz",
    healthcheckTimeout: 120,
    replicas: { [region]: 1 },
    volumeMounts: { "/data": data },
    env: {
      BOT_TOKEN: preserve(),
      ADMINS: preserve(),
      APP_URL: preserve(),
      DATABASE_PATH: "/data/itlive_bot.db",
      UPLOAD_DIR: "/data/uploads",
      RUN_BOT: "true",
    },
  });
  return project("itlive-bot", { resources: [app, data] });
});
