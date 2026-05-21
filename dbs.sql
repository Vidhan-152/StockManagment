create database stock;
use stock;

-- ============================================================
--  1. USERS
-- ============================================================
CREATE TABLE users (
    id              INT             NOT NULL AUTO_INCREMENT,
    name            VARCHAR(100)    NOT NULL,
    email           VARCHAR(150)    NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
 
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_email (email)
);
 
-- ============================================================
--  2. CATEGORIES
-- ============================================================
CREATE TABLE categories (
    id          INT             NOT NULL AUTO_INCREMENT,
    name        VARCHAR(100)    NOT NULL,
    description TEXT,
    created_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
 
    PRIMARY KEY (id),
    UNIQUE KEY uq_categories_name (name)
);
 
-- ============================================================
--  3. SUPPLIERS
-- ============================================================
CREATE TABLE suppliers (
    id                  INT             NOT NULL AUTO_INCREMENT,
    name                VARCHAR(150)    NOT NULL,
    contact_name        VARCHAR(100),
    email               VARCHAR(150),
    phone               VARCHAR(20),
    avg_lead_days       INT             NOT NULL DEFAULT 0,
    reliability_score   FLOAT           NOT NULL DEFAULT 1.0 COMMENT '0.0 to 1.0',
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
 
    PRIMARY KEY (id),
    CONSTRAINT chk_reliability CHECK (reliability_score BETWEEN 0.0 AND 1.0)
);
 
-- ============================================================
--  4. PRODUCTS
-- ============================================================
CREATE TABLE products (
    id                  INT             NOT NULL AUTO_INCREMENT,
    user_id             INT             NOT NULL,
    category_id         INT,
    name                VARCHAR(150)    NOT NULL,
    sku                 VARCHAR(100)    NOT NULL,
    description         TEXT,
    unit_price          DECIMAL(10, 2)  NOT NULL DEFAULT 0.00,
    stock               INT             NOT NULL DEFAULT 0,
    reorder_threshold   INT             NOT NULL DEFAULT 10  COMMENT 'Alert fires when stock falls below this',
    overstock_threshold INT             NOT NULL DEFAULT 500 COMMENT 'Alert fires when stock exceeds this',
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
 
    PRIMARY KEY (id),
    UNIQUE KEY uq_products_sku (sku),
    CONSTRAINT fk_products_user     FOREIGN KEY (user_id)     REFERENCES users(id)      ON DELETE CASCADE,
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    CONSTRAINT chk_stock            CHECK (stock >= 0),
    CONSTRAINT chk_unit_price       CHECK (unit_price >= 0)
);
 
-- ============================================================
--  5. PRICE HISTORY
--     Auto-populated via trigger whenever unit_price changes.
-- ============================================================
CREATE TABLE price_history (
    id          INT             NOT NULL AUTO_INCREMENT,
    product_id  INT             NOT NULL,
    old_price   DECIMAL(10, 2)  NOT NULL,
    new_price   DECIMAL(10, 2)  NOT NULL,
    changed_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
 
    PRIMARY KEY (id),
    CONSTRAINT fk_price_history_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_price_history_product (product_id),
    INDEX idx_price_history_date    (changed_at)
);
 
-- Trigger: log price changes automatically
DELIMITER $$
CREATE TRIGGER trg_product_price_change
BEFORE UPDATE ON products
FOR EACH ROW
BEGIN
    IF OLD.unit_price <> NEW.unit_price THEN
        INSERT INTO price_history (product_id, old_price, new_price)
        VALUES (OLD.id, OLD.unit_price, NEW.unit_price);
    END IF;
END$$
DELIMITER ;
 
-- ============================================================
--  6. ORDERS
-- ============================================================
CREATE TABLE orders (
    id              INT             NOT NULL AUTO_INCREMENT,
    user_id         INT             NOT NULL,
    type            ENUM('sale', 'purchase')                   NOT NULL,
    status          ENUM('pending', 'completed', 'cancelled')  NOT NULL DEFAULT 'pending',
    total_amount    DECIMAL(12, 2)  NOT NULL DEFAULT 0.00,
    order_date      DATE            NOT NULL,
    expected_date   DATE,
    delivered_date  DATE,
    notes           TEXT,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

 
    PRIMARY KEY (id),
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_orders_user   (user_id),
    INDEX idx_orders_type   (type),
    INDEX idx_orders_status (status),
    INDEX idx_orders_date   (order_date)
);
 
