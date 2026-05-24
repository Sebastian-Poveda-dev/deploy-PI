Feature: Gestion de casos desde el modal

  Background:
    Given existe una sesion iniciada como admin

  Scenario: Crear un caso con Resolucion inmediata activa los campos extra y lo cierra directamente
    Given abre la pagina de casos
    When prepara el modal para crear un caso con resolucion inmediata
    Then ve los campos extra de resolucion inmediata
    When completa y crea el caso con resolucion inmediata
    Then el caso con resolucion inmediata aparece en la tabla
    And el caso con resolucion inmediata queda cerrado o finalizado
