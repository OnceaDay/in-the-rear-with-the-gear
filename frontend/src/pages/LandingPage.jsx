import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useEffect, useState } from "react";
import API from "../api/client";

const quickLinks = [
  { title: "Trending Setups", text: "See what spaces are getting attention right now." },
  { title: "Living Room", text: "Comfort-first pieces with cleaner organization." },
  { title: "Office Essentials", text: "Desks, chairs, and gear that support focus." },
  { title: "Bundle Deals", text: "Whole-room combinations built to work together." },
];

const missionCards = [
  {
    title: "Living Room Command",
    text: "Clean, comfortable furniture and storage that helps your space feel organized instead of crowded.",
    cta: "Shop Living Room",
  },
  {
    title: "Workstation Ready",
    text: "Desks, chairs, shelves, and setup gear built for focus, productivity, and everyday function.",
    cta: "Build Your Office",
  },
  {
    title: "Bedroom Logistics",
    text: "Beds, dressers, and smart storage that make the room flow better and work harder for you.",
    cta: "Shop Bedroom",
  },
];

const featurePoints = [
  "Browse the store without signing in",
  "Sign in only when you're ready to order",
  "Furniture, storage, and setup gear with purpose",
  "Clean shopping flow built for real people",
];

const bundleCards = [
  {
    title: "Starter Bedroom Setup",
    text: "Bed frame, side table, dresser, and storage pieces that work together from day one.",
  },
  {
    title: "Office Utility Bundle",
    text: "Desk, ergonomic chair, lighting, and support gear for a smarter work zone.",
  },
  {
    title: "Small Space System",
    text: "Functional pieces selected to help apartments and tight layouts feel bigger and cleaner.",
  },
];

const FEATURED_CATEGORY_ORDER = ["Office", "Bedroom", "Storage"];
const HERO_LOGO_PATH = "/images/Half_Gear_removebg.png";

function normalizeCategory(product) {
  if (typeof product.category === "string") {
    return product.category;
  }

  if (product.category && typeof product.category === "object") {
    return product.category.name || "Uncategorized";
  }

  return "Uncategorized";
}

