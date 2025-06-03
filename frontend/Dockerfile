# Use an official Nginx runtime as a parent image
FROM nginx:alpine

# Set working directory (though Nginx serves from /usr/share/nginx/html by default)
# WORKDIR /app 

# Copy the main HTML file
COPY ./index.html /usr/share/nginx/html/index.html

# Copy static assets from the ./static subfolder in the build context (frontend/static)
COPY ./static /usr/share/nginx/html/static/

# (Optional) Copy a custom Nginx configuration if needed
# For example, to inject environment variables into JS/HTML or set caching headers.
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 (Nginx default HTTP port)
EXPOSE 80

# Command to run Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"] 