// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract RiskAlertRegistry {
    address public immutable admin;
    mapping(address => bool) public reporter;

    event ReporterUpdated(address indexed reporterAddress, bool allowed);
    event AlertRaised(
        bytes32 indexed scenarioId,
        address indexed subject,
        uint8 score,
        bytes32 indexed reasonCode,
        bytes32 evidenceHash,
        uint256 timestamp
    );

    error NotAdmin();
    error NotReporter();
    error InvalidScore();

    constructor() {
        admin = msg.sender;
        reporter[msg.sender] = true;
    }

    function setReporter(address account, bool allowed) external {
        if (msg.sender != admin) revert NotAdmin();
        reporter[account] = allowed;
        emit ReporterUpdated(account, allowed);
    }

    function raiseAlert(
        bytes32 scenarioId,
        address subject,
        uint8 score,
        bytes32 reasonCode,
        bytes32 evidenceHash
    ) external {
        if (!reporter[msg.sender]) revert NotReporter();
        if (score > 100) revert InvalidScore();
        emit AlertRaised(scenarioId, subject, score, reasonCode, evidenceHash, block.timestamp);
    }
}