function formatPrice(value) {
  if (value === null || value === undefined || value === "") {
    return "Price unavailable";
  }

  const numericValue = Number(value);

  if (Number.isNaN(numericValue)) {
    return String(value);
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(numericValue);
}

export default function LandingPage() {
  const { isAuthenticated } = useAuth();
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [featuredError, setFeaturedError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function fetchFeaturedProducts() {
      try {
        setFeaturedError("");

        let url = "/products/";
        let allProducts = [];

        while (url) {
          const response = await API.get(url);
          const payload = response.data;

          const results = Array.isArray(payload) ? payload : payload.results || [];
          allProducts = [...allProducts, ...results];

          if (!payload.next) {
            url = null;
          } else {
            url = payload.next.replace("http://127.0.0.1:8000/api", "");
          }
        }

        const selected = FEATURED_CATEGORY_ORDER.map((categoryName) =>
          allProducts.find(
            (product) =>
              normalizeCategory(product).toLowerCase() === categoryName.toLowerCase()
          )
        ).filter(Boolean);

        if (isMounted) {
          setFeaturedProducts(selected);
        }
      } catch (error) {
        console.error("Failed to load featured products:", error);

        if (isMounted) {
          setFeaturedError("Unable to load featured products right now.");
        }
      }
    }

    fetchFeaturedProducts();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <main className="landing">
      <section className="landing__hero">
        <div className="landing__overlay" />

        <div className="landing__hero-content">
          <div className="landing__brand-lockup">
            <img
              src={HERO_LOGO_PATH}
              alt="In the Rear With the Gear logo"
              className="landing__brand-logo"
            />
          </div>

          <p className="landing__eyebrow">Furniture • Storage • Setup Gear</p>

          <h1 className="landing__title">In the Rear With the Gear</h1>

          <p className="landing__subtitle">
            The backbone behind every well-built space. Smart furniture,
            practical storage, and setup gear designed to make your home work
            better.
          </p>

          <div className="landing__actions">
            <Link to="/products" className="btn btn--primary">
              Shop the Store
            </Link>

            {!isAuthenticated ? (
              <Link to="/login" className="btn btn--secondary">
                Sign In to Order
              </Link>
            ) : (
              <Link to="/orders" className="btn btn--secondary">
                View Orders
              </Link>
            )}
          </div>
        </div>
      </section>

      <section className="landing__quick-grid">
        {quickLinks.map((item) => (
          <Link to="/products" key={item.title} className="quick-card">
            <span className="quick-card__title">{item.title}</span>
            <span className="quick-card__text">{item.text}</span>
          </Link>
        ))}
      </section>

      <section className="landing__featured">
        <div className="section-heading">
          <p className="section-label">Start exploring</p>
          <h2 className="section-title">Featured gear for real spaces</h2>
          <p className="section-text">
            A quick preview of the kinds of products that keep rooms functional,
            organized, and ready for everyday use.
          </p>
        </div>

        {featuredError && <p className="landing__featured-error">{featuredError}</p>}

        <div className="landing__featured-grid">
          {featuredProducts.map((product) => {
            const category = normalizeCategory(product);
            const imageSrc = product.primary_image || "";
            const altText = product.image_alt_text || `${product.name} product image`;

            return (
              <article key={product.id} className="featured-card">
                <div className="featured-card__media">
                  {imageSrc ? (
                    <img
                      src={imageSrc}
                      alt={altText}
                      className="featured-card__image"
                    />
                  ) : (
                    <div className="featured-card__image-placeholder">No Image</div>
                  )}
                </div>

                <p className="featured-card__category">{category}</p>
                <h3 className="featured-card__title">{product.name}</h3>
                <p className="featured-card__price">{formatPrice(product.price)}</p>
                <Link to="/products" className="landing__text-link">
                  View Product
                </Link>
              </article>
            );
          })}
        </div>
      </section>

      <section className="landing__intro">
        <div className="landing__intro-copy">
          <p className="section-label">Built with purpose</p>
          <h2 className="section-title">Every setup has a mission</h2>
          <p className="section-text">
            “In the Rear With the Gear” is about what makes everything work.
            Behind every clean room, productive office, and organized space is a
            system. This store is built for people who want furniture that does
            more than sit there and look pretty.
          </p>
        </div>

        <div className="landing__info-card">
          <span className="landing__card-label">Why shop here</span>
          <h3 className="landing__card-title">Built for practical living</h3>
          <p className="landing__card-text">
            No nonsense. No clutter. Just useful furniture and gear that helps
            your rooms function better.
          </p>

          <ul className="landing__list">
            {featurePoints.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="landing__missions">
        <div className="section-heading">
          <p className="section-label">Shop by mission</p>
          <h2 className="section-title">Gear up your space</h2>
        </div>

        <div className="landing__mission-grid">
          {missionCards.map((card) => (
            <article key={card.title} className="landing__mission-card">
              <h3 className="landing__mission-title">{card.title}</h3>
              <p className="landing__mission-text">{card.text}</p>
              <Link to="/products" className="landing__text-link">
                {card.cta}
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section className="landing__bundles">
        <div className="section-heading">
          <p className="section-label">Bundle-first shopping</p>
          <h2 className="section-title">
            Complete the mission, not just the piece
          </h2>
          <p className="section-text">
            Build whole-room solutions instead of piecing everything together the
            hard way.
          </p>
        </div>

        <div className="landing__bundle-grid">
          {bundleCards.map((bundle) => (
            <article key={bundle.title} className="landing__bundle-card">
              <h3 className="landing__bundle-title">{bundle.title}</h3>
              <p className="landing__bundle-text">{bundle.text}</p>
              <Link to="/products" className="landing__text-link">
                Explore Bundle
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section className="landing__cta-strip">
        <div className="landing__cta-copy">
          <p className="section-label">Ready when you are</p>
          <h2 className="section-title">Build your space like a system</h2>
          <p className="section-text">
            Browse products now, then sign in when you’re ready to place an
            order and manage your purchases.
          </p>
        </div>

        <div className="landing__actions landing__actions--footer">
          <Link to="/products" className="btn btn--primary">
            Browse Products
          </Link>

          {!isAuthenticated ? (
            <Link to="/login" className="btn btn--secondary">
              Sign In
            </Link>
          ) : (
            <Link to="/orders" className="btn btn--secondary">
              Go to Orders
            </Link>
          )}
        </div>
      </section>
    </main>
  );
}