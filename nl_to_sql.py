from transformers import pipeline
import torch
import re

class NLToSQL:

    def __init__(self):
        device = 0 if torch.cuda.is_available() else -1

        self.generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-small",
            device=device
        )

        self.departments = ['IT', 'HR', 'Sales', 'Engineering', 'Marketing']

    # -----------------------------
    # INTENT DETECTION
    # -----------------------------
    def detect_intent(self, query):
        q = query.lower().strip()

        if q.startswith(("add", "insert")):
            return "INSERT"
        elif q.startswith(("update", "modify", "change")):
            return "UPDATE"
        elif q.startswith(("delete", "remove")):
            return "DELETE"
        elif "show" in q or "list" in q:
            return "SELECT"
        else:
            return "UNKNOWN"

    # -----------------------------
    # ENTITY EXTRACTION (ROBUST)
    # -----------------------------
    def extract_entities(self, query):
        entities = {}
        q = query.lower()

        # -----------------------------
        # Salary extraction
        # -----------------------------
        salary_match = re.search(r'\b(\d{3,6})\b', q)
        if salary_match:
            entities["salary"] = salary_match.group(1)

        # Salary operator
        if any(word in q for word in ["below", "less than", "<"]):
            entities["salary_operator"] = "<"
        elif any(word in q for word in ["above", "greater than", ">"]):
            entities["salary_operator"] = ">"
        elif "salary" in q:
            entities["salary_operator"] = "="

        # -----------------------------
        # Department extraction
        # -----------------------------
        for d in self.departments:
            if d.lower() in q:
                entities["department"] = d
                break

        # -----------------------------
        # City extraction
        # -----------------------------
        city_match = re.search(r'city\s+([a-zA-Z]+)', q)
        if city_match:
            entities["city"] = city_match.group(1).capitalize()

        # -----------------------------
        # Name extraction (order independent)
        # -----------------------------
        cleaned = re.sub(
            r'(update|add|insert|delete|remove|change|salary|of|to|with|in|employee|city|above|below|greater|less|than|\d+)',
            '',
            q
        )

        words = cleaned.split()

        for word in words:
            if word.isalpha():
                entities["name"] = word.capitalize()
                break

        return entities

    # -----------------------------
    # SQL BUILDER
    # -----------------------------
    def build_sql(self, intent, entities):

        # -----------------------------
        # SELECT
        # -----------------------------
        if intent == "SELECT":
            sql = "SELECT * FROM employees"
            conditions = []

            if "department" in entities:
                conditions.append(f"department = '{entities['department']}'")

            if "salary" in entities:
                operator = entities.get("salary_operator", "=")
                conditions.append(f"salary {operator} {entities['salary']}")

            if conditions:
                sql += " WHERE " + " AND ".join(conditions)

            return sql + ";"

        # -----------------------------
        # INSERT
        # -----------------------------
        elif intent == "INSERT":
            if all(k in entities for k in ["name", "department", "salary"]):
                city = entities.get("city", "Unknown")
                return (
                    "INSERT INTO employees (name, department, salary, city) "
                    f"VALUES ('{entities['name']}', '{entities['department']}', "
                    f"{entities['salary']}, '{city}');"
                )

        # -----------------------------
        # UPDATE
        # -----------------------------
        elif intent == "UPDATE":
            if "name" in entities and "salary" in entities:
                return (
                    "UPDATE employees "
                    f"SET salary = {entities['salary']} "
                    f"WHERE name = '{entities['name']}';"
                )

        # -----------------------------
        # DELETE
        # -----------------------------
        elif intent == "DELETE":
            if "name" in entities:
                return (
                    "DELETE FROM employees "
                    f"WHERE name = '{entities['name']}';"
                )

        return None

    # -----------------------------
    # MAIN ENTRY
    # -----------------------------
    def generate_sql(self, nl_query):

        intent = self.detect_intent(nl_query)
        entities = self.extract_entities(nl_query)

        sql = self.build_sql(intent, entities)

        if sql:
            return sql

        # -----------------------------
        # FALLBACK TO MODEL (STRICT)
        # -----------------------------
        prompt = f"""
Convert this English query to valid MySQL.
Only table available:
employees(id, name, department, salary, city)

Rules:
- Always use FROM employees
- Output only SQL
- Allowed commands: SELECT, INSERT, UPDATE, DELETE

Query: {nl_query}
SQL:
"""

        output = self.generator(
            prompt,
            max_length=96,
            do_sample=False,
            temperature=0.0
        )

        sql_query = output[0]['generated_text'].strip()

        # -----------------------------
        # STRICT VALIDATION
        # -----------------------------
        if not re.match(r"^(SELECT|INSERT|UPDATE|DELETE)\s", sql_query, re.IGNORECASE):
            raise ValueError("Invalid SQL generated.")

        if sql_query.lower().startswith("select") and "from employees" not in sql_query.lower():
            raise ValueError("Invalid table reference.")

        if not sql_query.endswith(";"):
            sql_query += ";"

        return sql_query