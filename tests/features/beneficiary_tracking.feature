Feature: Seguimiento del caso para beneficiarios

  Scenario: Un beneficiario autenticado ve el estado de sus casos en su dashboard
    Given existe un caso asociado al beneficiario jperez
    When el beneficiario jperez inicia sesion
    Then entra a la vista autenticada de sus casos
    And no ve la tabla completa de staff
    And ve el estado de sus casos
