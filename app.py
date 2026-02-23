from flask import Flask, render_template, request, jsonify
from nl_to_sql import NLToSQL
from db_handler import DBHandler

app = Flask(__name__)

# Initialize modules
nl_converter = NLToSQL()
db_handler = DBHandler()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def process_query():
    try:
        data = request.get_json()
        nl_query = data.get('query')

        if not nl_query:
            return jsonify({'error': 'Please enter a query.'}), 400

        # Step 1: Generate SQL
        generated_sql = nl_converter.generate_sql(nl_query)

        # Step 2: Execute SQL
        results, error = db_handler.execute_query(generated_sql)

        if error:
            return jsonify({
                'sql': generated_sql,
                'error': error
            })

        # Prepare response based on query type
        response = {'sql': generated_sql}
        
        if 'columns' in results and 'data' in results:
            # SELECT query
            response['columns'] = results['columns']
            response['data'] = results['data']
        elif 'message' in results:
            # INSERT/UPDATE/DELETE query
            response['message'] = results['message']

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
