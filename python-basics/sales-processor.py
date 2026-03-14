import json
import csv

INPUT_FILE = "sales.json"
OUTPUT_FILE = "sales_output.csv"
SHIPPING_PER_ITEM = 5

rows = []
customer_totals = {}

# Read JSON file
with open(INPUT_FILE, "r") as f:
    data = json.load(f)

orders = data.get("orders", [])

for order in orders:

    order_id = order.get("order_id", "Unknown")
    customer = order.get("customer", {})
    customer_name = customer.get("name", "Unknown")

    shipping_address = order.get("shipping_address", "Unknown")
    country_code = "US"

    items = order.get("items", [])

    for item in items:

        product_name = item.get("name", "Unknown")
        price = float(item.get("price", 0))
        quantity = int(item.get("quantity", 0))

        total_value = price * quantity

        discount = total_value * 0.10 if total_value > 100 else 0

        shipping_cost = quantity * SHIPPING_PER_ITEM

        final_total = total_value - discount + shipping_cost

        row = {
            "Order ID": order_id,
            "Customer Name": customer_name,
            "Product Name": product_name,
            "Product Price": round(price,2),
            "Quantity Purchased": quantity,
            "Total Value": round(total_value,2),
            "Discount": round(discount,2),
            "Shipping Cost": shipping_cost,
            "Final Total": round(final_total,2),
            "Shipping Address": shipping_address,
            "Country Code": country_code
        }

        rows.append(row)

        customer_totals[customer_name] = customer_totals.get(customer_name,0) + final_total


# Sort rows by total spending per customer
rows.sort(key=lambda r: customer_totals[r["Customer Name"]], reverse=True)


# Save CSV
with open(OUTPUT_FILE, "w", newline="") as f:

    headers = list(rows[0].keys())
    writer = csv.DictWriter(f, fieldnames=headers)

    writer.writeheader()
    writer.writerows(rows)


# Function to print table
def print_table(data):

    headers = list(data[0].keys())

    col_widths = [max(len(str(row[h])) for row in data + [{h:h}]) for h in headers]

    # Print header
    for i,h in enumerate(headers):
        print(f"{h:<{col_widths[i]}}", end=" | ")
    print()

    print("-" * (sum(col_widths) + len(headers)*3))

    # Print rows
    for row in data:
        for i,h in enumerate(headers):
            print(f"{str(row[h]):<{col_widths[i]}}", end=" | ")
        print()


# Show output table
print("\nProcessed Order Data\n")
print_table(rows)

print("\nCSV file generated:", OUTPUT_FILE)