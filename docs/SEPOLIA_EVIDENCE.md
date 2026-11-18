# Bằng chứng triển khai Sepolia

- Thời điểm: 2026-11-07T15:45:28.231Z
- Chain ID: 11155111
- Ví triển khai: [0x23b1650A124E3F4D0Cc12EB3f4fD98014eb3a468](https://sepolia.etherscan.io/address/0x23b1650A124E3F4D0Cc12EB3f4fD98014eb3a468)
- Scenario ID: `0x07a775ef7395c61222fab1910bf7fe6478b53c19233f4e2b3f02099a090ea15d`

## Hợp đồng

- MockUSDC: [0x881f78bc17f9cdc3bb9f969d6c7f4a1b159eca58](https://sepolia.etherscan.io/address/0x881f78bc17f9cdc3bb9f969d6c7f4a1b159eca58) — [deployment tx](https://sepolia.etherscan.io/tx/0xf89ca24191926acb6a4040d63a767954af949a75e9f11859f6688b19ff269147), status=success, gas=5247225
- AgentRegistry: [0x241c5770c2150b7b61af7a643e5f340567e312af](https://sepolia.etherscan.io/address/0x241c5770c2150b7b61af7a643e5f340567e312af) — [deployment tx](https://sepolia.etherscan.io/tx/0x20f488c5c58bf8181cf944111f9a62d321b05157574be5631329110a4dcbf44a), status=success, gas=2789515
- ScenarioRecorder: [0x143228fc2e59b90ac834454cd91b0129115fd423](https://sepolia.etherscan.io/address/0x143228fc2e59b90ac834454cd91b0129115fd423) — [deployment tx](https://sepolia.etherscan.io/tx/0xacb07cdab95aa458d9ce715b601177ce212eaf803958864e7607d0e2016fc3d5), status=success, gas=3587380
- RiskAlertRegistry: [0x2b379635429ceed5904ad8cf09db36e2e100968f](https://sepolia.etherscan.io/address/0x2b379635429ceed5904ad8cf09db36e2e100968f) — [deployment tx](https://sepolia.etherscan.io/tx/0x12f60f6654d737e1b77c9390e2a61a45a0b284d89d260e95dfb946a81e436331), status=success, gas=2746741

## Replay và cảnh báo

- AgentRegistered: [0x32fe436a717e6debb81026201c9592accf2ec94db0a0147327c7daa0b8f653b8](https://sepolia.etherscan.io/tx/0x32fe436a717e6debb81026201c9592accf2ec94db0a0147327c7daa0b8f653b8), status=success, gas=349250
- MockUSDC mint: [0xab940ea801a93bd5cf4975e61a16d94c56412cdc25fbc5db004a0635a54408f3](https://sepolia.etherscan.io/tx/0xab940ea801a93bd5cf4975e61a16d94c56412cdc25fbc5db004a0635a54408f3), status=success, gas=238987
- ScenarioStarted: [0xd80a66b9472ecf392b6e5a327874b35bcdef6d241eee2d1ec1cc0563449de226](https://sepolia.etherscan.io/tx/0xd80a66b9472ecf392b6e5a327874b35bcdef6d241eee2d1ec1cc0563449de226), status=success, gas=129107
- ScenarioTransfer #1: [0xc37704d8bbb8d228a9d9172435c6268b90c8e83a09d27f2ccb67ed5fd2536b8d](https://sepolia.etherscan.io/tx/0xc37704d8bbb8d228a9d9172435c6268b90c8e83a09d27f2ccb67ed5fd2536b8d), status=success, gas=132869
- ScenarioTransfer #2: [0xc4d976fc4cecd1dab778b9f0de618ae65182545b6b5ae66a87e8f5c08e619ee4](https://sepolia.etherscan.io/tx/0xc4d976fc4cecd1dab778b9f0de618ae65182545b6b5ae66a87e8f5c08e619ee4), status=success, gas=34949
- ScenarioTransfer #3: [0xd413053ac73f9482fbc6884b568eba02f80f5ea60738e1f6ec5cc49471fe2147](https://sepolia.etherscan.io/tx/0xd413053ac73f9482fbc6884b568eba02f80f5ea60738e1f6ec5cc49471fe2147), status=success, gas=34949
- ScenarioCompleted: [0x4c40fd7959ce4bb2a4a9d6d957b5cc40359bb9a05a4445d8714de9303a01299d](https://sepolia.etherscan.io/tx/0x4c40fd7959ce4bb2a4a9d6d957b5cc40359bb9a05a4445d8714de9303a01299d), status=success, gas=22315
- AlertRaised: [0x7b09f85d9f07498c9aa9043b318486598f941bd60dcc48db346ae5672515be78](https://sepolia.etherscan.io/tx/0x7b09f85d9f07498c9aa9043b318486598f941bd60dcc48db346ae5672515be78), status=success, gas=25496

AlertRaised: subject=0x2cf207f5bc6cc36eebd60af984eafb7bba9274c6, score=67, reasonCode=0x41424d5f5249534b5f53434f5245000000000000000000000000000000000000, evidenceHash=0xdaace0341802789ea7fa72f42f93701cd0857140fffbc5576b0009478606d526.
