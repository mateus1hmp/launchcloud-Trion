"""
Porta (Port) do repositorio de triagem.

Define o contrato que qualquer adaptador de banco de dados deve implementar.
O dominio depende APENAS desta interface — nunca de um SDK especifico (boto3, etc).
"""

from abc import ABC, abstractmethod


class TriageRepositoryInterface(ABC):
    """Contrato para persistencia e consulta de triagens."""

    @abstractmethod
    def save_triage(self, triage_data: dict) -> dict:
        """
        Persiste um registro completo de triagem.

        Args:
            triage_data: Documento de triagem contendo input, output e metadata.
                         Deve incluir obrigatoriamente 'patient_id' e 'timestamp'.

        Returns:
            O documento persistido com confirmacao.

        Raises:
            DatabaseError: Se houver falha na comunicacao com o banco.
        """

    @abstractmethod
    def get_triage_by_patient(self, patient_id: str, limit: int = 10) -> list[dict]:
        """
        Retorna o historico de triagens de um paciente, ordenado do mais recente.

        Args:
            patient_id: Identificador pseudonimizado do paciente (ex: 'PAT-2024-001').
            limit: Numero maximo de registros retornados (default: 10).

        Returns:
            Lista de documentos de triagem ordenados por timestamp descendente.

        Raises:
            DatabaseError: Se houver falha na comunicacao com o banco.
        """
