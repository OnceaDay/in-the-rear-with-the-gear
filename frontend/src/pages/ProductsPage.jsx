import { useEffect, useMemo, useState } from "react";
import API from "../api/client";

const FILTERS = ["All", "Bedroom", "Office", "Storage", "Living Room", "Bundles"];
const BACKEND_BASE_URL = "http://127.0.0.1:8000";

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

function normalizeCategory(product) {
  if (typeof product.category === "string") {
    return product.category;
  }

  if (product.category && typeof product.category === "object") {
    return product.category.name || "Uncategorized";
  }

  return "Uncategorized";
}

function resolveImageUrl(imagePath) {
  if (!imagePath) {
    return "";
  }

  if (
    imagePath.startsWith("http://") ||
    imagePath.startsWith("https://")
  ) {
    return imagePath;
  }

  if (imagePath.startsWith("/")) {
    return `${BACKEND_BASE_URL}${imagePath}`;
  }

  return `${BACKEND_BASE_URL}/${imagePath}`;
}

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [selectedFilter, setSelectedFilter] = useState("All");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function fetchProducts() {
      try {
        setIsLoading(true);
        setError("");

        const response = await API.get("/products/");
        const results = Array.isArray(response.data)
          ? response.data
          : response.data?.results || [];

        if (isMounted) {
          setProducts(results);
        }
      } catch (err) {
        console.error("Failed to load products:", err);
        if (isMounted) {
          setError("Unable to load products right now.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    fetchProducts();

    return () => {
      isMounted = false;
    };
  }, []);

  const visibleProducts = useMemo(() => {
    if (selectedFilter === "All") {
      return products;
    }

    return products.filter(
      (product) =>
        normalizeCategory(product).toLowerCase() === selectedFilter.toLowerCase()
    );
  }, [products, selectedFilter]);

  return (
    <section className="products-page">
      <div className="products-page__hero">
        <p className="section-label">Storefront</p>
        <h1 className="products-page__title">Shop furniture and setup gear</h1>
        <p className="products-page__text">
          Explore products built to help your rooms function better, look
          cleaner, and stay organized.
        </p>
      </div>

      <div className="products-page__toolbar">
        {FILTERS.map((filter) => (
          <button
            key={filter}
            type="button"
            className={`products-page__filter${
              selectedFilter === filter ? " products-page__filter--active" : ""
            }`}
            onClick={() => setSelectedFilter(filter)}
          >
            {filter}
          </button>
        ))}
      </div>

      {isLoading && (
        <div className="products-page__state">
          <p>Loading products...</p>
        </div>
      )}

      {!isLoading && error && (
        <div className="products-page__state products-page__state--error">
          <p>{error}</p>
        </div>
      )}

      {!isLoading && !error && visibleProducts.length === 0 && (
        <div className="products-page__state">
          <p>No products matched that filter.</p>
        </div>
      )}

      {!isLoading && !error && visibleProducts.length > 0 && (
        <div className="products-page__grid">
          {visibleProducts.map((product) => {
            const category = normalizeCategory(product);
            const imageSrc = resolveImageUrl(product.primary_image);
            const altText =
              product.image_alt_text || `${product.name} product image`;

            return (
              <article key={product.id} className="product-card">
                <div className="product-card__media">
                  {imageSrc ? (
                    <img
                      src={imageSrc}
                      alt={altText}
                      className="product-card__image"
                    />
                  ) : (
                    <div className="product-card__image-placeholder">
                      No Image
                    </div>
                  )}
                </div>

                <p className="product-card__category">{category}</p>
                <h2 className="product-card__title">{product.name}</h2>
                <p className="product-card__description">
                  {product.short_description || "No description available."}
                </p>

                <div className="product-card__footer">
                  <span className="product-card__price">
                    {formatPrice(product.price)}
                  </span>
                  <button type="button" className="product-card__button">
                    View
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}