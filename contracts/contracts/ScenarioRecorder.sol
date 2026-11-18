// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract ScenarioRecorder {
    address public immutable admin;
    mapping(bytes32 => bool) public started;
    mapping(bytes32 => uint256) public transferCount;

    event ScenarioStarted(bytes32 indexed scenarioId, bytes32 configHash, uint256 timestamp);
    event ScenarioTransfer(
        bytes32 indexed scenarioId,
        uint256 indexed sequence,
        address indexed fromAgent,
        address toAgent,
        uint256 amount
    );
    event ScenarioCompleted(bytes32 indexed scenarioId, uint256 transfers, uint256 timestamp);

    error NotAdmin();
    error ScenarioNotStarted();
    error ScenarioAlreadyStarted();

    constructor() { admin = msg.sender; }

    modifier onlyAdmin() {
        if (msg.sender != admin) revert NotAdmin();
        _;
    }

    function start(bytes32 scenarioId, bytes32 configHash) external onlyAdmin {
        if (started[scenarioId]) revert ScenarioAlreadyStarted();
        started[scenarioId] = true;
        emit ScenarioStarted(scenarioId, configHash, block.timestamp);
    }

    function record(bytes32 scenarioId, address fromAgent, address toAgent, uint256 amount) external onlyAdmin {
        if (!started[scenarioId]) revert ScenarioNotStarted();
        uint256 sequence = transferCount[scenarioId]++;
        emit ScenarioTransfer(scenarioId, sequence, fromAgent, toAgent, amount);
    }

    function complete(bytes32 scenarioId) external onlyAdmin {
        if (!started[scenarioId]) revert ScenarioNotStarted();
        emit ScenarioCompleted(scenarioId, transferCount[scenarioId], block.timestamp);
    }
}

