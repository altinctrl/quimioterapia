SELECT
    id,
    paciente_id,
    poltrona_id,
    data,
    turno,
    horario_inicio,
    horario_fim,
    status,
    status_farmacia,
    encaixe,
    hora_inicio_real,
    hora_fim_real
FROM
    agendamentos
WHERE
    data = :data
ORDER BY
    horario_inicio ASC