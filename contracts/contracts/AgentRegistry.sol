// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract AgentRegistry {
    address public immutable admin;

    struct AgentInfo {
        bytes32 agentId;
        bytes32 role;
        bool active;
    }

    mapping(address => AgentInfo) public agents;
    event AgentRegistered(address indexed wallet, bytes32 indexed agentId, bytes32 role);
    event AgentStatusChanged(address indexed wallet, bool active);
    error NotAdmin();
    error ZeroAddress();

    constructor() { admin = msg.sender; }

    modifier onlyAdmin() {
        if (msg.sender != admin) revert NotAdmin();
        _;
    }

    function register(address wallet, bytes32 agentId, bytes32 role) external onlyAdmin {
        if (wallet == address(0)) revert ZeroAddress();
        agents[wallet] = AgentInfo(agentId, role, true);
        emit AgentRegistered(wallet, agentId, role);
    }

    function setActive(address wallet, bool active) external onlyAdmin {
        agents[wallet].active = active;
        emit AgentStatusChanged(wallet, active);
    }
}

