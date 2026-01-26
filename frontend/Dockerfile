# Use Bun official image
FROM oven/bun:1.3.6 as dev

WORKDIR /app

# Copy package.json & lockfile
COPY package.json bun.lockb* ./

# Install dependencies
RUN bun install

# Copy the rest of the source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Command to run Vite dev server
CMD ["bun", "run", "dev", "--", "--host", "0.0.0.0"]
