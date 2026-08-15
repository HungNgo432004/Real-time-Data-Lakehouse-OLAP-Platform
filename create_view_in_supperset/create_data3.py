import pymysql

def create_views():
    # Kết nối vào StarRocks FE (cổng 9030)
    connection = pymysql.connect(
        host='127.0.0.1', 
        port=9030,
        user='root',
        password='', # Mật khẩu rỗng
        database='movielens_db'
    )

    try:
        with connection.cursor() as cursor:
            print("Creating Massive View vw_movie_massive_join...")
            
            # Cố tình JOIN cả 3 bảng (bao gồm 2 bảng dữ liệu cực lớn là ratings và genome_scores)
            # Điều này sẽ tạo ra hàng trăm triệu dòng (Cartesian product) để stress-test StarRocks!
            sql_view = """
            CREATE OR REPLACE VIEW vw_movie_massive_join AS
            SELECT 
                r.userId,
                r.movieId,
                m.title,
                m.genres,
                r.rating,
                g.tagId,
                g.relevance,
                FROM_UNIXTIME(r.timestamp) AS rating_time
            FROM movielens_db.ratings r
            JOIN movielens_db.genome_scores g ON r.movieId = g.movieId
            LEFT JOIN movielens_db.movies m ON r.movieId = m.movieId;
            """
            cursor.execute(sql_view)
            print("=> Success! Massive View created.")
            
    finally:
        connection.close()
        print("Connection closed.")

if __name__ == "__main__":
    create_views()
