# 1. Create the project
npm create vue@latest frontend
# Select: Yes to Vue Router, Yes to Pinia. No to everything else.

cd frontend
npm install

# 2. Install Styles & API tools
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install axios @heroicons/vue

# 3. Configure Tailwind (Edit tailwind.config.js)
# Replace content: [] with:
# content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],


Got it! Since you want to use **Bun instead of npm**, the commands are slightly different because Bun is a drop-in replacement for package management and script execution. Here’s how to translate your steps to Bun:

---

### **1. Create the Vue project**

Bun doesn’t have `npm create` directly, but you can still use `bun create`:

```bash
bun create vue ./frontend
```

* During setup, select the same options as before: **Yes to Vue Router**, **Yes to Pinia**, **No to everything else**.

Then:

```bash
cd frontend
bun install
```

---

### **2. Install styles & API tools**

Instead of `npm install`, use `bun add`:

```bash
bun add -d tailwindcss@3 postcss autoprefixer
bun add axios @heroicons/vue
```

* `-d` is Bun’s equivalent of `--save-dev`.

Initialize Tailwind:

```bash
bun x tailwindcss init -p
```

> Bun uses `bun x` to run binaries installed via node_modules.

---

### **3. Configure Tailwind**

Edit `tailwind.config.js` exactly like you would for npm:

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

---

### ✅ Notes

* `bun add` replaces `npm install`.
* `bun x <binary>` replaces `npx <binary>` for running CLI tools.
* Everything else (Vue files, Tailwind setup) remains the same.
