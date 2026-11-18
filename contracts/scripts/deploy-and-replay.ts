import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import dotenv from "dotenv";
import {
  createPublicClient,
  createWalletClient,
  decodeEventLog,
  http,
  keccak256,
  stringToHex,
  toBytes,
  type Abi,
  type Address,
  type Hex,
} from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { sepolia } from "viem/chains";

const here = dirname(fileURLToPath(import.meta.url));
const contractsDir = resolve(here, "..");
const projectDir = resolve(contractsDir, "..");
dotenv.config({ path: resolve(projectDir, ".env") });

const rpcUrl = process.env.SEPOLIA_RPC_URL?.trim();
const rawKey = process.env.SEPOLIA_PRIVATE_KEY?.trim();
if (!rpcUrl || !rawKey) {
  throw new Error("Thiếu SEPOLIA_RPC_URL hoặc SEPOLIA_PRIVATE_KEY trong .env ở thư mục gốc.");
}
const privateKey = (rawKey.startsWith("0x") ? rawKey : `0x${rawKey}`) as Hex;
if (!/^0x[0-9a-fA-F]{64}$/.test(privateKey)) {
  throw new Error("SEPOLIA_PRIVATE_KEY không đúng định dạng 32 byte.");
}

const account = privateKeyToAccount(privateKey);
const publicClient = createPublicClient({ chain: sepolia, transport: http(rpcUrl) });
const walletClient = createWalletClient({ account, chain: sepolia, transport: http(rpcUrl) });
const explorer = "https://sepolia.etherscan.io";

type Artifact = { abi: Abi; bytecode: Hex };
type ReceiptEvidence = {
  txHash: Hex;
  status: string;
  blockNumber: string;
  gasUsed: string;
  explorer: string;
};

function artifact(contractName: string): Artifact {
  const path = resolve(contractsDir, "artifacts", "contracts", `${contractName}.sol`, `${contractName}.json`);
  const parsed = JSON.parse(readFileSync(path, "utf8"));
  return { abi: parsed.abi as Abi, bytecode: parsed.bytecode as Hex };
}

async function receiptFor(txHash: Hex): Promise<ReceiptEvidence> {
  const receipt = await publicClient.waitForTransactionReceipt({ hash: txHash, confirmations: 1 });
  if (receipt.status !== "success") throw new Error(`Giao dịch thất bại: ${txHash}`);
  return {
    txHash,
    status: receipt.status,
    blockNumber: receipt.blockNumber.toString(),
    gasUsed: receipt.gasUsed.toString(),
    explorer: `${explorer}/tx/${txHash}`,
  };
}

async function deploy(contractName: string) {
  const item = artifact(contractName);
  const txHash = await walletClient.deployContract({
    abi: item.abi,
    bytecode: item.bytecode,
    account,
  });
  const receipt = await publicClient.waitForTransactionReceipt({ hash: txHash, confirmations: 1 });
  if (receipt.status !== "success" || !receipt.contractAddress) {
    throw new Error(`Không triển khai được ${contractName}: ${txHash}`);
  }
  return {
    abi: item.abi,
    address: receipt.contractAddress,
    deployment: {
      txHash,
      status: receipt.status,
      blockNumber: receipt.blockNumber.toString(),
      gasUsed: receipt.gasUsed.toString(),
      explorer: `${explorer}/tx/${txHash}`,
    },
    explorer: `${explorer}/address/${receipt.contractAddress}`,
  };
}

async function write(
  address: Address,
  abi: Abi,
  functionName: string,
  args: readonly unknown[],
) {
  const txHash = await walletClient.writeContract({
    address,
    abi,
    functionName,
    args,
    account,
  } as never);
  return receiptFor(txHash);
}

const chainId = await publicClient.getChainId();
if (chainId !== 11155111) throw new Error(`RPC không phải Sepolia: chain ID ${chainId}`);
const balanceBefore = await publicClient.getBalance({ address: account.address });
if (balanceBefore === 0n) {
  throw new Error(`Ví ${account.address} chưa có Sepolia ETH để trả gas.`);
}

const payloadPath = resolve(projectDir, "data", "processed", "sepolia_payload.json");
const payload = JSON.parse(readFileSync(payloadPath, "utf8"));
if (!Array.isArray(payload.transfers) || payload.transfers.length === 0) {
  throw new Error("Payload Sepolia chưa có giao dịch. Hãy chạy export_sepolia_scenario.py trước.");
}

console.log(`Sepolia chain ID: ${chainId}`);
console.log(`Deployer: ${account.address}`);
console.log("Đang triển khai 4 hợp đồng...");
const mockUSDC = await deploy("MockUSDC");
const agentRegistry = await deploy("AgentRegistry");
const scenarioRecorder = await deploy("ScenarioRecorder");
const riskAlertRegistry = await deploy("RiskAlertRegistry");

const scenarioId = keccak256(toBytes(String(payload.scenario_id)));
const configHash = keccak256(toBytes(JSON.stringify(payload)));
const actions: Record<string, unknown>[] = [];

