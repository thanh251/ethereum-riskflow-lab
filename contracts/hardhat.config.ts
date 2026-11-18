import { defineConfig } from "hardhat/config";
import hardhatToolboxViem from "@nomicfoundation/hardhat-toolbox-viem";
import dotenv from "dotenv";

dotenv.config({ path: "../.env" });

const sepoliaRpc = process.env.SEPOLIA_RPC_URL ?? "";
const privateKey = process.env.SEPOLIA_PRIVATE_KEY ?? "";

export default defineConfig({
  plugins: [hardhatToolboxViem],
  solidity: {
    profiles: {
      default: { version: "0.8.28" },
      production: { version: "0.8.28", settings: { optimizer: { enabled: true, runs: 200 } } }
    }
  },
  networks: sepoliaRpc ? {
    sepolia: {
      type: "http",
      chainType: "l1",
      chainId: 11155111,
      url: sepoliaRpc,
      accounts: privateKey ? [privateKey] : []
    }
  } : {}
});

