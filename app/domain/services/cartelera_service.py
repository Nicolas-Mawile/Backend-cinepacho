"""Servicio de cartelera."""

from app.domain.exceptions import (
    CarteleraNotFoundError,
    CarteleraValidationError,
    MultiplexNotFoundError,
)
from app.infrastructure.models.multiplex_cartelera import MultiplexCartelera
from app.infrastructure.repositories.cartelera_repository import CarteleraRepository


class CarteleraService:
    def __init__(self, db):
        self.repo = CarteleraRepository(db)

    def ver_cartelera_general(self):
        return self.repo.listar_general()

    def ver_cartelera_por_multiplex(self, multiplex_id: int):
        multiplex = self.repo.get_multiplex(multiplex_id)
        if not multiplex:
            raise MultiplexNotFoundError("Multiplex no encontrado")
        return self.repo.listar_por_multiplex(multiplex_id)

    def agregar_a_cartelera(self, multiplex_id: int, pelicula_id: int):
        multiplex = self.repo.get_multiplex(multiplex_id)
        if not multiplex:
            raise MultiplexNotFoundError("Multiplex no encontrado")

        pelicula = self.repo.get_pelicula(pelicula_id)
        if not pelicula:
            raise CarteleraNotFoundError("Pelicula no encontrada")
        if not pelicula.estaActiva:
            raise CarteleraValidationError("No se puede agregar una pelicula inactiva a la cartelera")

        if self.repo.existe_entrada(multiplex_id, pelicula_id):
            raise CarteleraValidationError("La pelicula ya esta en la cartelera de este multiplex")

        self.repo.agregar(multiplex_id, pelicula_id)
        return self.repo.obtener_entrada(multiplex_id, pelicula_id)

    def remover_de_cartelera(self, multiplex_id: int, pelicula_id: int):
        multiplex = self.repo.get_multiplex(multiplex_id)
        if not multiplex:
            raise MultiplexNotFoundError("Multiplex no encontrado")

        if self.repo.tiene_funciones_activas(pelicula_id, multiplex_id):
            raise CarteleraValidationError(
                "No se puede quitar la pelicula: tiene funciones activas en este multiplex"
            )

        if not self.repo.eliminar_entrada(multiplex_id, pelicula_id):
            raise CarteleraNotFoundError("La pelicula no esta en la cartelera de este multiplex")

        return True

    def agregar_a_cartelera_general(self, pelicula_id: int):
        pelicula = self.repo.get_pelicula(pelicula_id)
        if not pelicula:
            raise CarteleraNotFoundError("Pelicula no encontrada")
        if not pelicula.estaActiva:
            raise CarteleraValidationError("No se puede agregar una pelicula inactiva a la cartelera")

        multiplex_ids = self.repo.listar_multiplex_activos_ids()
        if not multiplex_ids:
            raise CarteleraNotFoundError("No hay multiplex activos para actualizar cartelera")

        existentes = {
            getattr(entrada, "multiplexId", entrada)
            for entrada in self.repo.listar_entradas_por_pelicula(pelicula_id)
            if getattr(entrada, "multiplexId", entrada) in multiplex_ids
        }

        entradas_modelo = [
            MultiplexCartelera(
                multiplexId=multiplex_id,
                peliculaId=pelicula_id,
            )
            for multiplex_id in multiplex_ids
            if multiplex_id not in existentes
        ]

        self.repo.agregar_varios(entradas_modelo)

        return {
            "peliculaId": pelicula_id,
            "multiplexesActualizados": len(entradas_modelo),
            "multiplexesSinCambio": len(existentes),
        }

    def remover_de_cartelera_general(self, pelicula_id: int):
        pelicula = self.repo.get_pelicula(pelicula_id)
        if not pelicula:
            raise CarteleraNotFoundError("Pelicula no encontrada")

        if self.repo.tiene_funciones_activas(pelicula_id):
            raise CarteleraValidationError(
                "No se puede quitar la pelicula de la cartelera general: tiene funciones activas"
            )

        eliminadas = self.repo.eliminar_por_pelicula(pelicula_id)
        if eliminadas == 0:
            raise CarteleraNotFoundError("La pelicula no esta en la cartelera general")

        return {
            "peliculaId": pelicula_id,
            "multiplexesAfectados": eliminadas,
        }