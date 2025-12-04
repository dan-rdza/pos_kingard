PRAGMA foreign_keys = ON;

-- =========================================
-- TABLA: business_config
-- =========================================
CREATE TABLE IF NOT EXISTS business_config (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  rfc TEXT NOT NULL,
  address TEXT NOT NULL,
  phone TEXT NOT NULL,
  thank_you TEXT NOT NULL,
  tax_rate REAL NOT NULL DEFAULT 0.00,
  currency TEXT NOT NULL DEFAULT 'MXN'
);


INSERT INTO business_config (id, name, rfc, address, phone, thank_you) VALUES
(1, 'Prescolar Libertad y Creatividad A.C.', 'LCR030414IB8', 'El Túnel 103 B, Col. Ejido La Joya, León, Gto. Mx.', '477-198-31-64', '¡Gracias por su preferencia!');


-- =========================================
-- CATÁLOGOS: grades / groups / shifts
-- =========================================
CREATE TABLE IF NOT EXISTS grades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS groups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shifts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL
);

-- =========================================
-- TABLA: parents
-- =========================================
-- CREATE TABLE IF NOT EXISTS parents (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   first_name TEXT NOT NULL,
--   second_name TEXT,
--   relationship TEXT NOT NULL DEFAULT 'padre', -- 'madre', 'padre', 'tutor'
--   email TEXT,
--   phone TEXT,
--   mobile_phone TEXT NOT NULL,
--   address TEXT,
--   active INTEGER NOT NULL DEFAULT 1,
--   created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
--   updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
-- );

-- CREATE TRIGGER IF NOT EXISTS trg_parents_updated
-- AFTER UPDATE ON parents
-- FOR EACH ROW BEGIN
--   UPDATE parents
--   SET updated_at = datetime('now','localtime')
--   WHERE id = NEW.id;
-- END;

-- CREATE INDEX IF NOT EXISTS idx_parents_phone ON parents(phone);
-- CREATE INDEX IF NOT EXISTS idx_parents_name ON parents(second_name, first_name);

-- =========================================
-- TABLA: customers
-- =========================================
CREATE TABLE IF NOT EXISTS customers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  enrollment TEXT NOT NULL UNIQUE,
  first_name TEXT NOT NULL,
  second_name TEXT,
  address TEXT,
  grade_id INTEGER REFERENCES grades(id),
  group_id INTEGER REFERENCES groups(id),
  shift_id INTEGER REFERENCES shifts(id),
  gender TEXT CHECK (gender IN ('M','F')),
  birth_date TEXT,
  curp TEXT UNIQUE,
  pay_reference TEXT,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TRIGGER IF NOT EXISTS trg_customers_updated
AFTER UPDATE ON customers
FOR EACH ROW BEGIN
  UPDATE customers
  SET updated_at = datetime('now','localtime')
  WHERE id = NEW.id;
END;

CREATE INDEX IF NOT EXISTS idx_customers_enrollment ON customers(enrollment);
CREATE INDEX IF NOT EXISTS idx_customers_nombre ON customers(second_name, first_name);
CREATE INDEX IF NOT EXISTS idx_customers_salon ON customers(grade_id, group_id, shift_id);



