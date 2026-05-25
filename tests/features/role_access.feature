Feature: Control de acceso por rol

  Scenario: Un beneficiario no ve la tabla de casos de staff
    Given existe una sesion iniciada como beneficiario jperez
    When el beneficiario abre su vista de casos
    Then no ve la tabla completa de casos de staff
    And ve la vista de estado de sus propios casos

  Scenario: Un student no ve el boton Cerrar Caso
    Given existe un caso activo asignado al student s.vargas
    And existe una sesion iniciada como student s.vargas
    When el student abre la pagina de casos
    And abre el caso asignado al student para control de acceso
    Then no ve el boton Cerrar Caso
    And puede ver la opcion Solicitar Reasignacion

  Scenario: Un student no puede acceder a permisos
    Given existe una sesion iniciada como student s.vargas
    When el student intenta abrir permisos directamente
    Then no puede ver la administracion de permisos

  Scenario: Un advisor no puede crear usuarios
    Given existe una sesion iniciada como advisor a.torres
    When el advisor intenta abrir permisos directamente
    Then no puede ver la administracion de usuarios
    And no ve el boton Crear Usuario
