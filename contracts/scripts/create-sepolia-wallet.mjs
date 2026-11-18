import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { privateKeyToAccount, generatePrivateKey } from "viem/accounts";

const here = dirname(fileURLToPath(import.meta.url));
const projectDir = resolve(here, "..", "..");
const envPath = resolve(projectDir, ".env");
if (existsSync(envPath)) {
  throw new Error(".env đã tồn tại; không ghi đè ví hoặc cấu hình hiện có.");
}

const privateKey = generatePrivateKey();
const account = privateKeyToAccount(privateKey);
const example = readFileSync(resolve(projectDir, ".env.example"), "utf8");
const configured = example
  .replace(/^SEPOLIA_RPC_URL=.*$/m, "SEPOLIA_RPC_URL=https://ethereum-sepolia-rpc.publicnode.com")
  .replace(/^SEPOLIA_PRIVATE_KEY=.*$/m, `SEPOLIA_PRIVATE_KEY=${privateKey}`);
writeFileSync(envPath, configured, { encoding: "utf8", flag: "wx" });

const resultsDir = resolve(projectDir, "data", "results");
mkdirSync(resultsDir, { recursive: true });
writeFileSync(resolve(resultsDir, "sepolia_wallet.json"), JSON.stringify({
  network: "Sepolia",
  chainId: 11155111,
  address: account.address,
  createdAt: new Date().toISOString(),
  note: "Dedicated testnet-only deployment wallet. Private key is stored only in ignored .env.",
}, null, 2), "utf8");

console.log(`Sepolia test wallet: ${account.address}`);
console.log("Private key saved only to ignored .env; it was not printed.");
