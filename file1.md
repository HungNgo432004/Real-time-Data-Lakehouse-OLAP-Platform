Bước 1: tạo conf để connection mysql tới redpanda
Bước 2: Chạy Job đồng bộ dữ liệu (từ MySQL sang Redpanda) Bạn mở Terminal và chạy lệnh sau:
docker exec -it seatunnel-master /opt/seatunnel/bin/seatunnel.sh --config /opt/seatunnel/jobs/mysql-to-redpanda.conf
sau bước này các dữ liệu sẽ đổ về redpanda
Ran command: `docker exec starrocks-fe mysql -h 127.0.0.1 -P 9030 -u root -e "SHOW DATABASES;"`

StarRocks đang chạy tốt! Bây giờ mình sẽ hướng dẫn bạn chi tiết từng bước để tự làm nhé.

---

## Giai đoạn 1: Tạo Database & Tables trong StarRocks

### Cách kết nối vào StarRocks

StarRocks dùng giao thức MySQL, nên bạn có **2 cách** để kết nối:

**Cách 1 (nhanh, không cần cài gì thêm) - Dùng MySQL CLI có sẵn bên trong container StarRocks:**
```bash
docker exec -it starrocks-fe mysql -h 127.0.0.1 -P 9030 -u root
```
→ Bạn sẽ vào ngay giao diện dòng lệnh SQL của StarRocks.

**Cách 2 (giao diện đồ họa) - Dùng DBeaver:**
- Tạo kết nối mới, chọn loại **MySQL**
- Host: `localhost`, Port: `9030`, User: `root`, Password: *(để trống)*

---

### Hiểu cấu trúc bảng trong StarRocks

Bảng StarRocks khác MySQL ở 2 điểm quan trọng:
1. **Bắt buộc phải khai báo loại bảng** (`PRIMARY KEY`, `DUPLICATE KEY`, `AGGREGATE KEY`).
   - **`PRIMARY KEY`**: Dùng khi dữ liệu có thể bị cập nhật (UPDATE). Khuyên dùng cho hầu hết các trường hợp.
   - **`DUPLICATE KEY`**: Dùng khi dữ liệu chỉ thêm mới (INSERT), không update.
2. **Bắt buộc phải có `DISTRIBUTED BY`**: Khai báo StarRocks dàn đều dữ liệu theo cột nào.

---

### Script SQL tạo Database & Tables

Dựa vào tên các bảng trong file config của bạn (`df_customers`, `df_orderitems`, `df_products`, `df_payments`, `df_orders`), đây là script SQL mẫu bạn cần chạy. Bạn hãy **điều chỉnh kiểu dữ liệu** cho đúng với schema MySQL thực tế của mình:

```sql
-- Bước 1: Tạo database mới trong StarRocks
CREATE DATABASE IF NOT EXISTS ecommerce_olap;

-- Bước 2: Chọn database vừa tạo
USE ecommerce_olap;

-- Bảng df_customers
CREATE TABLE IF NOT EXISTS df_customers (
    customer_id     INT          NOT NULL  COMMENT "Mã khách hàng (khóa chính)",
    customer_name   VARCHAR(255)           COMMENT "Tên khách hàng",
    email           VARCHAR(255)           COMMENT "Email",
    phone           VARCHAR(50)            COMMENT "Số điện thoại",
    created_at      DATETIME               COMMENT "Ngày tạo"
)
PRIMARY KEY (customer_id)
DISTRIBUTED BY HASH(customer_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");

-- Bảng df_products
CREATE TABLE IF NOT EXISTS df_products (
    product_id      INT          NOT NULL  COMMENT "Mã sản phẩm",
    product_name    VARCHAR(255)           COMMENT "Tên sản phẩm",
    category        VARCHAR(100)           COMMENT "Danh mục",
    price           DECIMAL(10, 2)         COMMENT "Giá"
)
PRIMARY KEY (product_id)
DISTRIBUTED BY HASH(product_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");

-- Bảng df_orders
CREATE TABLE IF NOT EXISTS df_orders (
    order_id        INT          NOT NULL  COMMENT "Mã đơn hàng",
    customer_id     INT                    COMMENT "Mã khách hàng",
    order_date      DATETIME               COMMENT "Ngày đặt hàng",
    status          VARCHAR(50)            COMMENT "Trạng thái đơn hàng",
    total_amount    DECIMAL(10, 2)         COMMENT "Tổng tiền"
)
PRIMARY KEY (order_id)
DISTRIBUTED BY HASH(order_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");

-- Bảng df_orderitems
CREATE TABLE IF NOT EXISTS df_orderitems (
    order_item_id   INT          NOT NULL  COMMENT "Mã dòng đơn hàng",
    order_id        INT                    COMMENT "Mã đơn hàng",
    product_id      INT                    COMMENT "Mã sản phẩm",
    quantity        INT                    COMMENT "Số lượng",
    unit_price      DECIMAL(10, 2)         COMMENT "Đơn giá"
)
PRIMARY KEY (order_item_id)
DISTRIBUTED BY HASH(order_item_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");

-- Bảng df_payments
CREATE TABLE IF NOT EXISTS df_payments (
    payment_id      INT          NOT NULL  COMMENT "Mã thanh toán",
    order_id        INT                    COMMENT "Mã đơn hàng",
    payment_method  VARCHAR(50)            COMMENT "Phương thức thanh toán",
    amount          DECIMAL(10, 2)         COMMENT "Số tiền",
    payment_date    DATETIME               COMMENT "Ngày thanh toán"
)
PRIMARY KEY (payment_id)
DISTRIBUTED BY HASH(payment_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");
```

