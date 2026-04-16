export default function CartPage() {
  const cartItems = []; // placeholder

  if (cartItems.length === 0) {
    return (
      <div className="cart-empty">
        <h2>Your cart is empty</h2>
        <p>Start adding gear to build your setup.</p>
        <a href="/products" className="btn btn--primary">
          Browse Products
        </a>
      </div>
    );
  }

  return (
    <section className="cart">
      <h1>Shopping Cart</h1>

      <div className="cart__layout">
        <div className="cart__items">
          {/* map items here */}
        </div>

        <div className="cart__summary">
          <h3>Summary</h3>
          <p>Subtotal: $0.00</p>
          <button className="btn btn--primary">
            Proceed to Checkout
          </button>
        </div>
      </div>
    </section>
  );
}