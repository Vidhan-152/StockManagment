import { useEffect, useState } from "react";
import FormField from "../components/FormField";
import SectionHeader from "../components/SectionHeader";
import { createProduct, deleteProduct, listProducts } from "../services/api";

const initialState = {
  user_id: "",
  category_id: "",
  name: "",
  sku: "",
  description: "",
  unit_price: "",
  stock: "",
  reorder_threshold: "",
  overstock_threshold: ""
};

export default function Products() {
  const [formState, setFormState] = useState(initialState);
  const [items, setItems] = useState([]);
  const [status, setStatus] = useState({ loading: false, error: "" });

  const loadProducts = async () => {
    setStatus({ loading: true, error: "" });
    try {
      const data = await listProducts();
      setItems(data);
    } catch (error) {
      setStatus({ loading: false, error: error.message });
      return;
    }
    setStatus({ loading: false, error: "" });
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormState((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatus({ loading: true, error: "" });

    const payload = {
      ...formState,
      user_id: Number(formState.user_id),
      category_id: formState.category_id ? Number(formState.category_id) : null,
      unit_price: Number(formState.unit_price),
      stock: Number(formState.stock),
      reorder_threshold: Number(formState.reorder_threshold),
      overstock_threshold: Number(formState.overstock_threshold)
    };

    try {
      await createProduct(payload);
      setFormState(initialState);
      await loadProducts();
    } catch (error) {
      setStatus({ loading: false, error: error.message });
      return;
    }
    setStatus({ loading: false, error: "" });
  };

  const handleDelete = async (id) => {
    setStatus({ loading: true, error: "" });
    try {
      await deleteProduct(id);
      await loadProducts();
    } catch (error) {
      setStatus({ loading: false, error: error.message });
      return;
    }
    setStatus({ loading: false, error: "" });
  };

  return (
    <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
      <div className="glass-panel rounded-3xl p-6 shadow-xl">
        <SectionHeader title="Products" subtitle="Create and monitor inventory items." />
        {status.error ? (
          <div className="mt-4 rounded-2xl border border-red-400/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {status.error}
          </div>
        ) : null}
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-200">
            <thead className="text-xs uppercase text-slate-400">
              <tr>
                <th className="py-2">Name</th>
                <th className="py-2">SKU</th>
                <th className="py-2">Stock</th>
                <th className="py-2">Price</th>
                <th className="py-2">Actions</th>
              </tr>
            </thead>
            <tbody className="text-slate-100">
              {items.map((item) => (
                <tr key={item.id} className="border-t border-white/5">
                  <td className="py-3">
                    <p className="font-medium text-white">{item.name}</p>
                    <p className="text-xs text-slate-400">User {item.user_id}</p>
                  </td>
                  <td className="py-3">{item.sku}</td>
                  <td className="py-3">{item.stock}</td>
                  <td className="py-3">${item.unit_price}</td>
                  <td className="py-3">
                    <button
                      className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-200 transition hover:border-red-400/60 hover:text-red-200"
                      onClick={() => handleDelete(item.id)}
                      type="button"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {items.length === 0 ? (
                <tr>
                  <td colSpan="5" className="py-6 text-center text-sm text-slate-400">
                    No products yet. Add one using the form.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>

      <form className="glass-panel rounded-3xl p-6 shadow-xl" onSubmit={handleSubmit}>
        <SectionHeader title="Add Product" subtitle="All fields are required." />
        <div className="mt-5 grid gap-4">
          <FormField
            label="User ID"
            name="user_id"
            value={formState.user_id}
            onChange={handleChange}
            placeholder="1"
          />
          <FormField
            label="Category ID (optional)"
            name="category_id"
            value={formState.category_id}
            onChange={handleChange}
            placeholder="1"
          />
          <FormField label="Name" name="name" value={formState.name} onChange={handleChange} />
          <FormField label="SKU" name="sku" value={formState.sku} onChange={handleChange} />
          <FormField
            label="Description"
            name="description"
            value={formState.description}
            onChange={handleChange}
          />
          <div className="grid gap-4 md:grid-cols-2">
            <FormField
              label="Unit Price"
              name="unit_price"
              value={formState.unit_price}
              onChange={handleChange}
            />
            <FormField
              label="Stock"
              name="stock"
              value={formState.stock}
              onChange={handleChange}
            />
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <FormField
              label="Reorder Threshold"
              name="reorder_threshold"
              value={formState.reorder_threshold}
              onChange={handleChange}
            />
            <FormField
              label="Overstock Threshold"
              name="overstock_threshold"
              value={formState.overstock_threshold}
              onChange={handleChange}
            />
          </div>
        </div>
        <button
          className="mt-6 w-full rounded-2xl bg-teal-400/80 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-teal-300"
          type="submit"
          disabled={status.loading}
        >
          {status.loading ? "Saving..." : "Create Product"}
        </button>
      </form>
    </section>
  );
}
