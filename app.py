from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

customers = {}
bills = {}
deliveries = {}
empty_bottles = {}

page = """
<!doctype html>
<html>
<head>
<title>Mineral Water Delivery Service</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 700px; margin: auto; padding: 20px; }
  h2 { color: #2F4F4F; }
  form { margin-bottom: 20px; padding: 15px; border: 1px solid #ccc; border-radius: 8px; }
  label { display: block; margin: 8px 0 4px; }
  input, select { padding: 8px; width: 100%; box-sizing: border-box; }
  button { margin-top: 10px; padding: 10px 15px; background-color: #28a745; color: white; border: none; cursor: pointer; border-radius: 5px; }
  button:hover { background-color: #218838; }
  #report { background-color: #f8f9fa; padding: 15px; margin-top: 20px; border-radius: 8px; }
  pre { white-space: pre-wrap; word-wrap: break-word; }
</style>
</head>
<body>

<h2>Mineral Water Delivery Service App</h2>

<h3>Add Customer</h3>
<form id="customerForm">
  <label>Customer ID:</label><input type="text" name="id" required>
  <label>Name:</label><input type="text" name="name" required>
  <label>Monthly Bottles:</label><input type="number" name="monthly_bottles" required min="0">
  <button type="submit">Add Customer</button>
</form>

<h3>Add Delivery</h3>
<form id="deliveryForm">
  <label>Customer ID:</label><input type="text" name="customer_id" required>
  <label>Date (YYYY-MM-DD):</label><input type="date" name="date" required>
  <button type="submit">Add Delivery</button>
</form>

<h3>Add Payment</h3>
<form id="paymentForm">
  <label>Customer ID:</label><input type="text" name="customer_id" required>
  <label>Amount:</label><input type="number" step="0.01" name="amount" required>
  <button type="submit">Add Payment</button>
</form>

<h3>Update Empty Bottles</h3>
<form id="emptyBottlesForm">
  <label>Customer ID:</label><input type="text" name="customer_id" required>
  <label>Count:</label><input type="number" name="count" required min="0">
  <button type="submit">Update Empty Bottles</button>
</form>

<h3>Get Customer Report</h3>
<form id="reportForm">
  <label>Customer ID:</label><input type="text" name="customer_id" required>
  <button type="submit">Get Report</button>
</form>
<div id="report"></div>

<script>
async function postData(url = '', data = {}) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
}

document.getElementById('customerForm').onsubmit = async function(e) {
  e.preventDefault();
  const form = e.target;
  const data = {
    id: form.id.value.trim(),
    name: form.name.value.trim(),
    monthly_bottles: parseInt(form.monthly_bottles.value)
  };
  const res = await postData('/customer', data);
  alert(res.message || res.error);
  form.reset();
};

document.getElementById('deliveryForm').onsubmit = async function(e) {
  e.preventDefault();
  const form = e.target;
  const data = {
    customer_id: form.customer_id.value.trim(),
    date: form.date.value
  };
  const res = await postData('/delivery', data);
  alert(res.message || res.error);
  form.reset();
};

document.getElementById('paymentForm').onsubmit = async function(e) {
  e.preventDefault();
  const form = e.target;
  const data = {
    customer_id: form.customer_id.value.trim(),
    amount: parseFloat(form.amount.value)
  };
  const res = await postData('/payment', data);
  alert(res.message || res.error);
  form.reset();
};

document.getElementById('emptyBottlesForm').onsubmit = async function(e) {
  e.preventDefault();
  const form = e.target;
  const data = {
    customer_id: form.customer_id.value.trim(),
    count: parseInt(form.count.value)
  };
  const res = await postData('/empty_bottles', data);
  alert(res.message || res.error);
  form.reset();
};

document.getElementById('reportForm').onsubmit = async function(e) {
  e.preventDefault();
  const cust_id = e.target.customer_id.value.trim();
  if(!cust_id) {
    alert('Customer ID required');
    return;
  }
  const response = await fetch(`/report/${cust_id}`);
  const res = await response.json();
  if(res.error) {
    document.getElementById('report').innerHTML = '<b style="color:red;">' + res.error + '</b>';
  } else {
    document.getElementById('report').innerHTML = '<pre>' + JSON.stringify(res, null, 2) + '</pre>';
  }
};
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(page)

@app.route('/customer', methods=['POST'])
def add_customer():
    data = request.json
    cust_id = data.get('id')
    if not cust_id or cust_id in customers:
        return jsonify({'error': 'Invalid or existing customer ID'}), 400
    customers[cust_id] = {
        'name': data.get('name', ''),
        'monthly_bottles': data.get('monthly_bottles', 0),
        'payments': 0.0
    }
    bills[cust_id] = 0.0
    deliveries[cust_id] = []
    empty_bottles[cust_id] = 0
    return jsonify({'message': 'Customer added successfully'})

@app.route('/delivery', methods=['POST'])
def add_delivery():
    data = request.json
    cust_id = data.get('customer_id')
    date = data.get('date')
    if cust_id not in customers or not date:
        return jsonify({'error': 'Missing or invalid data'}), 400
    deliveries[cust_id].append(date)
    bills[cust_id] += customers[cust_id]['monthly_bottles'] * 50
    return jsonify({'message': 'Delivery added'})

@app.route('/payment', methods=['POST'])
def add_payment():
    data = request.json
    cust_id = data.get('customer_id')
    amount = data.get('amount')
    if cust_id not in customers or amount is None:
        return jsonify({'error': 'Missing or invalid data'}), 400
    customers[cust_id]['payments'] += amount
    return jsonify({'message': 'Payment recorded'})

@app.route('/empty_bottles', methods=['POST'])
def update_empty_bottles():
    data = request.json
    cust_id = data.get('customer_id')
    count = data.get('count')
    if cust_id not in customers or count is None:
        return jsonify({'error': 'Missing or invalid data'}), 400
    empty_bottles[cust_id] = count
    return jsonify({'message': 'Empty bottles updated'})

@app.route('/report/<customer_id>')
def customer_report(customer_id):
    if customer_id not in customers:
        return jsonify({'error': 'Customer not found'}), 404
    c = customers[customer_id]
    report = {
        'name': c['name'],
        'monthly_bottles': c['monthly_bottles'],
        'payments': c['payments'],
        'bills': bills.get(customer_id, 0),
        'deliveries': deliveries.get(customer_id, []),
        'empty_bottles': empty_bottles.get(customer_id, 0)
    }
    return jsonify(report)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
