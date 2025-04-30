Análise de Complexidade – heapq

-> `heapq.heappush()`: adicionar chamado
-> Complexidade:O(log n)
  Cada inserção reorganiza parcialmente a heap para manter a propriedade de min-heap, o que exige no máximo log n comparações.

-> `heapq.heappop()`: remover chamado de maior prioridade
-> Complexidade: O (log n)
  A remoção do menor elemento (maior prioridade) também reorganiza a heap, com custo proporcional à altura da árvore binária (logarítmica).


Comparação com Alternativas

| Estrutura             | Inserção   | Remoção do mais prioritário | Comentário                                      |
|-----------------------|------------|-----------------------------|-------------------------------------------------|
| Heap (heapq)          | O (log n)  | O (log n)                   | Ideal para fila de prioridades.                 |
| Lista Ordenada        | O (n)      | O (1)                       | Inserção lenta, mas remoção rápida.             |
| Lista Não Ordenada    | O (1)      | O (n)                       | Inserção rápida, mas busca/remoção lenta.       |
| Fila de prioridade    | O (log n)  | O (log n)                   | Mais flexível, mas mais complexa de implementar.|
  com árvore balanceada

➡ Conclusão: A `heapq` oferece o melhor custo-benefício em Python puro, especialmente considerando o volume crescente de chamados.


Escalabilidade do Sistema

-> Comportamento com volume crescente de chamados:
- A estrutura heap é eficiente mesmo com milhares de elementos.
- Operações de push/pop mantêm desempenho consistente (O(log n)), diferente de listas que degradam para O(n).

-> Pontos de atenção com escalabilidade:
- Se houver centenas de milhares de chamados simultâneos, pode valer a pena:
  - Persistir os dados em um banco (Redis, SQLite, PostgreSQL).
  - Usar tarefas assíncronas/processamento em lote.
  - Aplicar sharding por cliente/tipo de chamado para balanceamento.


-> Resumo Final

| Aspecto                       | Resultado |
|-------------------------------|-----------|
| Inserção (heappush)           | O(log n)  |
| Remoção (heappop)             | O(log n)  |
| Ideal para grande volume?     | ✅ Sim    |
| Melhor que listas simples?    | ✅ Muito mais eficiente |


PARA RODAR O CÓDIGO 
python -m uvicorn FilaPrioridade:app --reload

