// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {MockUSDC} from "../contracts/MockUSDC.sol";
import {AgentRegistry} from "../contracts/AgentRegistry.sol";
import {ScenarioRecorder} from "../contracts/ScenarioRecorder.sol";
import {RiskAlertRegistry} from "../contracts/RiskAlertRegistry.sol";

contract RiskFlowTest {
    function testMockUSDCTransfer() public {
        MockUSDC token = new MockUSDC();
        token.mint(address(this), 1_000_000);
        token.transfer(address(0xBEEF), 250_000);
        require(token.balanceOf(address(0xBEEF)) == 250_000, "transfer failed");
    }

    function testAgentRegistration() public {
        AgentRegistry registry = new AgentRegistry();
        registry.register(address(0xCAFE), bytes32("agent-1"), bytes32("relay"));
        (, , bool active) = registry.agents(address(0xCAFE));
        require(active, "agent not active");
    }

    function testScenarioAndAlert() public {
        ScenarioRecorder recorder = new ScenarioRecorder();
        RiskAlertRegistry alerts = new RiskAlertRegistry();
        bytes32 scenarioId = keccak256("scenario-1");
        recorder.start(scenarioId, keccak256("config"));
        recorder.record(scenarioId, address(0x1), address(0x2), 100_000);
        recorder.complete(scenarioId);
        alerts.raiseAlert(scenarioId, address(0x2), 80, bytes32("FAST_FORWARD"), keccak256("evidence"));
        require(recorder.transferCount(scenarioId) == 1, "wrong transfer count");
    }
}

