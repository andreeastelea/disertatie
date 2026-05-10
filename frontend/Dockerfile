FROM nginx:1.27-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/
COPY static/    /usr/share/nginx/html/static/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
