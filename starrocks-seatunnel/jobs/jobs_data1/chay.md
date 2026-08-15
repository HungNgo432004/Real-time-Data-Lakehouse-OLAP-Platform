docker exec seatunnel-master /opt/seatunnel/bin/seatunnel.sh --config /opt/seatunnel/jobs/jobs_data1/mysql-to-redpanda-customers.conf
docker exec seatunnel-master /opt/seatunnel/bin/seatunnel.sh --config /opt/seatunnel/jobs/jobs_data1/mysql-to-redpanda-orderitems.conf
docker exec seatunnel-master /opt/seatunnel/bin/seatunnel.sh --config /opt/seatunnel/jobs/jobs_data1/mysql-to-redpanda-orders.conf
docker exec seatunnel-master /opt/seatunnel/bin/seatunnel.sh --config /opt/seatunnel/jobs/jobs_data1/mysql-to-redpanda-products.conf
docker exec seatunnel-master /opt/seatunnel/bin/seatunnel.sh --config /opt/seatunnel/jobs/jobs_data1/mysql-to-redpanda-payments.conf
