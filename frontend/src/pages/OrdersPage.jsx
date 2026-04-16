export default function OrdersPage() {
  const orders = []; // placeholder

  if (orders.length === 0) {
    return (
      <div className="orders-empty">
        <h2>No orders yet</h2>
        <p>Once you place an order, it will appear here.</p>
      </div>
    );
  }

  return (
    <section className="orders">
      <h1>Your Orders</h1>

      <div className="orders__list">
        {/* map orders here */}
      </div>
    </section>
  );
}