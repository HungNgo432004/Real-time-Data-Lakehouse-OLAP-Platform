import pymysql

def create_views():
    # 1. Kết nối vào StarRocks FE (cổng 9030)
    # Lưu ý: Mật khẩu mặc định của StarRocks thường để trống (''), nhưng nếu bạn đã đổi thành '123456' thì giữ nguyên.
    connection = pymysql.connect(
        host='127.0.0.1', 
        port=9030,
        user='root',
        password='', # Sửa lại thành '123456' nếu StarRocks của bạn có mật khẩu
        database='taxi_db'
    )

    try:
        with connection.cursor() as cursor:
            print("Creating View vw_taxi_trips_analysis...")
            sql_view_1 = """
            CREATE OR REPLACE VIEW vw_taxi_trips_analysis AS
            SELECT 
                t.VendorID,
                t.tpep_pickup_datetime AS pickup_time,
                t.tpep_dropoff_datetime AS dropoff_time,
                t.passenger_count,
                t.trip_distance,
                t.payment_type,
                t.fare_amount,
                t.tip_amount,
                t.tolls_amount,
                t.total_amount,
                -- Thông tin Khu vực ĐÓN khách (Pickup)
                pu.zone_nam AS pickup_zone,
                pu.borough AS pickup_borough,
                -- Thông tin Khu vực TRẢ khách (Dropoff)
                do.zone_nam AS dropoff_zone,
                do.borough AS dropoff_borough,
                -- Trích xuất nhanh Giờ và Thứ để dễ vẽ biểu đồ phân tích hành vi
                HOUR(t.tpep_pickup_datetime) AS pickup_hour,
                DAYNAME(t.tpep_pickup_datetime) AS pickup_day_of_week
            FROM taxi_db.taxi_trip_data t
            -- JOIN lần 1: Lấy thông tin điểm ĐÓN
            LEFT JOIN taxi_db.taxi_zone_geo pu ON t.PULocationID = pu.zone_id
            -- JOIN lần 2: Lấy thông tin điểm TRẢ
            LEFT JOIN taxi_db.taxi_zone_geo do ON t.DOLocationID = do.zone_id;
            """
            cursor.execute(sql_view_1)
            print("=> Success! View created.")
            
    finally:
        connection.close()
        print("Connection closed.")

if __name__ == "__main__":
    create_views()
