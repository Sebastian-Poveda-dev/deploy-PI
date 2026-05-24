Feature: Gestion de usuarios y permisos

  Scenario: La tabla de usuarios muestra todos los usuarios con su rol y sala
    Given existe una sesion iniciada como admin
    When abre la pagina de permisos
    Then la tabla de permisos muestra sus columnas principales
    And la tabla de permisos muestra los usuarios seed
    And el usuario "a.torres" muestra rol "Asesor" y una sala
    And el usuario "s.vargas" muestra rol "Estudiante"