-- =========================================
-- TABLA: tutors
-- =========================================
CREATE TABLE IF NOT EXISTS tutors (
  tutor_id   INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  first_name TEXT NOT NULL,
  second_name TEXT,
  relationship TEXT NOT NULL, -- Padre, Madre, Tutor, Abuelo, etc.
  phone      TEXT,
  email      TEXT,
  is_primary INTEGER NOT NULL DEFAULT 0,
  active     INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE INDEX IF NOT EXISTS idx_tutors_student ON tutors(student_id);
CREATE INDEX IF NOT EXISTS idx_tutors_name ON tutors(first_name, second_name);


-- =========================================
-- TABLA: customer_parents
-- =========================================
-- CREATE TABLE IF NOT EXISTS customer_parents (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
--   parent_id INTEGER NOT NULL REFERENCES parents(id) ON DELETE CASCADE,
--   is_primary INTEGER NOT NULL DEFAULT 0,
--   can_pickup INTEGER NOT NULL DEFAULT 1,
--   emergency_contact INTEGER NOT NULL DEFAULT 0,
--   created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
--   UNIQUE(customer_id, parent_id)
-- );

-- CREATE INDEX IF NOT EXISTS idx_customer_parents_customer ON customer_parents(customer_id);
-- CREATE INDEX IF NOT EXISTS idx_customer_parents_parent ON customer_parents(parent_id);

-- =========================================
-- TABLA: sellers
-- =========================================
CREATE TABLE IF NOT EXISTS sellers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  employee_code TEXT NOT NULL UNIQUE,
  first_name TEXT NOT NULL,
  second_name TEXT,
  address TEXT,
  job_title TEXT NOT NULL,
  username TEXT UNIQUE,
  password_hash TEXT,
  role TEXT NOT NULL DEFAULT 'seller', -- 'admin', 'seller', 'report'
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TRIGGER IF NOT EXISTS trg_sellers_updated
AFTER UPDATE ON sellers
FOR EACH ROW BEGIN
  UPDATE sellers
  SET updated_at = datetime('now','localtime')
  WHERE id = NEW.id;
END;

CREATE INDEX IF NOT EXISTS idx_sellers_nombre ON sellers(second_name, first_name);
CREATE INDEX IF NOT EXISTS idx_sellers_username ON sellers(username);


INSERT INTO sellers (employee_code, first_name, second_name, job_title, username, password_hash, role) VALUES
('SUPERUSR', 'SUPER', 'USER', 'SUPER USER', 'SUPERUSR', 'Sup3r2025#', 'super'),
('USR01', 'VICTOR MANUEL', 'MATA', 'ADMINISTRADOR', 'VMATA', 'Sistema*', 'admin'),
('USR02', 'RUTH', 'ALDERETE', 'ADMINISTRADOR', 'RUTH', 'Sistema*', 'admin');


-- =========================================
-- CATÁLOGO: categories y products
-- =========================================
CREATE TABLE IF NOT EXISTS categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
  sku TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  price REAL NOT NULL CHECK (price >= 0),
  cost REAL NOT NULL DEFAULT 0 CHECK (cost >= 0),
  unit TEXT NOT NULL DEFAULT 'pz',
  kind TEXT NOT NULL DEFAULT 'Servicio',
  tax_rate REAL NOT NULL DEFAULT 0.16,
  category_id INTEGER REFERENCES categories(id),
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
  is_pos_shortcut BOOLEAN DEFAULT FALSE,
  print_logo BOOLEAN DEFAULT FALSE
);

CREATE TRIGGER IF NOT EXISTS trg_products_updated
AFTER UPDATE ON products
FOR EACH ROW BEGIN
  UPDATE products
  SET updated_at = datetime('now','localtime')
  WHERE sku = NEW.sku;
END;

CREATE INDEX IF NOT EXISTS idx_products_desc ON products(description);

