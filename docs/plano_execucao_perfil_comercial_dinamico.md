# Plano de Engenharia e Análise Crítica: Desacoplamento do Perfil de Loja (StoreProfile Engine)

---

## 1. Objetivo Técnico
Transformar o sistema de uma solução de código fixo (hardcoded para a Victor Cell) em uma **plataforma comercializável e configurável (Domain-Agnostic)**, permitindo que consultores ou clientes configurem o nome da loja, nicho de mercado, produtos recusados, métodos de entrega e tom de voz diretamente por API e banco de dados, sem alterar código-fonte.

---

## 2. Desenho do Plano Inicial

1. **Camada de Domínio (`domain/entities.py`):**
   - Criar dataclass `StoreProfile` contendo:
     - `store_id: str = "default"`
     - `store_name: str = "Victor Cell"`
     - `niche_description: str = "Peças e manutenção exclusiva de tablets"`
     - `out_of_scope_keywords: List[str] = ["celular", "iphone", "smartphone", "capa", "pelicula"]`
     - `rejection_message: str = "Só peças de tablet"`
     - `delivery_methods: List[str] = ["Uber Flash", "Balcão"]`
     - `tone_guidelines: str = "ultra-curto, direto, objetivo, 1 a 6 palavras no máximo"`
2. **Camada de Repositório (`infrastructure/repositories/sqlite_repository.py`):**
   - Criar tabela `store_profile` no SQLite.
   - Adicionar métodos assíncronos `get_store_profile()` e `save_store_profile()`.
3. **Camada de Serviço de IA (`infrastructure/services/agent_service.py`):**
   - Injetar `StoreProfile` no prompt do Gemini e no motor de fallback semântico.
4. **Camada de Apresentação (`presentation/api.py`):**
   - Expor endpoints `GET /api/system/profile` e `POST /api/system/profile`.
5. **Suíte de Testes:**
   - Adicionar testes cobrindo a nova entidade, a persistência e a alternância de nicho (ex: Loja de Autopeças de Moto).

---

## 3. Análise Crítica do Plano: Identificação de Pontos Fracos e Correções

| Ponto Fraco Identificado | Risco Associado | Correção Aplicada ao Plano |
| :--- | :--- | :--- |
| **1. Estado Inicial Vazio no Banco** | Falha de inicialização em bancos existentes que não possuem a tabela `store_profile`. | `get_store_profile()` deve retornar uma instância padrão pré-populada da Victor Cell caso o banco esteja vazio, garantindo que nenhum teste ou operação em produção falhe. |
| **2. Parsing Rígido de Palavras Proibidas** | Se o lojista cadastrar `"carro, moto , caminhão"`, espaços em branco poderiam quebrar o matching. | Normalizar a lista com strip e lower: `[k.strip().lower() for k in keywords if k.strip()]`. |
| **3. Quebra de Retrocompatibilidade** | Se `ProcessIncomingMessageUseCase` exigir `StoreProfile` como parâmetro obrigatório, testes legados falhariam. | Tornar `store_profile: Optional[StoreProfile] = None` opcional em todos os métodos, aplicando fallback automático para o padrão da loja caso omitido. |
| **4. Validação de Payloads na API** | O usuário poderia postar JSON malformado ou campos vazios via REST. | Criar schema Pydantic `StoreProfileSchema` com validações de tamanho mínimo para campos de texto. |

---

## 4. Plano Refinado Pronto para Execução

- **Passo 1:** Implementar a entidade `StoreProfile` em `domain/entities.py`.
- **Passo 2:** Implementar tabela e métodos de persistência em `infrastructure/repositories/sqlite_repository.py`.
- **Passo 3:** Conectar `StoreProfile` ao `AIAgentService` e `ProcessIncomingMessageUseCase`.
- **Passo 4:** Criar endpoints `GET /api/system/profile` e `POST /api/system/profile` em `presentation/api.py`.
- **Passo 5:** Criar suíte de testes `tests/test_store_profile_commercial.py` validando o perfil padrão e nichos alternativos (autopeças, farmácia).
- **Passo 6:** Executar suíte completa (`pytest`) e verificar 100% de aprovação.
