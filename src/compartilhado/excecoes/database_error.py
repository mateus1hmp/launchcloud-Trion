"""Excecoes relacionadas a camada de banco de dados."""


class DatabaseError(Exception):
    """Erro generico de comunicacao com o banco de dados."""

    def __init__(self, message: str, operation: str, original_error: Exception = None):
        self.operation = operation
        self.original_error = original_error
        super().__init__(f"[{operation}] {message}")
