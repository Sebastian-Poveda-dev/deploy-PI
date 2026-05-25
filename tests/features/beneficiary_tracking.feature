Feature: Seguimiento del caso para beneficiarios

  Scenario: Un beneficiario autenticado ve el estado de sus casos en su dashboard
    Given existe un caso asociado al beneficiario jperez
    When el beneficiario jperez inicia sesion
    Then entra a la vista autenticada de sus casos
    And no ve la tabla completa de staff
    And ve el estado de sus casos

  Scenario: El seguimiento publico con cedula valida muestra los casos
    Given existe un caso asociado a la cedula "1001234567"
    When abre la pagina de seguimiento publico
    And consulta el seguimiento publico con la cedula "1001234567"
    Then el seguimiento publico de beneficiario muestra casos asociados
    And el seguimiento publico de beneficiario muestra estado o progreso del caso

  Scenario: El seguimiento publico con cedula inexistente muestra mensaje de no encontrado
    When abre la pagina de seguimiento publico
    And consulta el seguimiento publico con la cedula "9999999999"
    Then el seguimiento publico de beneficiario muestra mensaje de no encontrado
