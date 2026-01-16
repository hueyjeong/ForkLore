# 🔌 MCP (Model Context Protocol) 가이드

**작성일**: 2026.01.16  
**작성자**: Antigravity  
**문서 버전**: v1.0

---

> Claude Code에서 외부 도구 및 데이터 소스와 연결하기 위한 MCP 설정 가이드

## 1. 개요 (Overview)

**Model Context Protocol (MCP)**은 AI 모델(Claude 등)이 외부 도구, 데이터 소스 및 프롬프트와 안전하고 표준화된 방식으로 상호작용할 수 있도록 설계된 오픈 프로토콜입니다.

### 핵심 개념
- **Tools (도구)**: 모델이 실행할 수 있는 함수 (예: 파일 읽기, API 호출, 데이터베이스 쿼리).
- **Resources (리소스)**: 모델이 읽을 수 있는 데이터 (예: 로그 파일, API 문서, DB 스키마).
- **Prompts (프롬프트)**: 특정 작업을 위해 미리 정의된 템플릿.

## 2. MCP 구성 요소 (Components)

MCP 에코시스템은 세 가지 주요 역할로 나뉩니다:

1.  **MCP Host**: Claude Desktop, Claude Code와 같이 MCP 서버를 실행하고 제어하는 애플리케이션.
2.  **MCP Client**: Host 내에서 서버와 통신을 담당하는 클라이언트 구현체.
3.  **MCP Server**: 실제 도구와 리소스를 제공하는 실행 가능한 프로그램 (Python, Node.js 등).

## 3. 설정 방법 (Configuration)

MCP 설정은 설정 범위(Scope)에 따라 다른 위치에 저장됩니다.

### 설정 범위 비교

| 범위 | 위치 | 설명 |
| :--- | :--- | :--- |
| **Local (Project)** | `./.mcp.json` | 특정 프로젝트에 국한된 도구 설정. 협업 시 공유 가능. |
| **User (Global)** | `~/.claude.json` | 사용자의 모든 프로젝트에서 전역적으로 사용되는 도구 설정. |
| **System** | `/etc/claude/config.json` | 시스템 전체 설정 (주로 엔터프라이즈 환경). |

### 설정 형식 (Config Format)

`mcpServers` 객체 내에 서버 식별자와 실행 정보를 정의합니다. `${VAR}` 형식을 사용하여 환경 변수를 확장할 수 있습니다.

```json
{
  "mcpServers": {
    "my-tool": {
      "command": "node",
      "args": ["/path/to/server.js"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

## 4. 커스텀 도구 생성 (Custom Tools)

### Python (FastMCP 사용)
`fastmcp` 패키지를 사용하면 매우 간단하게 서버를 구축할 수 있습니다.

```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("MyProject")

@mcp.tool()
def get_project_status(project_name: str) -> str:
    """프로젝트의 현재 상태를 반환합니다."""
    return f"{project_name}은(는) 현재 정상 작동 중입니다."

if __name__ == "__main__":
    mcp.run()
```

### TypeScript (@modelcontextprotocol/sdk 사용)
공식 SDK를 사용하여 정교한 제어가 가능합니다.

```typescript
// index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

const server = new Server({
  name: "example-server",
  version: "1.0.0",
}, {
  capabilities: { tools: {} },
});

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: "hello",
    description: "인사를 건넵니다.",
    inputSchema: {
      type: "object",
      properties: { name: { type: "string" } },
    },
  }],
}));

const transport = new StdioServerTransport();
await server.connect(transport);
```

## 5. 사용 가능한 MCP 서버 (Available Servers)

이미 커뮤니티에서 제공하는 다양한 서버를 활용할 수 있습니다:

-   **PostgreSQL**: DB 쿼리 및 스키마 탐색.
-   **Filesystem**: 특정 디렉토리에 대한 안전한 읽기/쓰기 권한 부여.
-   **Git**: 커밋 이력 조회 및 브랜치 관리.
-   **Slack**: 메시지 전송 및 채널 읽기.
-   **Google Drive**: 문서 검색 및 읽기.

## 6. 프로젝트 설정 예시 (Project Setup)

ForkLore 프로젝트의 루트에 `.mcp.json`을 생성하여 개발 효율을 높일 수 있습니다.

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost:5432/forklore"]
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    },
    "custom-scripts": {
      "command": "python",
      "args": ["${CURDIR}/scripts/mcp_helper.py"],
      "env": {
        "PYTHONPATH": "${CURDIR}/backend"
      }
    }
  }
}
```

---

## 문서 끝
