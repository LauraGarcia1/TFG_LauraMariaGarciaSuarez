def recommend(user, responses, number_sections = 1):
    """
    Algoritmo de recomendación que devuelve el id de x juegos basado en los contextos preferidas del usuario.

    :param user: Objeto del usuario (puede no ser necesario en este caso).
    :param responses: Diccionario con las contextos preferidas, por ejemplo:
                      {"contexts": ['time:short', 'social:children', 'mood:strategic']}
    :return: El id del juego recomendado, o None si no se encuentra coincidencia.
    """
    # Extraer la lista de contextos desde el diccionario
    contexts = responses.get("contexts", [])

    # Caso 1: Si no hay contextos, seleccionar un juego aleatorio
    if not contexts:
        sql = """
        SELECT id 
        FROM zacatrus_games
        ORDER BY RANDOM()
        LIMIT 1;
        """
        result = db_query(sql, [])
        return result[0][0] if result else None

    # Construir condiciones dinámicas para la consulta SQL.
    # Por cada contexto, creamos una condición: "contexts LIKE %s"
    context_conditions = " OR ".join(["contexts LIKE %s" for _ in contexts])
    # Y definimos los parámetros: para cada contexto, se envuelve en %...%
    params = ["%" + ctx + "%" for ctx in contexts]

    # Construir la consulta SQL usando las condiciones dinámicas.
    sql = f"""
    SELECT zg.id, zg.name, GROUP_CONCAT(DISTINCT zgc.name ORDER BY zgc.name ASC) AS contexts
    FROM (
        SELECT id, name, url
        FROM zacatrus_games
        LIMIT 10
    ) zg
    LEFT JOIN (
        SELECT DISTINCT gameid, name
        FROM zacatrus_game_contexts
    ) zgc ON zg.id = zgc.gameid
    GROUP BY zg.id, zg.name
    HAVING {context_conditions};
    """

    # Ejecutar la consulta y obtener los resultados
    result = db_query(sql, params)
    # print(result)  # Para debug; quitar en producción

    # Filtrar los juegos que coincidan con alguna de las contextos del usuario
    matching_games = []
    for row in result:
        game_id, game_name, game_contexts = row
        if not game_contexts:
            continue  # Si no hay contextos, saltar este juego
        # Separar las contextos concatenadas y limpiar espacios
        game_contexts_list = [cat.strip() for cat in game_contexts.split(',')]
        
        # Verificar si alguna de las contextos del juego coincide exactamente con alguna contexto preferida
        match_found = False
        for cat in game_contexts_list:
            for pref in contexts:
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
