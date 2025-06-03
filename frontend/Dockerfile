# Use an official Nginx runtime as a parent image
FROM nginx:alpine

# Set working directory to Nginx public folder
WORKDIR /usr/share/nginx/html

# Remove default Nginx static assets
RUN rm -rf .

# Copy static assets from an assumed 'public' or root of the context (which is ./frontend)
# If your index.html and any other assets (CSS, JS) are directly in ./frontend, this is fine.
# If they are in a subfolder like ./frontend/public or ./frontend/dist, adjust the COPY source path.
COPY ./index.html .
# If you have other static assets like CSS or JS folders, copy them too:
# COPY ./css ./css
# COPY ./js ./js
# COPY ./images ./images

# Expose port 80 (Nginx default HTTP port)
EXPOSE 80

# Command to run Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"] 