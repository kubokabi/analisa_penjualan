from flask import Flask, render_template, request

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/')
def index():
    result = None
    error = None
    return render_template('index.html', result=result, error=error)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        num1 = float(request.form.get('num1', 0))
        num2 = float(request.form.get('num2', 0))
        operation = request.form.get('operation')
        
        if operation == 'add':
            result = num1 + num2
            op_symbol = '+'
        elif operation == 'subtract':
            result = num1 - num2
            op_symbol = '-'
        elif operation == 'multiply':
            result = num1 * num2
            op_symbol = '×'
        elif operation == 'divide':
            if num2 == 0:
                return render_template('index.html', result=None, error="Error: Pembagian dengan nol tidak diperbolehkan!")
            result = num1 / num2
            op_symbol = '÷'
        else:
            return render_template('index.html', result=None, error="Error: Operasi tidak valid!")
        
        return render_template('index.html', 
                             result=f"{num1} {op_symbol} {num2} = {result}", 
                             error=None)
    except ValueError:
        return render_template('index.html', result=None, error="Error: Masukkan angka yang valid!")
    except Exception as e:
        return render_template('index.html', result=None, error=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
