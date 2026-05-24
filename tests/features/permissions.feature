Feature: Gestion de usuarios y permisos

  Scenario: La tabla de usuarios muestra todos los usuarios con su rol y sala
    Given existe una sesion iniciada como admin
    When abre la pagina de permisos
    Then la tabla de permisos muestra sus columnas principales
    And la tabla de permisos muestra los usuarios seed
    And el usuario "a.torres" muestra rol "Asesor" y una sala
    And el usuario "s.vargas" muestra rol "Estudiante"

  Scenario: Crear un usuario advisor sin seleccionar sala muestra error de validacion
    Given existe una sesion iniciada como admin
    When abre la pagina de permisos
    And intenta crear un usuario advisor sin seleccionar sala
    Then ve error de validacion por sala legal requerida
    And el modal de crear usuario sigue abierto