-- ============================================================
--  7. ORDER ITEMS
-- ============================================================
CREATE TABLE order_items (
    id          INT             NOT NULL AUTO_INCREMENT,
    order_id    INT             NOT NULL,
    product_id  INT             NOT NULL,
    supplier_id INT,
    quantity    INT             NOT NULL,
    unit_price  DECIMAL(10, 2)  NOT NULL,
    line_total  DECIMAL(12, 2)  GENERATED ALWAYS AS (quantity * unit_price) STORED,
 
    PRIMARY KEY (id),
    CONSTRAINT fk_order_items_order    FOREIGN KEY (order_id)    REFERENCES orders(id)    ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product  FOREIGN KEY (product_id)  REFERENCES products(id)  ON DELETE RESTRICT,
    CONSTRAINT fk_order_items_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL,
    CONSTRAINT chk_order_item_qty      CHECK (quantity > 0),
    INDEX idx_order_items_order   (order_id),
    INDEX idx_order_items_product (product_id)
);
 
-- ============================================================
--  8. TRANSACTIONS
--     Atomic stock movement log — one row per stock change.
--     order_item_id is NULL for manual adjustments.
-- ============================================================
CREATE TABLE transactions (
    id              INT             NOT NULL AUTO_INCREMENT,
    product_id      INT             NOT NULL,
    user_id         INT             NOT NULL,
    order_item_id   INT,
    type            ENUM('sale', 'purchase', 'adjustment')  NOT NULL,
    quantity        INT             NOT NULL COMMENT 'Always positive; type determines direction',
    stock_before    INT             NOT NULL,
    stock_after     INT             NOT NULL,
    unit_price      DECIMAL(10, 2)  NOT NULL,
    total_amount    DECIMAL(12, 2)  GENERATED ALWAYS AS (quantity * unit_price) STORED,
    notes           TEXT,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
 
    PRIMARY KEY (id),
    CONSTRAINT fk_txn_product    FOREIGN KEY (product_id)    REFERENCES products(id)    ON DELETE RESTRICT,
    CONSTRAINT fk_txn_user       FOREIGN KEY (user_id)       REFERENCES users(id)       ON DELETE RESTRICT,
    CONSTRAINT fk_txn_order_item FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE SET NULL,
    CONSTRAINT chk_txn_quantity  CHECK (quantity > 0),
    INDEX idx_txn_product    (product_id),
    INDEX idx_txn_user       (user_id),
    INDEX idx_txn_type       (type),
    INDEX idx_txn_created_at (created_at)
);
 
-- ============================================================
--  9. PREDICTIONS
--     Stores ML output per product with model metadata inline.
-- ============================================================
CREATE TABLE predictions (
    id                      INT             NOT NULL AUTO_INCREMENT,
    product_id              INT             NOT NULL,
    model_type              VARCHAR(50)     NOT NULL COMMENT 'e.g. linear_regression, arima, prophet',
    predicted_demand        INT             NOT NULL,
    suggested_reorder_qty   INT             NOT NULL,
    confidence_score        FLOAT                    COMMENT '0.0 to 1.0',
    mae                     FLOAT                    COMMENT 'Mean Absolute Error of this run',
    rmse                    FLOAT                    COMMENT 'Root Mean Squared Error of this run',
    training_data_days      INT             NOT NULL COMMENT 'Days of history used to train',
    prediction_for_date     DATE            NOT NULL,
    created_at              TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
 
    PRIMARY KEY (id),
    CONSTRAINT fk_prediction_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT chk_confidence        CHECK (confidence_score BETWEEN 0.0 AND 1.0),
    INDEX idx_prediction_product (product_id),
    INDEX idx_prediction_date    (prediction_for_date)
);
 
-- ============================================================
--  10. ALERTS
-- ============================================================
CREATE TABLE alerts (
    id          INT         NOT NULL AUTO_INCREMENT,
    product_id  INT         NOT NULL,
    type        ENUM('low_stock', 'overstock', 'dead_stock')  NOT NULL,
    message     TEXT        NOT NULL,
    status      ENUM('active', 'resolved')                    NOT NULL DEFAULT 'active',
    created_at  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
 
    PRIMARY KEY (id),
    CONSTRAINT fk_alert_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_alert_product (product_id),
    INDEX idx_alert_status  (status),
    INDEX idx_alert_type    (type)
);









