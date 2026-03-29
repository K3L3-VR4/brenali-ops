CREATE TABLE inventario (
    id              SERIAL PRIMARY KEY,
    categoria       VARCHAR(50),
    material        VARCHAR(100),
    color_tipo      VARCHAR(50),
    unidad          VARCHAR(20),
    stock_inicial   NUMERIC(10,2),
    stock_actual    NUMERIC(10,2),
    ubicacion       VARCHAR(100),
    stock_minimo    NUMERIC(10,2),
    estado          VARCHAR(20),
    notas           TEXT
);