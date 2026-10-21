
from database import (
    incluir_ingresso,
    buscar_ingresso,
    excluir_ingresso,
    resumir_situacoes,
)

# 1. Incluir um ingresso de teste
incluir_ingresso("TESTE001", 20, "fora")

# 2. Conferir se foi cadastrado
print("Cadastrado:", buscar_ingresso("TESTE001"))
print("Resumo após inclusão:", resumir_situacoes())

# 3. Excluir o ingresso de teste
excluir_ingresso("TESTE001")

# 4. Conferir se foi removido
print("Após exclusão:", buscar_ingresso("TESTE001"))
print("Resumo final:", resumir_situacoes())
