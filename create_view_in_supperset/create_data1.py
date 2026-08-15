import pymysql

def create_views():
    # 1. Kết nối vào StarRocks FE (cổng 9030)
    connection = pymysql.connect(
        host='127.0.0.1', 
        port=9030,
        user='root',
        password='123456', 
        database='ecommerce_olap'
    )

    try:
        with connection.cursor() as cursor:
            print("Đang tạo View 1 (Phân tích Sales)...")
            sql_view_1 = """
            CREATE OR REPLACE VIEW vw_sales_analysis AS
            SELECT 
                o.order_id,
                CAST(o.order_purchase_timestamp AS DATETIME) AS purchase_date,
                c.customer_city,
                c.customer_state,
                oi.product_id,
                oi.price,
                oi.shipping_charges,
                p.product_category_name
            FROM df_orders o
            JOIN df_customers c ON o.customer_id = c.customer_id
            JOIN df_orderitems oi ON o.order_id = oi.order_id
            LEFT JOIN df_products p ON oi.product_id = p.product_id;
            """
            cursor.execute(sql_view_1)
            print("=> Thành công!")

            print("Đang tạo View 2 (Phân tích Payments)...")
            sql_view_2 = """
            CREATE OR REPLACE VIEW vw_payment_analysis AS
            SELECT 
                o.order_id,
                CAST(o.order_purchase_timestamp AS DATETIME) AS purchase_date,
                c.customer_city,
                c.customer_state,
                py.payment_type,
                py.payment_installments,
                py.payment_value
            FROM df_orders o
            JOIN df_customers c ON o.customer_id = c.customer_id
            JOIN df_payments py ON o.order_id = py.order_id;
            """
            cursor.execute(sql_view_2)
            print("=> Thành công!")
            
    finally:
        connection.close()
        print("Đã đóng kết nối.")

if __name__ == "__main__":
    create_views()
