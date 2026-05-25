Feature: Control de acceso por rol

  Scenario: Un beneficiario no ve la tabla de casos de staff
    Given existe una sesion iniciada como beneficiario jperez
    When el beneficiario abre su vista de casos
    Then no ve la tabla completa de casos de staff
    And ve la vista de estado de sus propios casos