> ⚠️ **Quan trọng:** Script SQL ở trên là **mẫu tham khảo**. Bạn cần mở MySQL lên, chạy `DESCRIBE df_customers;` (hoặc `SHOW CREATE TABLE df_customers;`) để xem đúng các cột và kiểu dữ liệu thực tế rồi điều chỉnh lại script cho khớp.

---

### Quy trình tóm gọn cho bạn tự làm:

1. **Xem schema MySQL**: Kết nối vào MySQL → chạy `SHOW CREATE TABLE tên_bảng;` cho từng bảng.
2. **Vào StarRocks**: Chạy `docker exec -it starrocks-fe mysql -h 127.0.0.1 -P 9030 -u root`.
3. **Chạy script SQL**: Tạo database → tạo từng bảng theo schema đã xem ở bước 1.
4. **Kiểm tra**: Chạy `SHOW TABLES IN ecommerce_olap;` để xác nhận các bảng đã tạo thành công.

Sau khi tạo xong bảng, bạn tiếp tục sang **Giai đoạn 2** (hút dữ liệu từ Redpanda vào StarRocks bằng Routine Load)!




Viewed docker-compose.yml:1-35
Ran command: `type d:\dashboard-stack-maintest\redpanda\.env`
Ran command: `docker exec redpanda-0 rpk topic list`

Dữ liệu đã có trong Redpanda rồi! Bây giờ sang Giai đoạn 2 nhé.

---

## Giai đoạn 2: Hút dữ liệu từ Redpanda vào StarRocks bằng Routine Load

### 📚 Lý thuyết quan trọng cần hiểu trước

**Routine Load là gì?**
Đây là một tính năng riêng của StarRocks (không cần cài thêm gì). Nó hoạt động như một **"người hầu" chạy nền 24/7** bên trong StarRocks. Bạn chỉ cần ra lệnh một lần, nó sẽ tự động kết nối tới Redpanda, lấy dữ liệu ra từ các topic, parse JSON và nhét vào bảng tương ứng — **liên tục, tự động, không cần chạy lại**.

**Tại sao Routine Load kết nối được Redpanda?**
Vì StarRocks và Redpanda đang ở 2 Docker network khác nhau, chúng sẽ nói chuyện với nhau qua **địa chỉ IP máy host** (trong môi trường của bạn là `host.docker.internal:19092` - port external của Redpanda).

---

### Cú pháp Routine Load (để bạn hiểu cấu trúc)

```sql
CREATE ROUTINE LOAD tên_job ON tên_bảng
COLUMNS TERMINATED BY ",",          -- phân cách dữ liệu (JSON thì không cần dòng này)
PROPERTIES (
    "format" = "json",              -- kiểu dữ liệu từ Kafka là JSON
    "jsonpaths" = "[...]"           -- map cột JSON vào cột bảng
)
FROM KAFKA (
    "kafka_broker_list" = "host:port",  -- địa chỉ Redpanda
    "kafka_topic" = "tên_topic",        -- topic cần đọc
    "kafka_partitions" = "0",           -- partition (mặc định 1 partition = "0")
    "kafka_offsets" = "OFFSET_BEGINNING" -- đọc từ đầu hay đọc tiếp từ vị trí hiện tại
);
```

---

### Script Routine Load thực tế cho dự án của bạn

Bạn vào StarRocks bằng lệnh:
```bash
docker exec -it starrocks-fe mysql -h 127.0.0.1 -P 9030 -u root
```

Rồi chạy lần lượt từng lệnh sau:

