movies_query = f"""
                SELECT
                   fw.id,
                   fw.title,
                   fw.description,
                   fw.rating,
                   fw.modified as fw_modified,
                   MAX(g.modified) as g_modified,
                   MAX(p.modified) as p_modified,
                   COALESCE (
                       json_agg(
                           DISTINCT jsonb_build_object(
                               'person_role', pfw.role,
                               'person_id', p.id,
                               'person_name', p.full_name
                           )
                       ) FILTER (WHERE p.id is not null),
                       '[]'
                   ) as persons,
                   COALESCE (
                       json_agg(
                           DISTINCT jsonb_build_object(
                               'name', g.name,
                               'id', g.id
                           )
                       ) FILTER (WHERE g.id is not null),
                       '[]'
                   ) as genres
                FROM content.film_work fw
                LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
                LEFT JOIN content.person p ON p.id = pfw.person_id
                LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
                LEFT JOIN content.genre g ON g.id = gfw.genre_id
                WHERE fw.modified > '%(last_update)s'
                      OR g.modified > '%(last_update)s'
                      OR p.modified > '%(last_update)s'
                GROUP BY fw.id
                ORDER BY fw.modified;
            """

persons_query = f"""
                    SELECT
                    id,
                    full_name, 
                    modified
                    FROM content.person
                    WHERE modified > '%(last_update)s'
                    GROUP BY id
                    ORDER BY modified;
                """

genres_query =  f"""
                    SELECT
                    id,
                    name,
                    description,
                    modified
                    FROM content.genre
                    WHERE modified > '%(last_update)s'
                    GROUP BY id
                    ORDER BY modified;
                    """