-- =========================================
-- TABLA: sales
-- =========================================
CREATE TABLE IF NOT EXISTS sales (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  folio TEXT UNIQUE,
  customer_id INTEGER REFERENCES customers(id),
  seller_id INTEGER REFERENCES sellers(id),
  customer TEXT NOT NULL,
  seller TEXT NOT NULL,
  subtotal REAL NOT NULL DEFAULT 0,
  discount_total REAL NOT NULL DEFAULT 0,
  tax_total REAL NOT NULL DEFAULT 0,
  total REAL NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'paid',
  payment_status TEXT NOT NULL DEFAULT 'unpaid',
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TRIGGER IF NOT EXISTS trg_sales_updated
AFTER UPDATE ON sales
FOR EACH ROW BEGIN
  UPDATE sales
  SET updated_at = datetime('now','localtime')
  WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_sales_set_folio
AFTER INSERT ON sales
FOR EACH ROW
WHEN NEW.folio IS NULL
BEGIN
  UPDATE sales
  SET folio = 'F' || printf('%04d', NEW.id)
  WHERE id = NEW.id;
END;

CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_seller ON sales(seller_id);
CREATE INDEX IF NOT EXISTS idx_sales_created ON sales(created_at);

-- =========================================
-- TABLA: sale_items
-- =========================================
CREATE TABLE IF NOT EXISTS sale_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
  sku TEXT REFERENCES products(sku),
  description_snapshot TEXT NOT NULL,
  qty REAL NOT NULL CHECK (qty > 0),
  unit_price REAL NOT NULL CHECK (unit_price >= 0),
  discount REAL NOT NULL DEFAULT 0 CHECK (discount >= 0),
  tax_rate REAL NOT NULL DEFAULT 0.16,
  line_total REAL NOT NULL CHECK (line_total >= 0)
);

CREATE INDEX IF NOT EXISTS idx_sale_items_saleid ON sale_items(sale_id);

-- ================================
-- TABLA: Métodos de Pago
-- ================================
CREATE TABLE IF NOT EXISTS payment_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,        -- Ej: Efectivo, Tarjeta, Transferencia
    code TEXT NOT NULL UNIQUE,        -- Ej: cash, card, transfer
    active INTEGER NOT NULL DEFAULT 1
);

-- Insertar algunos valores iniciales
INSERT INTO payment_methods (name, code) VALUES
('Efectivo', 'cash'),
('Tarjeta', 'card'),
('Transferencia', 'transfer');


-- =========================================
-- TABLA: payments
-- =========================================
CREATE TABLE IF NOT EXISTS payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
  method_id INTEGER NOT NULL REFERENCES payment_methods(id),
  amount REAL NOT NULL CHECK (amount >= 0),
  reference TEXT,
  transaction_id TEXT,
  payment_date TEXT DEFAULT (date('now')),
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE INDEX IF NOT EXISTS idx_payments_saleid ON payments(sale_id);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date);

-- =========================================
-- VISTA: v_sales_calc (totales por venta)
-- =========================================
DROP VIEW IF EXISTS v_sales_calc;
CREATE VIEW v_sales_calc AS
SELECT
  s.id AS sale_id,
  COALESCE(SUM((si.qty*si.unit_price)),0) AS sub,
  COALESCE(SUM(si.discount),0) AS disc,
  COALESCE(SUM(((si.qty*si.unit_price)-si.discount)*si.tax_rate),0) AS iva,
  COALESCE(SUM(((si.qty*si.unit_price)-si.discount)
        + (((si.qty*si.unit_price)-si.discount)*si.tax_rate)),0) AS tot
FROM sales s
LEFT JOIN sale_items si ON si.sale_id = s.id
GROUP BY s.id;

-- =========================================
-- TRIGGERS: mantener totales en sales
-- =========================================
CREATE TRIGGER IF NOT EXISTS trg_items_ai AFTER INSERT ON sale_items
BEGIN
  UPDATE sales
  SET subtotal       = (SELECT sub  FROM v_sales_calc WHERE sale_id = NEW.sale_id),
      discount_total = (SELECT disc FROM v_sales_calc WHERE sale_id = NEW.sale_id),
      tax_total      = (SELECT iva  FROM v_sales_calc WHERE sale_id = NEW.sale_id),
      total          = (SELECT tot  FROM v_sales_calc WHERE sale_id = NEW.sale_id)
  WHERE id = NEW.sale_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_items_au AFTER UPDATE ON sale_items
