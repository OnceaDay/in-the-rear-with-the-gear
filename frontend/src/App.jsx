import { Routes, Route, Link, NavLink } from "react-router-dom";
import { MapPin, Search, ShoppingCart } from "lucide-react";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import ProductsPage from "./pages/ProductsPage";
import CartPage from "./pages/CartPage";
import OrdersPage from "./pages/OrdersPage";
import ProtectedRoute from "./routes/ProtectedRoute";
import { useAuth } from "./context/AuthContext";

function Layout({ children }) {
  const { isAuthenticated, logout } = useAuth();

  const cartCount = 0;
  const deliveryName = "Forreal";
  const deliveryZip = "New York 10030";

  const handleSearchSubmit = (event) => {
    event.preventDefault();
  };

  const getNavLinkClass = ({ isActive }) =>
    isActive ? "site-nav__link site-nav__link--active" : "site-nav__link";

  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="site-header__bar">
          <p className="site-header__message">
            Furniture, storage, and setup gear built for real living.
          </p>

          <div className="site-header__utility">
            {!isAuthenticated ? (
              <NavLink to="/login" className="site-header__utility-link">
                Sign In
              </NavLink>
            ) : (
              <button className="site-header__logout" onClick={logout}>
                Logout
              </button>
            )}
          </div>
        </div>

        <nav className="site-nav site-nav--enhanced">
          <div className="site-nav__left">
            
            {/* ✅ LOGO REPLACEMENT */}
            <Link to="/" className="site-nav__brand">
              <img
                src="/images/logo.png"
                alt="In the Rear With the Gear logo"
                className="site-nav__logo"
              />
            </Link>

            <div className="site-nav__delivery">
              <span className="site-nav__delivery-icon" aria-hidden="true">
                <MapPin size={16} />
              </span>

              <div className="site-nav__delivery-text">
                <span className="site-nav__delivery-label">
                  Deliver to {deliveryName}
                </span>
                <span className="site-nav__delivery-value">{deliveryZip}</span>
              </div>
            </div>
          </div>

          <form className="site-search" onSubmit={handleSearchSubmit}>
            <input
              type="text"
              className="site-search__input"
              placeholder="Search furniture, storage, and setup gear"
              aria-label="Search products"
            />
            <button
              type="submit"
              className="site-search__button"
              aria-label="Search"
            >
              <Search size={18} />
            </button>
          </form>

          <div className="site-nav__right">
            <div className="site-nav__links">
              <NavLink to="/" className={getNavLinkClass}>
                Home
              </NavLink>

              <NavLink to="/products" className={getNavLinkClass}>
                Products
              </NavLink>

              {isAuthenticated && (
                <>
                  <NavLink to="/cart" className={getNavLinkClass}>
                    Cart
                  </NavLink>

                  <NavLink to="/orders" className={getNavLinkClass}>
                    Orders
                  </NavLink>
                </>
              )}
            </div>

            {!isAuthenticated ? (
              <NavLink
                to="/login"
                className="site-nav__account site-nav__account--guest"
              >
                <span className="site-nav__account-greeting">Welcome</span>
                <span className="site-nav__account-name">
                  Sign in to shop
                </span>
              </NavLink>
            ) : (
              <div className="site-nav__account">
                <span className="site-nav__account-greeting">
                  Hello, Forreal
                </span>
                <span className="site-nav__account-name">Account</span>
              </div>
            )}

            <Link to="/products" className="site-nav__shop-button">
              Shop Now
            </Link>

            {isAuthenticated && (
              <NavLink to="/cart" className="site-nav__cart-pill">
                <span className="site-nav__cart-icon" aria-hidden="true">
                  <ShoppingCart size={20} />
                </span>
                <span className="site-nav__cart-label">Cart</span>
                <span className="site-nav__cart-count">{cartCount}</span>
              </NavLink>
            )}
          </div>
        </nav>
      </header>

      <main>{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route
          path="/cart"
          element={
            <ProtectedRoute>
              <CartPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/orders"
          element={
            <ProtectedRoute>
              <OrdersPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Layout>
  );
}