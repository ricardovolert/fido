FROM nginx:latest
ADD ./nginx.conf /etc/nginx/nginx.conf
ADD ./foo.conf /etc/nginx/sites-enabled/foo.conf
VOLUME ["/www/data"]
CMD ["nginx", "-g", "daemon off;"]
