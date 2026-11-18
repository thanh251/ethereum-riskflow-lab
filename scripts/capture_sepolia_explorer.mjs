import { resolve } from "node:path";
import { chromium } from "file:///C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";

const projectDir = resolve(new URL("..", import.meta.url).pathname.replace(/^\/(.:)/, "$1"));
const outputDir = resolve(projectDir, "data", "results");
const browser = await chromium.launch({
  executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  headless: true,
  args: ["--disable-gpu", "--disable-dev-shm-usage"],
});
const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });
const page = await context.newPage();

async function capture(url, filename) {
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForTimeout(8000);
  for (const label of ["Got it", "Accept", "I agree"]) {
    const button = page.getByRole("button", { name: label, exact: true });
    if (await button.count()) {
      await button.first().click().catch(() => {});
      break;
    }
  }
  await page.screenshot({ path: resolve(outputDir, filename), fullPage: false });
  console.log(`${filename}: ${await page.title()}`);
}

await capture(
  "https://eth-sepolia.blockscout.com/tx/0x7b09f85d9f07498c9aa9043b318486598f941bd60dcc48db346ae5672515be78",
  "sepolia_alert_explorer.png",
);
await capture(
  "https://eth-sepolia.blockscout.com/address/0x2b379635429ceed5904ad8cf09db36e2e100968f",
  "sepolia_contract_explorer.png",
);
await browser.close();
