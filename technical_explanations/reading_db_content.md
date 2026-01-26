Got it! Since you’re using **PostgreSQL inside Docker**, there are a few ways to **view the data in your database**. I’ll break it down step by step, from simplest to more advanced.

---

## 1️⃣ Check which Docker container is running PostgreSQL

Run:

```bash
docker ps
```

You’ll see something like:

```
CONTAINER ID   IMAGE         NAME             PORTS
a1b2c3d4e5f6   postgres:16   my-postgres      5432/tcp
```

Take note of the **container name** (`my-postgres`) or **ID** (`a1b2c3d4e5f6`).

---

## 2️⃣ Access PostgreSQL inside the container

You can **open a psql shell** inside the container:

```bash
docker exec -it my-postgres psql -U postgres
```

* `-U postgres` → username (replace if you used a different one)
* This gives you the **PostgreSQL prompt**:

```
postgres=#
```

---

## 3️⃣ List databases

```sql
\l
```

You’ll see something like:

```
Name      | Owner    | Encoding
----------+----------+---------
postgres  | postgres | UTF8
mydb      | postgres | UTF8
```

Pick your database (probably the one your FastAPI app is using).

---

## 4️⃣ Connect to your database

```sql
\c mydb
```

Now you’re inside your app database.

---

## 5️⃣ List tables

```sql
\dt
```

Example output:

```
       List of relations
 Schema |      Name       | Type  |  Owner
--------+----------------+-------+---------
 public | meeting        | table | postgres
 public | knowledge_chunk| table | postgres
```

---

## 6️⃣ View rows in a table

```sql
SELECT * FROM meeting LIMIT 5;
SELECT * FROM knowledge_chunk LIMIT 5;
```

* Shows the **first 5 rows** of each table.
* If you want a more **readable view**, you can do:

```sql
SELECT id, content, category, metadata_json FROM knowledge_chunk LIMIT 5;
```

---

## 7️⃣ Exit psql

```sql
\q
```

---

## 8️⃣ Optional: Connect from your host machine

If you prefer **PGAdmin** or **DBeaver**, you can connect to your Docker PostgreSQL by using:

* **Host:** `localhost`
* **Port:** `5432` (or the mapped port in Docker)
* **Username:** `postgres`
* **Password:** whatever you set in your container
* **Database:** `mydb`

This way, you can **browse tables visually** without SQL commands.

---

💡 **Tip:** If you want to see **embeddings** (arrays of floats), don’t try to `SELECT *` in the console—it will be messy. Instead, select only `content`, `category`, and `metadata_json`.

---

If you want, I can give you a **one-liner to see the last 3 knowledge chunks stored** directly from Docker without opening psql every time. This is handy when testing your FastAPI endpoint.

Do you want me to do that?
