run:
	docker start postgres_db

drop:
	docker exec -itu postgres postgresdb psql -c "drop database delta_union_db"

create:
	docker exec -itu postgres postgresdb psql -c "create database delta_union_db"

refresh:
	make drop
	make create

