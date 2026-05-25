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

  Scenario: Crear un usuario advisor con sala asigna correctamente la categoria
    Given existe una sesion iniciada como admin
    When abre la pagina de permisos
    And crea un usuario advisor con sala asignada
    Then el usuario advisor creado aparece en la tabla
    And el usuario advisor creado muestra rol Asesor
    And el usuario advisor creado muestra la sala asignada

  Scenario: Desactivar un usuario lo marca como inactivo en la tabla
    Given existe una sesion iniciada como admin
    When abre la pagina de permisos
    And crea un usuario temporal activo
    When desactiva el usuario temporal desde el modal de edicion
    Then el usuario temporal aparece como inactivo en la tabla

  Scenario: Cambiar el rol de un usuario se refleja en la columna Rol
    Given existe una sesion iniciada como admin
    When abre la pagina de permisos
    And crea un usuario temporal activo
    When cambia el rol del usuario temporal a advisor
    Then el usuario temporal muestra rol Asesor en la tabla

  Scenario: Editar la sala de un advisor se actualiza en la columna Sala
    Given existe una sesion iniciada como admin
    When abre la pagina de permisos
    And crea un advisor temporal con sala inicial
    When cambia la sala del advisor temporal
    Then el advisor temporal muestra la nueva sala en la tabla
