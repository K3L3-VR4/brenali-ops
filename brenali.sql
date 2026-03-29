CREATE TABLE proyectos (
    id              SERIAL PRIMARY KEY,
    proyecto        VARCHAR(100),
    area            VARCHAR(50),
    seccion_trabajada VARCHAR(50),
    materiales      VARCHAR(50),
    tipo_pintura    VARCHAR(50),
    colores         VARCHAR(100),
    codigos         VARCHAR(100),
    stain_glaze     VARCHAR(50),
    nombre_stain    VARCHAR(100),
    codigo_stain    VARCHAR(50),
    fecha_inicio    DATE,
    fecha_delivery  DATE,
    estado          VARCHAR(20) DEFAULT 'Terminado',
    notas           TEXT
);