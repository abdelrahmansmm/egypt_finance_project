CREATE TABLE IF NOT EXISTS cbe_exchange_rates (
    id              SERIAL PRIMARY KEY,
    currency_code   VARCHAR(10) NOT NULL,
    currency_name   VARCHAR(100),
    buy_rate        NUMERIC(12, 4),
    sell_rate       NUMERIC(12, 4),
    rate_date       DATE NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS egx_stocks (
    id              SERIAL PRIMARY KEY,
    ticker          VARCHAR(20) NOT NULL,
    company_name    VARCHAR(200),
    open_price      NUMERIC(14, 4),
    close_price     NUMERIC(14, 4),
    high_price      NUMERIC(14, 4),
    low_price       NUMERIC(14, 4),
    volume          BIGINT,
    trade_date      DATE NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS worldbank_indicators (
    id              SERIAL PRIMARY KEY,
    indicator_code  VARCHAR(50) NOT NULL,
    indicator_name  VARCHAR(200),
    year            INT NOT NULL,
    value           NUMERIC(20, 6),
    country         VARCHAR(10) DEFAULT 'EG',
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS imf_data (
    id              SERIAL PRIMARY KEY,
    indicator       VARCHAR(100) NOT NULL,
    period          VARCHAR(20) NOT NULL,
    value           NUMERIC(20, 6),
    unit            VARCHAR(50),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cbe_rates_date ON cbe_exchange_rates(rate_date);
CREATE INDEX IF NOT EXISTS idx_cbe_rates_currency ON cbe_exchange_rates(currency_code);
CREATE INDEX IF NOT EXISTS idx_egx_ticker ON egx_stocks(ticker);
CREATE INDEX IF NOT EXISTS idx_egx_date ON egx_stocks(trade_date);
CREATE INDEX IF NOT EXISTS idx_wb_indicator ON worldbank_indicators(indicator_code, year);


CREATE DATABASE metastore;
GRANT ALL PRIVILEGES ON DATABASE metastore TO egfinanceuser;


ALTER USER egfinanceuser WITH PASSWORD 'egpassword123';