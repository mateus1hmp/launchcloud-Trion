"""
Adaptador DynamoDB para o repositorio de triagem.

Implementa a interface TriageRepositoryInterface usando boto3.
Esta e a unica camada que conhece o SDK da AWS — o dominio permanece desacoplado.
"""

import logging
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from src.dominio.repositorios.triage_repository_interface import TriageRepositoryInterface
from src.compartilhado.excecoes.database_error import DatabaseError

logger = logging.getLogger(__name__)

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "MediFlow-Triages")


class DynamoDBTriageRepository(TriageRepositoryInterface):
    """Implementacao concreta do repositorio usando Amazon DynamoDB."""

    def __init__(self, table_name: str = None):
        self._table_name = table_name or TABLE_NAME
        self._dynamodb = boto3.resource("dynamodb")
        self._table = self._dynamodb.Table(self._table_name)

    def save_triage(self, triage_data: dict) -> dict:
        """
        Persiste um documento de triagem na tabela MediFlow-Triages.

        O DynamoDB nao aceita float — valores decimais sao convertidos
        automaticamente para Decimal antes da escrita.
        """
        try:
            item = self._convert_floats_to_decimal(triage_data)
            self._table.put_item(Item=item)

            logger.info({
                "action": "save_triage",
                "patient_id": triage_data.get("patient_id"),
                "triage_id": triage_data.get("triage_id"),
                "status": "success"
            })

            return triage_data

        except ClientError as error:
            logger.error({
                "action": "save_triage",
                "patient_id": triage_data.get("patient_id"),
                "error_code": error.response["Error"]["Code"],
                "error_message": error.response["Error"]["Message"],
                "status": "failure"
            })
            raise DatabaseError(
                message=error.response["Error"]["Message"],
                operation="PutItem",
                original_error=error
            )

    def get_triage_by_patient(self, patient_id: str, limit: int = 10) -> list[dict]:
        """
        Consulta triagens de um paciente ordenadas por timestamp descendente.

        Usa Query com PK = patient_id e ScanIndexForward=False para ordem decrescente.
        """
        try:
            response = self._table.query(
                KeyConditionExpression=Key("patient_id").eq(patient_id),
                ScanIndexForward=False,
                Limit=limit
            )

            logger.info({
                "action": "get_triage_by_patient",
                "patient_id": patient_id,
                "results_count": response.get("Count", 0),
                "status": "success"
            })

            items = response.get("Items", [])
            return [self._convert_decimals_to_float(item) for item in items]

        except ClientError as error:
            logger.error({
                "action": "get_triage_by_patient",
                "patient_id": patient_id,
                "error_code": error.response["Error"]["Code"],
                "error_message": error.response["Error"]["Message"],
                "status": "failure"
            })
            raise DatabaseError(
                message=error.response["Error"]["Message"],
                operation="Query",
                original_error=error
            )

    # ------------------------------------------------------------------
    # Helpers internos — conversao float <-> Decimal para DynamoDB
    # ------------------------------------------------------------------

    def _convert_floats_to_decimal(self, data):
        """DynamoDB nao suporta float. Converte recursivamente para Decimal."""
        if isinstance(data, float):
            return Decimal(str(data))
        if isinstance(data, dict):
            return {key: self._convert_floats_to_decimal(value) for key, value in data.items()}
        if isinstance(data, list):
            return [self._convert_floats_to_decimal(item) for item in data]
        return data

    def _convert_decimals_to_float(self, data):
        """Converte Decimal de volta para float/int na leitura."""
        if isinstance(data, Decimal):
            return int(data) if data == int(data) else float(data)
        if isinstance(data, dict):
            return {key: self._convert_decimals_to_float(value) for key, value in data.items()}
        if isinstance(data, list):
            return [self._convert_decimals_to_float(item) for item in data]
        return data
