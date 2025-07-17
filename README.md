# Data-Scrape-to-RAG
 Mini end-to-end “Data-Scrape-to-RAG” lakehouse.

docker-compose up

http://localhost:8081/

# create airflow web server user
docker exec -it airflow-webserver bash
Example:
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin


docker exec -it airflow-webserver airflow connections add 'ssh_notebook' \
    --conn-type 'ssh' \
    --conn-host 'notebook' \
    --conn-login 'docker' \
    --conn-port '22'


docker exec -it notebook bash
bash /home/docker/notebooks/setup_ssh.sh


create minio bucket: warehouse

docker exec -it notebook bash
/home/docker/notebooks/up_fast_api.sh


http://localhost:10000/ask?question=book&numres=5