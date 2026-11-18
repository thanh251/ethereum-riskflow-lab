import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

export default buildModule("RiskFlow", (m) => {
  const mockUSDC = m.contract("MockUSDC");
  const agentRegistry = m.contract("AgentRegistry");
  const scenarioRecorder = m.contract("ScenarioRecorder");
  const riskAlertRegistry = m.contract("RiskAlertRegistry");
  return { mockUSDC, agentRegistry, scenarioRecorder, riskAlertRegistry };
});

