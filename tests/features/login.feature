Feature: Autenticacion de usuarios

  Scenario Outline: Login con credenciales validas redirige al dashboard segun rol
    Given el usuario esta en la pagina de login
    When ingresa el usuario "<usuario>" y la contrasena "<contrasena>"
    Then es redirigido a "<ruta>"
    And ve contenido autenticado para "<rol>"

    Examples:
      | rol         | usuario  | contrasena  | ruta             |
      | admin       | admin    | admin1234   | /dashboard       |
      | advisor     | a.torres | advisor1234 | /dashboard       |
      | student     | s.vargas | student1234 | /dashboard       |
      | beneficiary | jperez   | ben1234     | /dashboard/cases |

  Scenario: Login con credenciales invalidas muestra error y no redirige
    Given el usuario esta en la pagina de login
    When ingresa el usuario "admin" y la contrasena "incorrecta"
    Then ve un mensaje de error de autenticacion
    And permanece en la pagina de login

  Scenario: Acceder a una ruta protegida sin sesion muestra error de carga
    Given el visitante no tiene sesion iniciada
    When intenta acceder a la ruta protegida "/dashboard/cases"
    Then permanece en la ruta protegida
    And ve un error de carga de casos
