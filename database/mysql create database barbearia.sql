CREATE DATABASE barbearia;
USE barbearia;

CREATE TABLE orcamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    servico VARCHAR(100) NOT NULL,
    data_hora_solicitada DATETIME,
    consentimento BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);