```sql
USE ecommerce_olap;

-- 1. Hút dữ liệu topic ecommerce_db.df_customers vào bảng df_customers
CREATE ROUTINE LOAD ecommerce_olap.load_customers ON df_customers
PROPERTIES (
    "format" = "json",
    "jsonpaths" = "[\"$.customer_id\", \"$.customer_zip_code_prefix\", \"$.customer_city\", \"$.customer_state\"]"
)
FROM KAFKA (
    "kafka_broker_list" = "host.docker.internal:19092",
    "kafka_topic" = "ecommerce_db.df_customers",
    "kafka_partitions" = "0",
    "kafka_offsets" = "OFFSET_BEGINNING"
);

-- 2. Hút dữ liệu topic ecommerce_db.df_products vào bảng df_products
CREATE ROUTINE LOAD ecommerce_olap.load_products ON df_products
PROPERTIES (
    "format" = "json",
    "jsonpaths" = "[\"$.product_id\", \"$.product_category_name\", \"$.product_weight_g\", \"$.product_length_cm\", \"$.product_height_cm\", \"$.product_width_cm\"]"
)
FROM KAFKA (
    "kafka_broker_list" = "host.docker.internal:19092",
    "kafka_topic" = "ecommerce_db.df_products",
    "kafka_partitions" = "0",
    "kafka_offsets" = "OFFSET_BEGINNING"
);

-- 3. Hút dữ liệu topic ecommerce_db.df_orders vào bảng df_orders
CREATE ROUTINE LOAD ecommerce_olap.load_orders ON df_orders
PROPERTIES (
    "format" = "json",
    "jsonpaths" = "[\"$.order_id\", \"$.customer_id\", \"$.order_purchase_timestamp\", \"$.order_approved_at\"]"
)
FROM KAFKA (
    "kafka_broker_list" = "host.docker.internal:19092",
    "kafka_topic" = "ecommerce_db.df_orders",
    "kafka_partitions" = "0",
    "kafka_offsets" = "OFFSET_BEGINNING"
);

-- 4. Hút dữ liệu topic ecommerce_db.df_payments vào bảng df_payments
CREATE ROUTINE LOAD ecommerce_olap.load_payments ON df_payments
PROPERTIES (
    "format" = "json",
    "jsonpaths" = "[\"$.order_id\", \"$.payment_sequential\", \"$.payment_type\", \"$.payment_installments\", \"$.payment_value\"]"
)
FROM KAFKA (
    "kafka_broker_list" = "host.docker.internal:19092",
    "kafka_topic" = "ecommerce_db.df_payments",
    "kafka_partitions" = "0",
    "kafka_offsets" = "OFFSET_BEGINNING"
);

-- 5. Hút dữ liệu topic ecommerce_db.df_orderitems vào bảng df_orderitems
CREATE ROUTINE LOAD ecommerce_olap.load_orderitems ON df_orderitems
PROPERTIES (
    "format" = "json",
    "jsonpaths" = "[\"$.order_id\", \"$.product_id\", \"$.seller_id\", \"$.price\", \"$.shipping_charges\"]"
)
FROM KAFKA (
    "kafka_broker_list" = "host.docker.internal:19092",
    "kafka_topic" = "ecommerce_db.df_orderitems",
    "kafka_partitions" = "0",
    "kafka_offsets" = "OFFSET_BEGINNING"
);
```

---

### Cách kiểm tra sau khi tạo

```sql
-- Xem tất cả Routine Load đang chạy, trạng thái phải là RUNNING
SHOW ROUTINE LOAD FROM ecommerce_olap\G

-- Vài giây sau, kiểm tra dữ liệu đã vào bảng chưa
SELECT COUNT(*) FROM ecommerce_olap.df_customers;
SELECT COUNT(*) FROM ecommerce_olap.df_orders;
```

**Trạng thái `State` phải là `RUNNING`** là đang hoạt động tốt. Nếu thấy `PAUSED` thì có lỗi gì đó, bạn có thể chạy lệnh trên kèm `\G` để xem lý do ở trường `ReasonOfStateChanged`.



--- các bước để import dữ liệu lên supperset
bước 1: tạo file conf
bước 2 chạy lênh docker exec seatunnel-master /opt/seatunnel/bin/seatunnel.sh --config /opt/seatunnel/jobs/jobs data1/mysql-to-redpanda-customers.conf cho từng bảng
bước 3: tạo rountine load để hút dữ liệu từ redpanda vào starrocks

CREATE ROUTINE LOAD ecommerce_olap.load_customers ON df_customers
PROPERTIES (
    "format" = "json",
    "jsonpaths" = "[\"$.customer_id\", \"$.customer_zip_code_prefix\", \"$.customer_city\", \"$.customer_state\"]"
)
FROM KAFKA (
    "kafka_broker_list" = "redpanda-0:9092,redpanda-1:9092,redpanda-2:9092",
    "kafka_topic" = "ecommerce_db.df_customers",
    "kafka_partitions" = "0",
    "kafka_offsets" = "OFFSET_BEGINNING"
);


mysql+pymysql://root:@host.docker.internal:9030/taxi_db
