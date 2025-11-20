CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE inventor_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    area_atuacao VARCHAR(150) NOT NULL,
    experiencia VARCHAR(255),
    descricao_inovacao TEXT NOT NULL,
    estagio_inovacao VARCHAR(50),
    palavras_chave VARCHAR(255)
);

CREATE TABLE conversa (
    thread_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER,
    titulo VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX ix_conversa_thread_id ON conversa(thread_id);
CREATE INDEX ix_conversa_user_id ON conversa(user_id);

CREATE TABLE mensagem (
    id SERIAL PRIMARY KEY,
    content VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    conversa_id UUID REFERENCES conversa(thread_id) ON DELETE CASCADE
);
CREATE INDEX ix_mensagem_id ON mensagem(id);