BEGIN
  UPDATE sales
  SET subtotal       = (SELECT sub  FROM v_sales_calc WHERE sale_id = NEW.sale_id),
      discount_total = (SELECT disc FROM v_sales_calc WHERE sale_id = NEW.sale_id),
      tax_total      = (SELECT iva  FROM v_sales_calc WHERE sale_id = NEW.sale_id),
      total          = (SELECT tot  FROM v_sales_calc WHERE sale_id = NEW.sale_id)
  WHERE id = NEW.sale_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_items_ad AFTER DELETE ON sale_items
BEGIN
  UPDATE sales
  SET subtotal       = (SELECT sub  FROM v_sales_calc WHERE sale_id = OLD.sale_id),
      discount_total = (SELECT disc FROM v_sales_calc WHERE sale_id = OLD.sale_id),
      tax_total      = (SELECT iva  FROM v_sales_calc WHERE sale_id = OLD.sale_id),
      total          = (SELECT tot  FROM v_sales_calc WHERE sale_id = OLD.sale_id)
  WHERE id = OLD.sale_id;
END;


CREATE TRIGGER IF NOT EXISTS trg_payments_ai AFTER INSERT ON payments
BEGIN
    UPDATE sales
    SET payment_status = CASE
        WHEN (SELECT SUM(amount) FROM payments WHERE sale_id = NEW.sale_id) >= total
        THEN 'PAID'
        ELSE 'PARTIAL'
    END
    WHERE id = NEW.sale_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_payments_au AFTER UPDATE ON payments
BEGIN
    UPDATE sales
    SET payment_status = CASE
        WHEN (SELECT SUM(amount) FROM payments WHERE sale_id = NEW.sale_id) >= total
        THEN 'PAID'
        ELSE 'PARTIAL'
    END
    WHERE id = NEW.sale_id;
END;


CREATE TRIGGER IF NOT EXISTS trg_payments_ad AFTER DELETE ON payments
BEGIN
    UPDATE sales
    SET payment_status = CASE
        WHEN (SELECT SUM(amount) FROM payments WHERE sale_id = OLD.sale_id) >= total
        THEN 'PAID'
        ELSE 'PARTIAL'
    END
    WHERE id = OLD.sale_id;
END;

-- =========================================
-- VISTA: v_sales_paid (pagos por venta)
-- =========================================
DROP VIEW IF EXISTS v_sales_paid;
CREATE VIEW v_sales_paid AS
SELECT
  s.id AS sale_id,
  s.total AS total_doc,
  COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.sale_id = s.id),0) AS total_paid
FROM sales s;

-- =========================================
-- TRIGGERS: mantener payment_status en sales
-- =========================================
CREATE TRIGGER IF NOT EXISTS trg_pay_ai AFTER INSERT ON payments
BEGIN
  UPDATE sales
  SET payment_status = CASE
    WHEN (SELECT total_paid FROM v_sales_paid WHERE sale_id = NEW.sale_id) >= total THEN 'paid'
    WHEN (SELECT total_paid FROM v_sales_paid WHERE sale_id = NEW.sale_id) > 0    THEN 'partial'
    ELSE 'unpaid'
  END
  WHERE id = NEW.sale_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_pay_au AFTER UPDATE ON payments
BEGIN
  UPDATE sales
  SET payment_status = CASE
    WHEN (SELECT total_paid FROM v_sales_paid WHERE sale_id = NEW.sale_id) >= total THEN 'paid'
    WHEN (SELECT total_paid FROM v_sales_paid WHERE sale_id = NEW.sale_id) > 0    THEN 'partial'
    ELSE 'unpaid'
  END
  WHERE id = NEW.sale_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_pay_ad AFTER DELETE ON payments
BEGIN
  UPDATE sales
  SET payment_status = CASE
    WHEN (SELECT total_paid FROM v_sales_paid WHERE sale_id = OLD.sale_id) >= total THEN 'paid'
    WHEN (SELECT total_paid FROM v_sales_paid WHERE sale_id = OLD.sale_id) > 0    THEN 'partial'
    ELSE 'unpaid'
  END
  WHERE id = OLD.sale_id;
END;