actions.push({
  name: "AgentRegistered",
  ...(await write(agentRegistry.address, agentRegistry.abi, "register", [
    account.address,
    stringToHex("riskflow-deployer", { size: 32 }),
    stringToHex("operator", { size: 32 }),
  ])),
});
actions.push({
  name: "MockUSDC mint",
  ...(await write(mockUSDC.address, mockUSDC.abi, "mint", [account.address, 1_000_000_000n])),
});
actions.push({
  name: "ScenarioStarted",
  ...(await write(scenarioRecorder.address, scenarioRecorder.abi, "start", [scenarioId, configHash])),
});

const replayTransfers = payload.transfers.slice(0, 3);
for (const [index, transfer] of replayTransfers.entries()) {
  actions.push({
    name: `ScenarioTransfer #${index + 1}`,
    ...(await write(scenarioRecorder.address, scenarioRecorder.abi, "record", [
      scenarioId,
      transfer.from_agent as Address,
      transfer.to_agent as Address,
      BigInt(transfer.amount_micro_usdc),
    ])),
  });
}

actions.push({
  name: "ScenarioCompleted",
  ...(await write(scenarioRecorder.address, scenarioRecorder.abi, "complete", [scenarioId])),
});

const risky = [...payload.transfers].sort((a, b) => Number(b.risk_score) - Number(a.risk_score))[0];
const score = Math.max(0, Math.min(100, Number(risky.risk_score ?? 0)));
const reasonCode = stringToHex("ABM_RISK_SCORE", { size: 32 });
const evidenceHash = keccak256(toBytes(JSON.stringify(risky)));
const alertTxHash = await walletClient.writeContract({
  address: riskAlertRegistry.address,
  abi: riskAlertRegistry.abi,
  functionName: "raiseAlert",
  args: [scenarioId, risky.to_agent as Address, score, reasonCode, evidenceHash],
  account,
} as never);
const alertRawReceipt = await publicClient.waitForTransactionReceipt({ hash: alertTxHash, confirmations: 1 });
if (alertRawReceipt.status !== "success") throw new Error(`AlertRaised thất bại: ${alertTxHash}`);
const alertLog = alertRawReceipt.logs
  .filter((log) => log.address.toLowerCase() === riskAlertRegistry.address.toLowerCase())
  .map((log) => {
    try {
      return decodeEventLog({ abi: riskAlertRegistry.abi, data: log.data, topics: log.topics });
    } catch {
      return null;
    }
  })
  .find((log) => log?.eventName === "AlertRaised");
if (!alertLog) throw new Error("Receipt thành công nhưng không tìm thấy event AlertRaised.");
actions.push({
  name: "AlertRaised",
  txHash: alertTxHash,
  status: alertRawReceipt.status,
  blockNumber: alertRawReceipt.blockNumber.toString(),
  gasUsed: alertRawReceipt.gasUsed.toString(),
  explorer: `${explorer}/tx/${alertTxHash}`,
});

const balanceAfter = await publicClient.getBalance({ address: account.address });
const contracts = {
  MockUSDC: mockUSDC,
  AgentRegistry: agentRegistry,
  ScenarioRecorder: scenarioRecorder,
  RiskAlertRegistry: riskAlertRegistry,
};
const evidence = {
  network: "Sepolia",
  chainId,
  createdAt: new Date().toISOString(),
  deployer: account.address,
  balanceBeforeWei: balanceBefore.toString(),
  balanceAfterWei: balanceAfter.toString(),
  scenarioId,
  configHash,
  contracts: Object.fromEntries(Object.entries(contracts).map(([name, item]) => [name, {
    address: item.address,
    deployment: item.deployment,
    explorer: item.explorer,
  }])),
  actions,
  alert: {
    subject: risky.to_agent,
    score,
    reasonCode,
    evidenceHash,
    eventName: alertLog.eventName,
    transactionHash: alertTxHash,
    explorer: `${explorer}/tx/${alertTxHash}`,
  },
};

const resultsDir = resolve(projectDir, "data", "results");
mkdirSync(resultsDir, { recursive: true });
const evidencePath = resolve(resultsDir, "sepolia_evidence.json");
writeFileSync(evidencePath, JSON.stringify(evidence, null, 2), "utf8");

const md = [
  "# Bằng chứng triển khai Sepolia",
  "",
  `- Thời điểm: ${evidence.createdAt}`,
  `- Chain ID: ${chainId}`,
  `- Ví triển khai: [${account.address}](${explorer}/address/${account.address})`,
  `- Scenario ID: \`${scenarioId}\``,
  "",
  "## Hợp đồng",
  "",
  ...Object.entries(contracts).map(([name, item]) =>
    `- ${name}: [${item.address}](${item.explorer}) — [deployment tx](${item.deployment.explorer}), status=${item.deployment.status}, gas=${item.deployment.gasUsed}`),
  "",
  "## Replay và cảnh báo",
  "",
  ...actions.map((action) =>
    `- ${action.name}: [${action.txHash}](${action.explorer}), status=${action.status}, gas=${action.gasUsed}`),
  "",
  `AlertRaised: subject=${risky.to_agent}, score=${score}, reasonCode=${reasonCode}, evidenceHash=${evidenceHash}.`,
  "",
];
writeFileSync(resolve(projectDir, "docs", "SEPOLIA_EVIDENCE.md"), md.join("\n"), "utf8");
console.log(`Đã lưu bằng chứng: ${evidencePath}`);
console.log(`AlertRaised: ${explorer}/tx/${alertTxHash}`);
