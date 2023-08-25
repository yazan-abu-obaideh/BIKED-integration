FROM nginx

COPY gateway/nginx.conf /etc/nginx/nginx.conf
COPY gateway/secrets/ /secrets/
