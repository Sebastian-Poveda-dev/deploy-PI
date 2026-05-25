Feature: Documentos y logs del caso

  Scenario: El modal de documentos carga los archivos asociados al caso
    Given existe un caso preparado con un documento asociado
    And el admin inicia sesion para revisar documentos
    When abre la pagina de casos para documentos
    And abre el caso preparado para documentos
    And abre el modal de documentos del caso
    Then el modal de documentos del caso preparado esta abierto
    And el documento preparado aparece en la lista

  Scenario: Subir un documento desde el modal aparece en la lista
    Given existe un caso activo preparado para subir documentos
    And el admin inicia sesion para revisar documentos
    When abre la pagina de casos para documentos
    And abre el caso preparado para documentos
    And abre el modal de documentos del caso
    And sube un documento desde el modal de documentos del caso
    Then el documento subido aparece en la lista de documentos

  Scenario: El modal de seguimiento muestra el historial de cambios de estado
    Given existe un caso preparado con historial de seguimiento
    And el admin inicia sesion para revisar documentos
    When abre la pagina de casos para documentos
    And abre el caso preparado para seguimiento
    And abre el modal de seguimiento del caso
    Then el modal de seguimiento del caso preparado esta abierto
    And el historial preparado aparece en el modal de seguimiento
