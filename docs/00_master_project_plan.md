# Plano Mestre de Engenharia e Documentação Técnica
## Sistema Autônomo de Vendas, Cotação e Expedição de Peças via WhatsApp (Victor Cell)

---

### Metadados da Suíte de Engenharia

| Atributo | Definição |
| :--- | :--- |
| **Identificador** | ENG-MASTER-PLAN-001 |
| **Organização** | Victor Cell (Fortaleza/CE) |
| **Padrão de Documentação** | Google Engineering Documentation Standard (RFC / PRD / UCS) |
| **Versão** | 2.1.0 |
| **Status** | Aprovado |

---

## 1. Índice da Suíte de Documentação Técnica

A documentação técnica do sistema é estruturada sob padrões rigorosos de engenharia de software e gestão de produto:

1. [PRD-001: Especificação de Requisitos de Produto](file:///home/robson/Projetos_Desenvolvimento/victor-cell/pecasbot-api/docs/01_product_requirements_document.md)
   - Declaração do problema, objetivos estratégicos e métricas de sucesso (OKRs/KPIs).
   - Análise de personas (Técnico de Bancada, Operador de Caixa, Gestor).
   - Invariantes não-negociáveis: especialização exclusiva em tablets, concisão estrita de 1 a 6 palavras, doutrina do transbordo silencioso e protocolo de despacho em duas fases.
   - Requisitos Funcionais (FR-01 a FR-15) e Requisitos Não-Funcionais (NFR-01 a NFR-08).
   - Máquina de Estados Finitos (FSM) e limites do sistema.

2. [UCS-001: Especificação Formal de Casos de Uso](file:///home/robson/Projetos_Desenvolvimento/victor-cell/pecasbot-api/docs/02_use_case_specifications.md)
   - Matriz de rastreabilidade completa entre Requisitos Funcionais e Casos de Uso.
   - Especificação detalhada segundo padrão Cockburn/IEEE 830:
     - UC-01: Cotação Direta de Peça de Tablet em Horário Comercial
     - UC-02: Cotação Fora do Expediente Comercial e Aos Domingos
     - UC-03: Rejeição Determinística de Telefonia Móvel (Não-Tablets)
     - UC-04: Protocolo Multimodal e Triagem Visual de Imagens
     - UC-05: Fechamento de Pedido e Despacho Uber Flash em Duas Fases
     - UC-06: Reserva de Peça para Retirada no Balcão Físico
     - UC-07: Transbordo Silencioso para Atendimento Humano
     - UC-08: Intervenção Manual de Operador e Filtro Anti-Eco
     - UC-09: Consulta de Status Operacional e Rastreio Pós-Venda
     - UC-10: Consulta Analítica e Auditoria via Copilot do Gestor
   - Análise de Modos de Falha e Efeitos (FMEA).

3. [RFC-002: Arquitetura de Software e Design Técnico](file:///home/robson/Projetos_Desenvolvimento/victor-cell/pecasbot-api/docs/02_technical_architecture_design.md)
   - Arquitetura Limpa (Clean Architecture) e Portas & Adaptadores (Hexagonal).
   - Provedor Pluggable de Estoque com suporte a Bling ERP v3, Google Sheets e Memória.
   - Cache Proxy com latência de consulta inferior a 2 milissegundos e Circuit Breaker.

4. [RFC-003: Esquema de Dados, Integrações e Contratos de API](file:///home/robson/Projetos_Desenvolvimento/victor-cell/pecasbot-api/docs/03_data_schema_and_integrations.md)
   - Esquema relacional SQLite e modelos Pydantic v2.
   - Contratos de webhooks da Evolution API v2 (Baileys) e endpoints REST do FastAPI.
   - Protocolos de notificação sonora via ntfy.

5. [RFC-004: Infraestrutura, Implantação e DevOps](file:///home/robson/Projetos_Desenvolvimento/victor-cell/pecasbot-api/docs/04_infrastructure_and_deployment.md)
   - Topologia de containers Docker Compose na nuvem Oracle Cloud Infrastructure (OCI).
   - Configurações de rede, proxies reversos Nginx e procedimentos de rollback.

6. [Relatório de Cobertura de Testes e Gaps de Infraestrutura](file:///home/robson/Projetos_Desenvolvimento/victor-cell/pecasbot-api/docs/relatorio_cobertura_testes_e_gaps_infra.md)
   - Validação automatizada de 81 testes (100% aprovados, 84% de cobertura global).
   - Mapeamento detalhado dos 4 gaps de infraestrutura física/externa pendentes de validação ao vivo.
