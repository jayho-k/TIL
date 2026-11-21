from copy import deepcopy

# message AgentCapabilities {
#   optional bool streaming = 1;
#   optional bool push_notifications = 2;
#   repeated AgentExtension extensions = 3;
#   optional bool extended_agent_card = 4;
# }

# {
#   "jsonrpc": "2.0",
#   "id": "req-001",
#   "method": "SendMessage",
#   "params": {}
# }

# {"jsonrpc": "2.0", "id": "req-001", "result": {}}

# {"jsonrpc": "2.0", "id": "req-001", "error": {"code": -32600, "message": "Invalid Request"}}

AGENT_CARD = {
    "name": "expense-agent",
    "description": "출장 경비를 정리하고 사내 규정 위반을 찾는다",
    "version": "1.0.0",
    "securitySchemes" : {
        "finance_token": {
            "httpAuthSecurityScheme": {
                "scheme": "Bearer",
                "bearerFormat": "opaque",
            }
        }
    },
    "supportedInterfaces": [
        {
            "url": "http://worker:8000",
            "protocolBinding": "JSONRPC", # GRPC, HTTP + JSON
            "protocolVersion": "1.0",
        },
        {
            "url": "worker:50051",
            "protocolBinding": "GRPC",
            "protocolVersion": "1.0",
        },
    ],
    "capabilities": {
        "streaming": True,
        "pushNotifications": True,
        "extendedAgentCard": True,
    },
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain", "application/json"],
    "skills": [
        {
            "id": "settle_expense",
            "name": "경비 정산",
            "description": (
                "출장 번호를 주면 영수증을 모아 외화를 원화로 환산하고, "
                "사내 규정 한도를 넘는 항목을 찾아 합계와 함께 돌려준다."
            ),
            "tags": ["expense", "finance", "policy"],
            "examples": [
                "출장 T-2026-03 경비를 정리해 주세요",
                "T-2026-04 규정 위반이 있는지 봐 주세요",
            ],
        },
        {
            "id": "settle_and_pay",
            "name": "지급 전 정산 확정",
            "description": (
                "재무 권한을 확인한 뒤 정산 결과를 확정하는 실습용 기능이다. "
                "실제 송금은 수행하지 않는다."
            ),
            "tags": ["expense", "finance", "payment"],
            "securityRequirements": [
                {"schemes": {"finance_token": {"list": []}}}
            ],
        },
    ],
}

INTERNAL_SKILLS = [
    {
        "id": "audit_trail",
        "name": "규정 위반 근거 조회",
        "description": (
            "출장 1건의 규정 위반 판정 근거를 violations 값으로 돌려준다. "
            "위반이 있으면 승인 대기 메시지의 reason에 먼저 담는다."
        ),
        "tags": ["expense", "audit", "internal"],
        "examples": ["출장 T-2026-03 정산 근거를 보여 주세요"],
        "securityRequirements": [
            {"schemes": {"finance_token": {"list": []}}}
        ],
    },
    {
        "id": "settlement_detail",
        "name": "구조화된 정산 내역 조회",
        "description": (
            "출장 1건의 합계, 규정 위반, 처리한 영수증 수를 "
            "application/json 형식으로 돌려준다."
        ),
        "tags": ["expense", "detail", "internal"],
        "examples": ["출장 T-2026-04 상세 내역을 보여 주세요"],
        "securityRequirements": [
            {"schemes": {"finance_token": {"list": []}}}
        ],
    },
]

def extended_card() -> dict:
    """인증한 클라이언트에 내부 skill을 추가한 카드를 돌려준다."""
    card = deepcopy(AGENT_CARD)
    card["skills"].extend(INTERNAL_SKILLS)
    return card

# securitySchemes : 내가 사용할 수 있는 인증 방법을 정의
# securityRequirements  : 실제 요청에 요구하는 인증 밥업