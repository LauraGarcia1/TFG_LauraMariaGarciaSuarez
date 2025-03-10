def recommend(user, responses, number_sections=1):
    """
    Función que recomienda juegos de mesa de forma aleatoria basada en las respuestas del usuario.
    
    Args:
        user (User): El usuario autenticado.
        responses (list): Las preferencias o categorías que el usuario tiene para los juegos.
        number_sections (int, optional): Número de juegos a recomendar. Default es 1.

    Returns:
        list: Lista de juegos recomendados.
    """
    # Construir la consulta SQL usando las condiciones dinámicas.
    sql = """
    SELECT id
    FROM zacatrus_games
    ORDER BY RAND()
    LIMIT %s
    """
    
    # Ejecutar la consulta y obtener los resultados
    games = db_query(sql, [number_sections])
    
    recommended_games = []

    for game in games:
        recommended_games.append(game[0])
    
    return recommended_games
