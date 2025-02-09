# Frontend Dockerfile
FROM nginx:alpine
WORKDIR /usr/share/nginx/html
COPY . .
COPY default.conf /etc/nginx/conf.d/default.conf 
CMD ["nginx", "-g", "daemon off;"]