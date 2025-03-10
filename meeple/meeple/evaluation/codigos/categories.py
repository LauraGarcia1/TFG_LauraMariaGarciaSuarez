def recommend(user, responses, number_sections = 1):
    """
    Algoritmo de recomendación que devuelve el id de x juegos basado en las categorías preferidas del usuario.

    :param user: Objeto del usuario (puede no ser necesario en este caso).
    :param responses: Diccionario con las categorías preferidas, por ejemplo:
                      {"categories": ['Economic', 'Negotiation', 'Political']}
    :return: El id del juego recomendado, o None si no se encuentra coincidencia.
    """
    # Extraer la lista de categorías desde el diccionario
    categories = responses.get("categories", [])

    # Caso 1: Si no hay categorías, seleccionar un juego aleatorio
    if not categories:
        sql = """
        SELECT id 
        FROM zacatrus_games
        ORDER BY RANDOM()
        LIMIT 1;
        """
        result = db_query(sql, [])
        return result[0][0] if result else None

    # Construir condiciones dinámicas para la consulta SQL.
    # Por cada categoría, creamos una condición: "categories LIKE %s"
    category_conditions = " OR ".join(["categories LIKE %s" for _ in categories])
    # Y definimos los parámetros: para cada categoría, se envuelve en %...%
    params = ["%" + cat + "%" for cat in categories]

    # Construir la consulta SQL usando las condiciones dinámicas.
    sql = f"""
    SELECT zg.id, zg.name, GROUP_CONCAT(DISTINCT zgc.name ORDER BY zgc.name ASC) AS categories
    FROM (
        SELECT id, name, url
        FROM zacatrus_games
        LIMIT 10
    ) zg
    LEFT JOIN (
        SELECT DISTINCT gameid, name
        FROM zacatrus_game_categories
    ) zgc ON zg.id = zgc.gameid
    GROUP BY zg.id, zg.name
    HAVING {category_conditions};
    """

    # Ejecutar la consulta y obtener los resultados
    result = db_query(sql, params)
    # print(result)  # Para debug; quitar en producción

    # Filtrar los juegos que coincidan con alguna de las categorías del usuario
    matching_games = []
    for row in result:
        game_id, game_name, game_categories = row
        if not game_categories:
            continue  # Si no hay categorías, saltar este juego
        # Separar las categorías concatenadas y limpiar espacios
        game_categories_list = [cat.strip() for cat in game_categories.split(',')]
        
        # Verificar si alguna de las categorías del juego coincide exactamente con alguna categoría preferida
        match_found = False
        for cat in game_categories_list:
            for pref in categories:
                if cat == pref:
                    match_found = True
                    break
            if match_found:
                break

        if match_found:
            matching_games.append(game_id)

    # Si hay juegos coincidentes, seleccionar uno al azar y devolver su ID
    if matching_games:
        if len(matching_games) >= number_sections:
            return random.sample(matching_games, number_sections)
        else:
            return random.choices(matching_games, k=number_sections)
    else:
        return None  # Si no hay coincidencias, se devuelve None
