Feature: Dashboard y gestion de casos

  Background:
    Given existe una sesion iniciada como admin

  Scenario: El dashboard carga la tabla de casos sin errores
    When abre la pagina de casos
    Then la tabla de casos carga sin errores

  Scenario: El contador de casos activos y pendientes refleja el estado real
    When abre la pagina de casos
    Then los estados activos y pendientes aparecen segun los casos cargados

  Scenario: La tabla filtra casos al usar el buscador
    Given abre la pagina de casos
    When filtra la tabla por el beneficiario de la primera fila
    Then la tabla muestra solo casos que coinciden con el filtro

  Scenario: Abrir el modal de caso desde la tabla muestra la informacion correcta
    Given abre la pagina de casos
    When abre el primer caso de la tabla
    Then el modal del caso muestra la informacion correcta

  Scenario: Un admin puede crear un caso y aparece en la tabla
    Given abre la pagina de casos
    When crea un caso nuevo desde el modal
    Then el caso nuevo aparece en la tabla

  Scenario: Crear un caso sin campos obligatorios muestra errores de validacion
    Given abre la pagina de casos
    When intenta crear un caso sin campos obligatorios
    Then ve errores de validacion del caso

  Scenario: El selector de Proceso se habilita solo despues de elegir una Sala
    Given abre la pagina de casos
    When abre el modal de creacion de caso
    Then el selector de proceso esta deshabilitado
    When selecciona una sala
    Then el selector de proceso queda habilitado
